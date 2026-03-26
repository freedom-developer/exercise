"""
风险管理模块
在策略信号转换为订单前进行风控检查
"""
import logging
from typing import Optional, Tuple
import pandas as pd

from ..strategy.base import Signal, SignalType

logger = logging.getLogger(__name__)


class RiskManager:
    """
    风险管理器
    职责：
    1. 仓位管理（控制单标的最大仓位）
    2. 最大回撤熔断
    3. 止损控制
    4. 计算实际下单数量
    """

    def __init__(
        self,
        max_position_ratio: float = 0.2,
        max_drawdown_limit: float = 0.15,
        stop_loss_ratio: float = 0.05,
    ):
        self.max_position_ratio = max_position_ratio    # 单标的最大仓位
        self.max_drawdown_limit = max_drawdown_limit    # 最大回撤熔断
        self.stop_loss_ratio = stop_loss_ratio          # 止损比例

        self._peak_equity: float = 0.0
        self._is_halted: bool = False                   # 熔断状态
        self._entry_prices: dict = {}                   # 各标的建仓均价

    # ------------------------------------------------------------------
    # 主入口：校验信号并计算下单数量
    # ------------------------------------------------------------------

    def check_signal(
        self,
        signal: Signal,
        total_equity: float,
        cash: float,
        positions: dict,
        current_price: float,
    ) -> Tuple[bool, float, str]:
        """
        检查信号是否通过风控

        Returns:
            (passed, quantity, reason)
            passed:   是否允许下单
            quantity: 实际下单数量（股，A股需为100的整数倍）
            reason:   拒绝原因（空字符串表示通过）
        """
        if self._is_halted:
            return False, 0, "系统熔断中，停止交易"

        if signal.type == SignalType.HOLD:
            return False, 0, "HOLD信号"

        if signal.type == SignalType.BUY:
            return self._check_buy(signal, total_equity, cash, positions, current_price)
        else:
            return self._check_sell(signal, positions, current_price)

    def _check_buy(
        self,
        signal: Signal,
        total_equity: float,
        cash: float,
        positions: dict,
        price: float,
    ) -> Tuple[bool, float, str]:
        # 已有仓位则不追加（简单策略：一个标的只建一次仓）
        if signal.symbol in positions:
            return False, 0, f"{signal.symbol} 已有持仓，跳过买入"

        # 计算最大可买金额
        max_amount = total_equity * self.max_position_ratio
        available = min(cash * 0.95, max_amount)  # 留5%现金缓冲

        if available < price * 100:
            return False, 0, f"可用资金不足: {available:.0f} < {price * 100:.0f}"

        # 计算下单数量（A股：100股为最小单位）
        raw_qty = available / price
        quantity = int(raw_qty / 100) * 100

        if quantity <= 0:
            return False, 0, "计算数量为0"

        self._entry_prices[signal.symbol] = price
        return True, quantity, ""

    def _check_sell(
        self,
        signal: Signal,
        positions: dict,
        price: float,
    ) -> Tuple[bool, float, str]:
        if signal.symbol not in positions:
            return False, 0, f"{signal.symbol} 无持仓，无法卖出"

        quantity = positions[signal.symbol]

        if quantity <= 0:
            return False, 0, "持仓数量为0"

        return True, quantity, ""

    # ------------------------------------------------------------------
    # 回撤熔断
    # ------------------------------------------------------------------

    def update_equity(self, equity: float):
        """每个交易日末调用，更新权益并检查是否触发熔断"""
        if equity > self._peak_equity:
            self._peak_equity = equity

        if self._peak_equity > 0:
            drawdown = (self._peak_equity - equity) / self._peak_equity
            if drawdown >= self.max_drawdown_limit:
                if not self._is_halted:
                    logger.warning(
                        f"触发最大回撤熔断! 回撤={drawdown:.1%}, "
                        f"峰值={self._peak_equity:.0f}, 当前={equity:.0f}"
                    )
                self._is_halted = True

    # ------------------------------------------------------------------
    # 止损检查（在每根K线末调用）
    # ------------------------------------------------------------------

    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """
        检查是否触发止损

        Returns:
            True 表示需要止损卖出
        """
        entry = self._entry_prices.get(symbol)
        if entry is None:
            return False
        loss_ratio = (entry - current_price) / entry
        if loss_ratio >= self.stop_loss_ratio:
            logger.warning(
                f"止损触发: {symbol} 成本={entry:.3f} 当前={current_price:.3f} "
                f"亏损={loss_ratio:.1%}"
            )
            return True
        return False

    def on_position_closed(self, symbol: str):
        """持仓清空时清理记录"""
        self._entry_prices.pop(symbol, None)

    @property
    def is_halted(self) -> bool:
        return self._is_halted

    def reset_halt(self):
        """手动解除熔断（测试用）"""
        self._is_halted = False
