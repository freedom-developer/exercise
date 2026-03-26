"""
量化交易系统主入口

用法示例:
    python main.py                          # 默认运行双均线策略回测
    python main.py --strategy rsi           # RSI策略
    python main.py --strategy macd          # MACD策略
    python main.py --symbol 600036          # 招商银行
    python main.py --start 2020-01-01 --end 2024-01-01
    python main.py --capital 500000         # 50万初始资金
    python main.py --plot                   # 显示图表
"""
import argparse
import logging
import sys
import os

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from src.data.fetcher import DataFetcher
from src.data.storage import DataStorage
from src.data.feed import DataFeed
from src.strategy.ma_strategy import MACrossStrategy
from src.strategy.rsi_strategy import RSIStrategy
from src.strategy.macd_strategy import MACDStrategy
from src.backtest.engine import BacktestEngine
from src.visualization.dashboard import Dashboard


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def build_strategy(name: str, params: dict):
    strategies = {
        "ma_cross": lambda: MACrossStrategy(
            fast=params.get("fast", 5),
            slow=params.get("slow", 20),
        ),
        "rsi": lambda: RSIStrategy(
            period=params.get("period", 14),
            oversold=params.get("oversold", 30),
            overbought=params.get("overbought", 70),
        ),
        "macd": lambda: MACDStrategy(
            fast=params.get("fast", 12),
            slow=params.get("slow", 26),
            signal=params.get("signal", 9),
        ),
    }
    if name not in strategies:
        raise ValueError(f"未知策略: {name}，可选: {list(strategies.keys())}")
    return strategies[name]()


def main():
    parser = argparse.ArgumentParser(description="量化交易回测系统")
    parser.add_argument("--symbol",   default="000001",    help="股票代码 (默认: 000001 平安银行)")
    parser.add_argument("--start",    default="2020-01-01", help="开始日期")
    parser.add_argument("--end",      default="2024-12-31", help="结束日期")
    parser.add_argument("--strategy", default="ma_cross",   help="策略: ma_cross | rsi | macd")
    parser.add_argument("--capital",  type=float, default=1_000_000, help="初始资金")
    parser.add_argument("--adjust",   default="qfq",        help="复权方式: qfq | hfq | none")
    parser.add_argument("--plot",     action="store_true",  help="显示图表")
    parser.add_argument("--save-plot",default="",           help="保存图表路径")
    parser.add_argument("--log",      default="INFO",       help="日志级别")
    args = parser.parse_args()

    setup_logging(args.log)
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 55)
    print("          量化交易回测系统")
    print("=" * 55)
    print(f"  标的:     {args.symbol}")
    print(f"  区间:     {args.start} ~ {args.end}")
    print(f"  策略:     {args.strategy}")
    print(f"  初始资金: {args.capital:,.0f} 元")
    print("=" * 55)

    # 1. 加载数据
    storage = DataStorage(cache_dir="./data_cache")
    df = storage.load_stock(args.symbol, args.start, args.end, args.adjust)

    if df is None:
        logger.info("本地缓存未命中，从网络拉取数据...")
        fetcher = DataFetcher(provider="akshare")
        df = fetcher.fetch_stock_daily(args.symbol, args.start, args.end, args.adjust)
        storage.save_stock(df, args.symbol, args.start, args.end, args.adjust)
    
    print(f"\n  数据加载完成: {len(df)} 根K线  {df.index[0].date()} ~ {df.index[-1].date()}")

    # 2. 构建数据馈送
    feed = DataFeed(df, symbol=args.symbol)

    # 3. 构建策略
    strategy = build_strategy(args.strategy, {})
    print(f"  策略初始化: {strategy}")

    # 4. 运行回测
    engine = BacktestEngine(
        feed=feed,
        strategy=strategy,
        initial_capital=args.capital,
    )
    metrics = engine.run()

    # 5. 打印成交汇总
    trades_df = engine.trades_df()
    equity_df = engine.equity_df

    dashboard = Dashboard(equity_df, trades_df)
    dashboard.print_trade_summary()

    # 6. 可视化
    if args.plot or args.save_plot:
        save = args.save_plot or None
        dashboard.plot_equity(
            title=f"{args.symbol} {strategy.name} 回测结果",
            save_path=save,
        )

    print()


if __name__ == "__main__":
    main()
