"""
策略基类
所有策略继承此类，实现 on_bar() 方法
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import pandas as pd

from ..data.feed import Bar


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    """策略信号"""
    type: SignalType
    symbol: str
    price: float                  # 建议成交价（0=市价）
    quantity: float = 0.0         # 建议数量（0=由风控/仓位管理决定）
    confidence: float = 1.0       # 信号置信度 [0,1]
    reason: str = ""              # 信号原因（调试用）
    date: Optional[pd.Timestamp] = None


class BaseStrategy(ABC):
    """
    策略基类
    子类实现 on_bar() 产生信号
    """

    def __init__(self, name: str, params: dict = None):
        self.name = name
        self.params = params or {}
        self._signals: list[Signal] = []

    @abstractmethod
    def on_bar(self, idx: int, bar: Bar, row: pd.Series) -> Optional[Signal]:
        """
        每根K线调用一次

        Args:
            idx: 当前K线在序列中的位置（用于判断预热期）
            bar: 当前K线数据
            row: 包含所有预计算指标的行数据

        Returns:
            Signal 或 None
        """
        ...

    def warmup_period(self) -> int:
        """预热期（前N根K线不产生信号）"""
        return 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.params})"
