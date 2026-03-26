"""
订单模型
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid
import pandas as pd


class OrderType(Enum):
    MARKET = "market"   # 市价单
    LIMIT = "limit"     # 限价单


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"       # 待提交
    SUBMITTED = "submitted"   # 已提交
    FILLED = "filled"         # 已成交
    PARTIAL = "partial"       # 部分成交
    CANCELLED = "cancelled"   # 已撤销
    REJECTED = "rejected"     # 已拒绝


@dataclass
class Order:
    """订单"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float                       # 委托数量（股）
    price: float = 0.0                    # 委托价（市价单填0）

    # 以下字段由系统填充
    order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: OrderStatus = OrderStatus.PENDING
    filled_qty: float = 0.0
    filled_price: float = 0.0
    filled_amount: float = 0.0            # 成交金额（含手续费）
    commission: float = 0.0
    created_at: Optional[pd.Timestamp] = None
    filled_at: Optional[pd.Timestamp] = None
    reject_reason: str = ""

    @property
    def is_done(self) -> bool:
        return self.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED)

    @property
    def remaining_qty(self) -> float:
        return self.quantity - self.filled_qty

    def __repr__(self) -> str:
        return (
            f"Order({self.order_id} {self.side.value} {self.symbol} "
            f"{self.quantity}@{self.price} [{self.status.value}])"
        )
