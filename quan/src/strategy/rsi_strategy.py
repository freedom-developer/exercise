"""
RSI 超买超卖策略
RSI < 超卖线 -> 买入
RSI > 超买线 -> 卖出
"""
from typing import Optional
import pandas as pd

from .base import BaseStrategy, Signal, SignalType
from ..data.feed import Bar


class RSIStrategy(BaseStrategy):
    """
    RSI 策略

    Params:
        period:     RSI 周期，默认 14
        oversold:   超卖阈值，默认 30（低于此值买入）
        overbought: 超买阈值，默认 70（高于此值卖出）
    """

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__(
            name=f"RSI({period})",
            params={"period": period, "oversold": oversold, "overbought": overbought},
        )
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self._prev_rsi: Optional[float] = None
        self._in_long = False

    def warmup_period(self) -> int:
        return self.period * 2

    def on_bar(self, idx: int, bar: Bar, row: pd.Series) -> Optional[Signal]:
        rsi = row.get("rsi14")
        if pd.isna(rsi):
            return None

        signal = None

        # 从超卖区反弹 -> 买入
        if not self._in_long and self._prev_rsi is not None:
            if self._prev_rsi < self.oversold and rsi >= self.oversold:
                signal = Signal(
                    type=SignalType.BUY,
                    symbol=bar.symbol,
                    price=bar.close,
                    confidence=min(1.0, (self.oversold - self._prev_rsi) / self.oversold),
                    reason=f"RSI超卖反弹: {self._prev_rsi:.1f} -> {rsi:.1f}",
                    date=bar.date,
                )
                self._in_long = True

        # 从超买区回落 -> 卖出
        elif self._in_long and self._prev_rsi is not None:
            if self._prev_rsi > self.overbought and rsi <= self.overbought:
                signal = Signal(
                    type=SignalType.SELL,
                    symbol=bar.symbol,
                    price=bar.close,
                    confidence=min(1.0, (self._prev_rsi - self.overbought) / (100 - self.overbought)),
                    reason=f"RSI超买回落: {self._prev_rsi:.1f} -> {rsi:.1f}",
                    date=bar.date,
                )
                self._in_long = False

        self._prev_rsi = rsi
        return signal
