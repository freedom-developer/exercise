"""
模拟实盘券商
用于策略实盘模拟（非回测），维护账户状态
"""
import logging
from typing import Dict, Optional
import pandas as pd

from .order import Order, OrderType, OrderSide, OrderStatus

logger = logging.getLogger(__name__)


class Position:
    """持仓"""
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity: float = 0.0       # 持仓数量
        self.cost_price: float = 0.0     # 平均成本价
        self.market_value: float = 0.0   # 市值

    def update_market_value(self, price: float):
        self.market_value = self.quantity * price

    @property
    def cost_amount(self) -> float:
        return self.quantity * self.cost_price

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_amount

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_amount == 0:
            return 0.0
        return self.unrealized_pnl / self.cost_amount


class PaperBroker:
    """
    模拟实盘账户
    支持买入/卖出，计算手续费/印花税，维护持仓和现金
    """

    def __init__(
        self,
        initial_capital: float = 1_000_000.0,
        commission_rate: float = 0.0003,
        stamp_duty: float = 0.001,
        slippage: float = 0.0002,
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.stamp_duty = stamp_duty      # 印花税（卖出收取）
        self.slippage = slippage

        self.cash: float = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: list[Order] = []

    # ------------------------------------------------------------------
    # 下单接口
    # ------------------------------------------------------------------

    def buy(self, symbol: str, quantity: float, price: float = 0.0) -> Order:
        order = Order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET if price == 0 else OrderType.LIMIT,
            quantity=quantity,
            price=price,
            created_at=pd.Timestamp.now(),
        )
        self.orders.append(order)
        self._fill_order(order, price or price)
        return order

    def sell(self, symbol: str, quantity: float, price: float = 0.0) -> Order:
        order = Order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET if price == 0 else OrderType.LIMIT,
            quantity=quantity,
            price=price,
            created_at=pd.Timestamp.now(),
        )
        self.orders.append(order)
        self._fill_order(order, price or price)
        return order

    # ------------------------------------------------------------------
    # 内部撮合
    # ------------------------------------------------------------------

    def _fill_order(self, order: Order, market_price: float):
        if market_price <= 0:
            order.status = OrderStatus.REJECTED
            order.reject_reason = "无效价格"
            return

        # 滑点
        if order.side == OrderSide.BUY:
            fill_price = market_price * (1 + self.slippage)
        else:
            fill_price = market_price * (1 - self.slippage)

        amount = fill_price * order.quantity

        # 手续费
        commission = amount * self.commission_rate
        commission = max(commission, 5.0)  # 最低5元

        # 印花税（仅卖出）
        tax = amount * self.stamp_duty if order.side == OrderSide.SELL else 0.0

        total_cost = amount + commission + tax

        if order.side == OrderSide.BUY:
            if self.cash < total_cost:
                order.status = OrderStatus.REJECTED
                order.reject_reason = f"资金不足: 需要 {total_cost:.2f}, 可用 {self.cash:.2f}"
                logger.warning(order.reject_reason)
                return
            self.cash -= total_cost
            self._add_position(order.symbol, order.quantity, fill_price)

        else:  # SELL
            pos = self.positions.get(order.symbol)
            if pos is None or pos.quantity < order.quantity:
                order.status = OrderStatus.REJECTED
                order.reject_reason = "持仓不足"
                logger.warning(order.reject_reason)
                return
            self.cash += amount - commission - tax
            self._reduce_position(order.symbol, order.quantity)

        order.status = OrderStatus.FILLED
        order.filled_qty = order.quantity
        order.filled_price = fill_price
        order.filled_amount = total_cost
        order.commission = commission + tax
        order.filled_at = pd.Timestamp.now()

        logger.info(
            f"成交: {order.side.value} {order.symbol} {order.quantity}股 "
            f"@ {fill_price:.3f}, 手续费={commission + tax:.2f}, 现金余额={self.cash:.2f}"
        )

    def _add_position(self, symbol: str, qty: float, price: float):
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)
        pos = self.positions[symbol]
        total_cost = pos.quantity * pos.cost_price + qty * price
        pos.quantity += qty
        pos.cost_price = total_cost / pos.quantity

    def _reduce_position(self, symbol: str, qty: float):
        pos = self.positions[symbol]
        pos.quantity -= qty
        if pos.quantity <= 0:
            del self.positions[symbol]

    # ------------------------------------------------------------------
    # 账户信息
    # ------------------------------------------------------------------

    def update_market_prices(self, prices: Dict[str, float]):
        """更新持仓市值"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].update_market_value(price)

    @property
    def total_market_value(self) -> float:
        return sum(p.market_value for p in self.positions.values())

    @property
    def total_equity(self) -> float:
        return self.cash + self.total_market_value

    @property
    def total_pnl(self) -> float:
        return self.total_equity - self.initial_capital

    def summary(self) -> dict:
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "market_value": self.total_market_value,
            "total_equity": self.total_equity,
            "total_pnl": self.total_pnl,
            "total_pnl_pct": self.total_pnl / self.initial_capital,
            "positions": {
                s: {"qty": p.quantity, "cost": p.cost_price, "pnl": p.unrealized_pnl}
                for s, p in self.positions.items()
            },
        }
