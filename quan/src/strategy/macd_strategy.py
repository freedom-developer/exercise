"""
MACD 策略
DIF 上穿 DEA (MACD柱由负转正) -> 买入
DIF 下穿 DEA (MACD柱由正转负) -> 卖出
"""
from typing import Optional
import pandas as pd

from .base import BaseStrategy, Signal, SignalType
from ..data.feed import Bar


class MACDStrategy(BaseStrategy):
    """
    MACD 金叉死叉策略

    Params:
        fast:   快线EMA周期，默认 12
        slow:   慢线EMA周期，默认 26
        signal: 信号线EMA周期，默认 9
    """

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__(
            name=f"MACD({fast},{slow},{signal})",
            params={"fast": fast, "slow": slow, "signal": signal},
        )
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self._prev_dif: Optional[float] = None
        self._prev_dea: Optional[float] = None

    def warmup_period(self) -> int:
        return self.slow + self.signal + 5

    def on_bar(self, idx: int, bar: Bar, row: pd.Series) -> Optional[Signal]:
        dif = row.get("macd_dif")
        dea = row.get("macd_dea")
        hist = row.get("macd_hist")

        if pd.isna(dif) or pd.isna(dea):
            self._prev_dif = dif
            self._prev_dea = dea
            return None

        signal = None

        if self._prev_dif is not None and self._prev_dea is not None:
            prev_cross = self._prev_dif - self._prev_dea
            curr_cross = dif - dea

            # 金叉
            if prev_cross <= 0 and curr_cross > 0:
                signal = Signal(
                    type=SignalType.BUY,
                    symbol=bar.symbol,
                    price=bar.close,
                    reason=f"MACD金叉: DIF={dif:.4f} DEA={dea:.4f} HIST={hist:.4f}",
                    date=bar.date,
                )
            # 死叉
            elif prev_cross >= 0 and curr_cross < 0:
                signal = Signal(
                    type=SignalType.SELL,
                    symbol=bar.symbol,
                    price=bar.close,
                    reason=f"MACD死叉: DIF={dif:.4f} DEA={dea:.4f} HIST={hist:.4f}",
                    date=bar.date,
                )

        self._prev_dif = dif
        self._prev_dea = dea
        return signal
