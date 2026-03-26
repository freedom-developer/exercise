"""
回测引擎（事件驱动）
流程：
  for each bar:
    1. DataFeed 产生 Bar
    2. Strategy.on_bar() 产生 Signal
    3. RiskManager 校验信号，计算数量
    4. SimBroker 执行成交
    5. 记录净值快照
"""
import logging
from typing import Optional
import pandas as pd

from ..data.feed import DataFeed
from ..strategy.base import BaseStrategy, SignalType
from ..risk.manager import RiskManager
from .broker import SimBroker
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    事件驱动回测引擎
    """

    def __init__(
        self,
        feed: DataFeed,
        strategy: BaseStrategy,
        initial_capital: float = 1_000_000.0,
        commission_rate: float = 0.0003,
        stamp_duty: float = 0.001,
        slippage: float = 0.0002,
        max_position_ratio: float = 0.2,
        max_drawdown_limit: float = 0.15,
        stop_loss_ratio: float = 0.05,
    ):
        self.feed = feed
        self.strategy = strategy

        self.broker = SimBroker(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            stamp_duty=stamp_duty,
            slippage=slippage,
        )
        self.risk = RiskManager(
            max_position_ratio=max_position_ratio,
            max_drawdown_limit=max_drawdown_limit,
            stop_loss_ratio=stop_loss_ratio,
        )

        self._warmup = strategy.warmup_period()

    # ------------------------------------------------------------------
    # 运行回测
    # ------------------------------------------------------------------

    def run(self) -> PerformanceMetrics:
        logger.info(
            f"开始回测: 策略={self.strategy.name}, "
            f"标的={self.feed.symbol}, "
            f"初始资金={self.broker.initial_capital:,.0f}"
        )

        for idx, bar, row in self.feed:
            if idx < self._warmup:
                # 预热期仍记录净值
                self.broker.snapshot(bar.date, {bar.symbol: bar.close})
                continue

            # 1. 止损检查
            if self.risk.check_stop_loss(bar.symbol, bar.close):
                qty = self.broker.positions.get(bar.symbol, 0)
                if qty > 0:
                    self.broker.execute_sell(bar.date, bar.symbol, qty, bar.close)
                    self.risk.on_position_closed(bar.symbol)

            # 2. 策略信号
            signal = self.strategy.on_bar(idx, bar, row)

            # 3. 风控 + 执行
            if signal is not None and signal.type != SignalType.HOLD:
                equity = self._current_equity(bar.close)
                passed, quantity, reason = self.risk.check_signal(
                    signal=signal,
                    total_equity=equity,
                    cash=self.broker.cash,
                    positions=self.broker.positions,
                    current_price=bar.close,
                )

                if passed and quantity > 0:
                    if signal.type == SignalType.BUY:
                        self.broker.execute_buy(bar.date, bar.symbol, quantity, bar.close)
                    else:
                        self.broker.execute_sell(bar.date, bar.symbol, quantity, bar.close)
                        self.risk.on_position_closed(bar.symbol)
                elif not passed:
                    logger.debug(f"{bar.date} 信号被风控拒绝: {reason}")

            # 4. 净值快照
            self.broker.snapshot(bar.date, {bar.symbol: bar.close})

            # 5. 回撤熔断更新
            self.risk.update_equity(self._current_equity(bar.close))

        equity_df = self.broker.get_equity_df()
        metrics = PerformanceMetrics(equity_df)
        metrics.print_report()

        logger.info(f"回测完成，共 {len(self.broker.trades)} 笔成交")
        return metrics

    def _current_equity(self, price: float) -> float:
        mv = self.broker.positions.get(self.feed.symbol, 0) * price
        return self.broker.cash + mv

    # ------------------------------------------------------------------
    # 结果访问
    # ------------------------------------------------------------------

    @property
    def equity_df(self) -> pd.DataFrame:
        return self.broker.get_equity_df()

    @property
    def trades(self) -> list:
        return self.broker.trades

    def trades_df(self) -> pd.DataFrame:
        if not self.broker.trades:
            return pd.DataFrame()
        rows = []
        for t in self.broker.trades:
            rows.append({
                "date": t.date,
                "symbol": t.symbol,
                "side": t.side,
                "quantity": t.quantity,
                "price": t.price,
                "amount": t.amount,
                "commission": t.commission,
                "pnl": t.pnl,
            })
        return pd.DataFrame(rows).set_index("date")
