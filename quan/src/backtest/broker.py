"""
回测模拟券商
在回测引擎中负责订单撮合、持仓管理、资金管理
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import pandas as pd

from ..execution.order import Order, OrderSide, OrderStatus

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """成交记录"""
    date: pd.Timestamp
    symbol: str
    side: str
    quantity: float
    price: float
    amount: float
    commission: float
    pnl: float = 0.0   # 平仓时的盈亏


class SimBroker:
    """
    回测模拟券商
    核心：每根K线的收盘价成交（简单模型）
    """

    def __init__(
        self,
        initial_capital: float = 1_000_000.0, # 初始资本
        commission_rate: float = 0.0003,    # 佣金率
        stamp_duty: float = 0.001,  # 印花税
        slippage: float = 0.0002,   # 滑点，指预期成交价格与实际成交价格的差异
    ):
        self.initial_capital = initial_capital  # 初始资本
        self.commission_rate = commission_rate  # 佣金率
        self.stamp_duty = stamp_duty    # 印花税
        self.slippage = slippage    # 滑点，指预期成交价格与实际成交价格的差异

        # 账户状态
        self.cash: float = initial_capital      # 现金
        self.positions: Dict[str, float] = {}           # 仓位：[symbol] = quantity
        self.cost_prices: Dict[str, float] = {}         # 仓位的成本价格: [symbol] = avg_cost
        self.trades: List[Trade] = []       # 交易记录

        # 净值序列（每日记录）
        self.equity_curve: List[dict] = []

    # ------------------------------------------------------------------
    # 执行买入/卖出
    # ------------------------------------------------------------------

    def execute_buy(self, date: pd.Timestamp, symbol: str, quantity: float, price: float) -> bool:
        fill_price = price * (1 + self.slippage)    # 实际成交价格
        amount = fill_price * quantity  # 成交金额
        commission = max(amount * self.commission_rate, 5.0) # 佣金
        total_cost = amount + commission # 成交的总成本

        if self.cash < total_cost:
            logger.debug(f"{date} 买入 {symbol} 资金不足")
            return False

        self.cash -= total_cost

        # 更新持仓均价
        old_qty = self.positions.get(symbol, 0)
        old_cost = self.cost_prices.get(symbol, 0)
        new_qty = old_qty + quantity

        # 成本价含买入佣金（摊销到每股），使卖出时 pnl 计算准确
        new_cost = (old_qty * old_cost + quantity * fill_price + commission) / new_qty
        
        self.positions[symbol] = new_qty
        self.cost_prices[symbol] = new_cost

        self.trades.append(Trade(
            date=date, symbol=symbol, side="buy",
            quantity=quantity, price=fill_price,
            amount=total_cost, commission=commission,
        ))
        logger.debug(f"{date} 买入 {symbol} {quantity}股 @ {fill_price:.3f}, 现金={self.cash:.0f}")
        return True

    def execute_sell(self, date: pd.Timestamp, symbol: str, quantity: float, price: float) -> bool:
        held = self.positions.get(symbol, 0)
        if held < quantity:
            logger.debug(f"{date} 卖出 {symbol} 持仓不足")
            return False

        fill_price = price * (1 - self.slippage)
        amount = fill_price * quantity
        commission = max(amount * self.commission_rate, 5.0)
        tax = amount * self.stamp_duty
        net_amount = amount - commission - tax

        # 计算盈亏：cost 已含买入佣金（摊销），此处再减去卖出佣金和印花税
        cost = self.cost_prices.get(symbol, fill_price)
        pnl = (fill_price - cost) * quantity - commission - tax

        self.cash += net_amount
        new_qty = held - quantity
        if new_qty <= 0:
            self.positions.pop(symbol, None)
            self.cost_prices.pop(symbol, None)
        else:
            self.positions[symbol] = new_qty

        self.trades.append(Trade(
            date=date, symbol=symbol, side="sell",
            quantity=quantity, price=fill_price,
            amount=net_amount, commission=commission + tax, pnl=pnl,
        ))
        logger.debug(f"{date} 卖出 {symbol} {quantity}股 @ {fill_price:.3f}, pnl={pnl:.0f}, 现金={self.cash:.0f}")
        return True

    # ------------------------------------------------------------------
    # 净值快照
    # ------------------------------------------------------------------

    def snapshot(self, date: pd.Timestamp, prices: Dict[str, float]):
        """记录当日净值"""
        # 股票市值 = 股票市场值
        mv = sum(self.positions.get(s, 0) * p for s, p in prices.items())
        equity = self.cash + mv # 净值 = 股票市值 + 现金
        self.equity_curve.append({
            "date": date,
            "cash": self.cash,
            "market_value": mv,
            "equity": equity,   
            "return": (equity - self.initial_capital) / self.initial_capital, # 回报率
        })

    def get_equity_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.equity_curve)
        if df.empty:
            return df
        df = df.set_index("date")
        df["daily_return"] = df["equity"].pct_change() # 每日回报 = 相邻现行的百分比变化
        return df

    @property
    def total_equity(self) -> float:
        return self.cash  # 无实时价格时用现金近似

    def position_value(self, symbol: str, price: float) -> float:
        qty = self.positions.get(symbol, 0)
        return qty * price
