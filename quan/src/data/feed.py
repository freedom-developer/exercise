"""
数据馈送模块
将历史数据按时间顺序逐条喂给策略（事件驱动回测核心）
同时支持实时行情模拟
"""
import logging
import pandas as pd
import numpy as np
from typing import Optional, Iterator, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Bar:
    """单根K线数据"""
    symbol: str
    date: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float = 0.0

    @property
    def typical_price(self) -> float:
        return (self.high + self.low + self.close) / 3


class DataFeed:
    """
    历史数据馈送器
    包含指标计算（MA/RSI/MACD/布林带），供策略使用
    """

    def __init__(self, df: pd.DataFrame, symbol: str):
        """
        Args:
            df:     标准化 DataFrame (index=DatetimeIndex, cols=[open,high,low,close,volume])
            symbol: 标的代码
        """
        self.symbol = symbol
        self.df = df.copy()
        self._cursor = 0
        self._precompute_indicators()

    def _precompute_indicators(self):
        """预计算常用技术指标，提升回测性能"""
        c = self.df["close"]    # 收盘列
        v = self.df["volume"]   # 成交量列

        # 移动平均
        for n in [5, 10, 20, 30, 60]:
            self.df[f"ma{n}"] = c.rolling(n).mean()

        # EMA
        for n in [12, 26]:
            self.df[f"ema{n}"] = c.ewm(span=n, adjust=False).mean()

        # MACD
        self.df["macd_dif"] = self.df["ema12"] - self.df["ema26"]
        self.df["macd_dea"] = self.df["macd_dif"].ewm(span=9, adjust=False).mean()
        self.df["macd_hist"] = (self.df["macd_dif"] - self.df["macd_dea"]) * 2

        # RSI(14)
        self.df["rsi14"] = self._calc_rsi(c, 14)

        # 布林带(20, 2)
        self.df["boll_mid"] = c.rolling(20).mean()
        std20 = c.rolling(20).std()
        self.df["boll_upper"] = self.df["boll_mid"] + 2 * std20
        self.df["boll_lower"] = self.df["boll_mid"] - 2 * std20

        # ATR(14)
        self.df["atr14"] = self._calc_atr(14)

        # 成交量MA
        self.df["vol_ma5"] = v.rolling(5).mean()
        self.df["vol_ma20"] = v.rolling(20).mean()

    @staticmethod
    def _calc_rsi(close: pd.Series, period: int) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return 100 - 100 / (1 + rs)

    def _calc_atr(self, period: int) -> pd.Series:
        h = self.df["high"]
        l = self.df["low"]
        c = self.df["close"].shift(1)
        tr = pd.concat([h - l, (h - c).abs(), (l - c).abs()], axis=1).max(axis=1)
        return tr.ewm(com=period - 1, adjust=False).mean()

    # ------------------------------------------------------------------
    # 迭代接口（供回测引擎使用）
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.df)

    def __iter__(self) -> Iterator[Tuple[int, Bar, pd.Series]]:
        """
        逐行迭代，返回 (index, bar, row)
        row 包含当前时刻所有指标值（策略可直接读取）
        """
        for i, (date, row) in enumerate(self.df.iterrows()):
            bar = Bar(
                symbol=self.symbol,
                date=date,
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
                amount=row.get("amount", 0.0),
            )
            yield i, bar, row

    def get_slice(self, end_idx: int, lookback: int = 60) -> pd.DataFrame:
        """获取到 end_idx 为止的 lookback 根K线"""
        start = max(0, end_idx - lookback)
        return self.df.iloc[start : end_idx + 1]

    @property
    def closes(self) -> pd.Series:
        return self.df["close"]

    @property
    def dates(self) -> pd.DatetimeIndex:
        return self.df.index
