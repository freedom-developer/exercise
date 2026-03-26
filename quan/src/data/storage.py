"""
数据存储模块
使用 Parquet 格式本地缓存，读写高效
"""
import os
import logging
import pandas as pd
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DataStorage:
    """
    本地数据缓存
    目录结构:
        cache_dir/
            stocks/
                000001_qfq_2020-01-01_2024-01-01.parquet
            index/
                000300_2020-01-01_2024-01-01.parquet
    """

    def __init__(self, cache_dir: str = "./data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "stocks").mkdir(exist_ok=True)
        (self.cache_dir / "index").mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # 缓存 key
    # ------------------------------------------------------------------

    def _stock_path(self, symbol: str, start: str, end: str, adjust: str) -> Path:
        fname = f"{symbol}_{adjust}_{start}_{end}.parquet"
        return self.cache_dir / "stocks" / fname

    def _index_path(self, symbol: str, start: str, end: str) -> Path:
        fname = f"{symbol}_{start}_{end}.parquet"
        return self.cache_dir / "index" / fname

    # ------------------------------------------------------------------
    # 保存
    # ------------------------------------------------------------------

    def save_stock(self, df: pd.DataFrame, symbol: str, start: str, end: str, adjust: str):
        path = self._stock_path(symbol, start, end, adjust)
        df.to_parquet(path)
        logger.info(f"已缓存 {symbol} -> {path}")

    def save_index(self, df: pd.DataFrame, symbol: str, start: str, end: str):
        path = self._index_path(symbol, start, end)
        df.to_parquet(path)
        logger.info(f"已缓存指数 {symbol} -> {path}")

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------

    def load_stock(
        self, symbol: str, start: str, end: str, adjust: str
    ) -> Optional[pd.DataFrame]:
        path = self._stock_path(symbol, start, end, adjust)
        if path.exists():
            logger.info(f"命中缓存 {symbol}")
            return pd.read_parquet(path)
        return None

    def load_index(self, symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
        path = self._index_path(symbol, start, end)
        if path.exists():
            logger.info(f"命中缓存指数 {symbol}")
            return pd.read_parquet(path)
        return None

    def list_cached(self) -> list:
        """列出所有已缓存文件"""
        files = []
        for f in self.cache_dir.rglob("*.parquet"):
            files.append(str(f.relative_to(self.cache_dir)))
        return sorted(files)
