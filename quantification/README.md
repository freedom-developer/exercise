# QuantStudio - 量化交易软件

一个完整的量化交易软件，包含数据获取、策略开发、回测和风险管理功能。

## 功能特性

- 📊 **数据管理**: 支持多种数据源（CSV、数据库、API）
- 📈 **策略开发**: 提供策略模板和回测框架
- ⚙️ **回测引擎**: 完整的回测系统，支持多种指标
- 🛡️ **风险管理**: 风险控制和资金管理
- 📱 **可视化**: 数据可视化和结果展示
- 🔧 **配置管理**: 灵活的配置文件管理

## 项目结构

```
quantification/
├── README.md
├── requirements.txt
├── config/
│   └── config.yaml
├── data/
│   ├── raw/           # 原始数据
│   ├── processed/     # 处理后的数据
│   └── cache/         # 缓存数据
├── src/
│   ├── __init__.py
│   ├── data/          # 数据模块
│   ├── strategy/      # 策略模块
│   ├── backtest/      # 回测模块
│   ├── risk/          # 风险管理
│   ├── utils/         # 工具函数
│   └── visualization/ # 可视化
├── strategies/        # 策略文件
├── notebooks/         # Jupyter Notebooks
├── tests/            # 测试文件
└── main.py           # 主程序入口
```

## 安装和使用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置
编辑 `config/config.yaml` 文件，配置数据源和参数。

### 3. 运行示例
```bash
python main.py --strategy moving_average --start 2020-01-01 --end 2023-12-31
```

### 4. 开发新策略
在 `strategies/` 目录中创建新的策略文件。

## 支持的策略类型

1. **趋势跟踪策略**
   - 移动平均线策略
   - 布林带策略
   - MACD策略

2. **均值回归策略**
   - RSI策略
   - 统计套利

3. **机器学习策略**
   - 基于特征的预测模型
   - 深度学习模型

## 数据源支持

- CSV文件
- MySQL/PostgreSQL数据库
- Yahoo Finance API
- Alpha Vantage API
- 聚宽/JQData (中国A股)

## 性能指标

- 年化收益率
- 夏普比率
- 最大回撤
- 胜率
- 盈亏比
- 索提诺比率

## 许可证

MIT License