"""
数据获取模块
支持 akshare (免费) 和 tushare (需Token)
"""
import logging
import pandas as pd
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    行情数据获取器
    统一封装多数据源，返回标准化 DataFrame：
    columns: [open, high, low, close, volume, amount]
    index: DatetimeIndex
    """

    def __init__(self, provider: str = "akshare", token: str = ""):
        self.provider = provider
        self.token = token
        self._init_provider()

    def _init_provider(self):
        if self.provider == "tushare":
            try:
                import tushare as ts
                ts.set_token(self.token)
                self._ts_pro = ts.pro_api()
                logger.info("tushare 初始化成功")
            except ImportError:
                raise ImportError("请安装 tushare: pip install tushare")
        elif self.provider == "akshare":
            try:
                import akshare  # noqa: F401
                logger.info("akshare 初始化成功")
            except ImportError:
                raise ImportError("请安装 akshare: pip install akshare")

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def fetch_stock_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        """
        获取A股日线数据

        Args:
            symbol:     股票代码，如 "000001"（平安银行）
            start_date: 开始日期 "YYYY-MM-DD"
            end_date:   结束日期 "YYYY-MM-DD"
            adjust:     复权方式 qfq/hfq/none

        Returns:
            标准化 DataFrame
        """
        if self.provider == "akshare":
            return self._fetch_akshare_stock_daily(symbol, start_date, end_date, adjust)
        elif self.provider == "tushare":
            return self._fetch_tushare_stock_daily(symbol, start_date, end_date, adjust)
        else:
            raise ValueError(f"不支持的数据源: {self.provider}")

    def fetch_index_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """获取指数日线数据，如沪深300(000300)、上证指数(000001)"""
        if self.provider == "akshare":
            return self._fetch_akshare_index_daily(symbol, start_date, end_date)
        else:
            raise NotImplementedError(f"{self.provider} 暂不支持指数数据")

    # ------------------------------------------------------------------
    # akshare 实现
    # ------------------------------------------------------------------

    def _fetch_akshare_stock_daily(
        self, symbol: str, start_date: str, end_date: str, adjust: str
    ) -> pd.DataFrame:
        import akshare as ak

        adjust_map = {"qfq": "qfq", "hfq": "hfq", "none": ""}
        ak_adjust = adjust_map.get(adjust, "qfq")

        # akshare 日期格式 YYYYMMDD
        start = start_date.replace("-", "")
        end = end_date.replace("-", "")

        logger.info(f"akshare 拉取 {symbol} {start_date}~{end_date} ({adjust})")
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start,
            end_date=end,
            adjust=ak_adjust,
        )
        return self._normalize_akshare_stock(df)

    def _fetch_akshare_index_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        import akshare as ak

        start = start_date.replace("-", "")
        end = end_date.replace("-", "")

        logger.info(f"akshare 拉取指数 {symbol} {start_date}~{end_date}")
        df = ak.index_zh_a_hist(symbol=symbol, period="daily", start_date=start, end_date=end)
        return self._normalize_akshare_stock(df)

    @staticmethod
    def _normalize_akshare_stock(df: pd.DataFrame) -> pd.DataFrame:
        """将 akshare 原始列名统一为标准列名"""
        col_map = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "pct_change",
        }
        df = df.rename(columns=col_map)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()

        # 保留标准列，忽略多余列
        keep = [c for c in ["open", "high", "low", "close", "volume", "amount"] if c in df.columns]
        return df[keep].astype(float)

    # ------------------------------------------------------------------
    # tushare 实现
    # ------------------------------------------------------------------

    def _fetch_tushare_stock_daily(
        self, symbol: str, start_date: str, end_date: str, adjust: str
    ) -> pd.DataFrame:
        # tushare 代码格式: 000001.SZ / 600000.SH
        ts_code = self._to_ts_code(symbol)
        start = start_date.replace("-", "")
        end = end_date.replace("-", "")

        logger.info(f"tushare 拉取 {ts_code} {start_date}~{end_date}")
        df = self._ts_pro.daily(ts_code=ts_code, start_date=start, end_date=end)
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df = df.set_index("trade_date").sort_index()
        df = df.rename(columns={"vol": "volume", "amount": "amount"})
        keep = [c for c in ["open", "high", "low", "close", "volume", "amount"] if c in df.columns]
        return df[keep].astype(float)

    @staticmethod
    def _to_ts_code(symbol: str) -> str:
        """将6位股票代码转为 tushare 格式"""
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        return f"{symbol}.SZ"
