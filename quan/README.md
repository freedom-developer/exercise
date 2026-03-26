# 量化交易系统 (Quant Trading System)

基于 **Python + C++** 混合架构的完整量化交易软件，从数据获取到回测到可视化一体化。

---

## 项目架构

```
quan/
├── main.py                     # 主入口，命令行运行回测
├── requirements.txt
├── config/
│   └── config.yaml             # 全局配置
│
├── src/
│   ├── data/
│   │   ├── fetcher.py          # 数据获取（akshare/tushare）
│   │   ├── storage.py          # 本地 Parquet 缓存
│   │   └── feed.py             # 数据馈送 + 预计算指标
│   │
│   ├── strategy/
│   │   ├── base.py             # 策略基类 + Signal/SignalType
│   │   ├── ma_strategy.py      # 双均线金叉死叉
│   │   ├── rsi_strategy.py     # RSI 超买超卖
│   │   └── macd_strategy.py    # MACD 金叉死叉
│   │
│   ├── backtest/
│   │   ├── engine.py           # 事件驱动回测引擎
│   │   ├── broker.py           # 模拟券商（撮合/手续费/印花税）
│   │   └── metrics.py          # 绩效指标（夏普/最大回撤/Calmar等）
│   │
│   ├── risk/
│   │   └── manager.py          # 风险管理（仓位/止损/熔断）
│   │
│   ├── execution/
│   │   ├── order.py            # 订单数据模型
│   │   └── paper_broker.py     # 模拟实盘账户
│   │
│   └── visualization/
│       └── dashboard.py        # 净值曲线/回撤/K线可视化
│
└── cpp/                        # C++ 高性能指标计算模块
    ├── CMakeLists.txt
    ├── build.sh                # 一键编译脚本
    ├── include/
    │   └── indicators.h        # SMA/EMA/MACD/RSI/ATR/Boll/KDJ
    └── src/
        ├── indicators.cpp      # 指标实现
        └── bindings.cpp        # pybind11 Python 绑定
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行回测

```bash
# 默认：平安银行 双均线策略 2020-2024
python main.py

# 指定参数
python main.py --symbol 600036 --strategy rsi --start 2021-01-01 --end 2024-01-01

# 显示图表
python main.py --plot

# 保存图表
python main.py --save-plot result.png
```

**支持的策略**：

| 参数 | 策略 |
|------|------|
| `ma_cross` | 双均线金叉死叉 (默认 5/20) |
| `rsi` | RSI 超买超卖 (14, 30/70) |
| `macd` | MACD 金叉死叉 (12,26,9) |

### 3. 编译 C++ 指标模块（可选，提升性能）

```bash
cd cpp
bash build.sh
```

编译后可在 Python 中使用：
```python
import quan_indicators
close = [10.0, 10.5, 11.0, ...]
result = quan_indicators.macd(close)
print(result["dif"], result["dea"], result["hist"])
```

---

## 自定义策略

继承 `BaseStrategy`，实现 `on_bar()` 方法：

```python
from src.strategy.base import BaseStrategy, Signal, SignalType
from src.data.feed import Bar
import pandas as pd

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="MyStrategy")

    def warmup_period(self) -> int:
        return 30  # 前30根K线不产生信号

    def on_bar(self, idx, bar: Bar, row: pd.Series):
        # row 包含所有预计算指标：ma5/ma20/rsi14/macd_dif/...
        if row["ma5"] > row["ma20"]:
            return Signal(
                type=SignalType.BUY,
                symbol=bar.symbol,
                price=bar.close,
                reason="自定义条件",
                date=bar.date,
            )
        return None
```

---

## 绩效指标说明

| 指标 | 说明 |
|------|------|
| 年化收益率 | 复利年化 |
| Sharpe 比率 | 超额收益/波动率，>1 较好 |
| Sortino 比率 | 只考虑下行波动，更严格 |
| Calmar 比率 | 年化收益/最大回撤 |
| 最大回撤 | 净值从峰值下跌的最大幅度 |

---

## 风控参数

在 `config/config.yaml` 中配置：

```yaml
risk:
  max_position_ratio: 0.2   # 单标的最大仓位 20%
  max_drawdown_limit: 0.15  # 回撤超过 15% 触发熔断
  stop_loss_ratio: 0.05     # 单笔止损 5%
```

---

## 数据源

默认使用 **akshare**（完全免费，无需注册）。

切换为 tushare（需要 token）：
```python
fetcher = DataFetcher(provider="tushare", token="YOUR_TOKEN")
```
