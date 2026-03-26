"""
双均线金叉死叉策略
快线上穿慢线 -> 买入
快线下穿慢线 -> 卖出
"""
from typing import Optional
import pandas as pd

from .base import BaseStrategy, Signal, SignalType
from ..data.feed import Bar


class MACrossStrategy(BaseStrategy):
    """
    双均线交叉策略

    Params:
        fast:  快线周期，默认 5
        slow:  慢线周期，默认 20
    """

    def __init__(self, fast: int = 5, slow: int = 20):
        super().__init__(
            name=f"MA({fast},{slow})",
            params={"fast": fast, "slow": slow},
        )
        self.fast = fast
        self.slow = slow
        self._prev_fast: Optional[float] = None
        self._prev_slow: Optional[float] = None

    def warmup_period(self) -> int:
        return self.slow + 1

    def on_bar(self, idx: int, bar: Bar, row: pd.Series) -> Optional[Signal]:
        fast_key = f"ma{self.fast}"
        slow_key = f"ma{self.slow}"

        curr_fast = row.get(fast_key)
        curr_slow = row.get(slow_key)

        if pd.isna(curr_fast) or pd.isna(curr_slow):
            self._prev_fast = curr_fast
            self._prev_slow = curr_slow
            return None

        signal = None

        if self._prev_fast is not None and self._prev_slow is not None:
            # 金叉：快线从下方穿过慢线
            if self._prev_fast <= self._prev_slow and curr_fast > curr_slow:
                signal = Signal(
                    type=SignalType.BUY,
                    symbol=bar.symbol,
                    price=bar.close,
                    reason=f"MA金叉: MA{self.fast}={curr_fast:.2f} 上穿 MA{self.slow}={curr_slow:.2f}",
                    date=bar.date,
                )
            # 死叉：快线从上方穿过慢线
            elif self._prev_fast >= self._prev_slow and curr_fast < curr_slow:
                signal = Signal(
                    type=SignalType.SELL,
                    symbol=bar.symbol,
                    price=bar.close,
                    reason=f"MA死叉: MA{self.fast}={curr_fast:.2f} 下穿 MA{self.slow}={curr_slow:.2f}",
                    date=bar.date,
                )

        self._prev_fast = curr_fast
        self._prev_slow = curr_slow
        return signal
