#!/usr/bin/env python3
"""
QuantStudio - 量化交易软件主程序
"""

import argparse
import logging
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.data_manager import DataManager
from src.strategy.strategy_manager import StrategyManager
from src.backtest.backtest_engine import BacktestEngine
from src.visualization.plotter import Plotter
from src.utils.config_loader import load_config

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/quant_studio.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QuantStudio - 量化交易软件')
    parser.add_argument('--strategy', type=str, default='moving_average',
                       help='策略名称 (default: moving_average)')
    parser.add_argument('--symbol', type=str, default='AAPL',
                       help='交易标的 (default: AAPL)')
    parser.add_argument('--start', type=str, default='2020-01-01',
                       help='开始日期 (default: 2020-01-01)')
    parser.add_argument('--end', type=str, default='2023-12-31',
                       help='结束日期 (default: 2023-12-31)')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='初始资金 (default: 100000)')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='配置文件路径 (default: config.yaml)')
    parser.add_argument('--plot', action='store_true',
                       help='显示图表')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("QuantStudio 量化交易软件启动")
    logger.info(f"策略: {args.strategy}, 标的: {args.symbol}")
    logger.info(f"时间范围: {args.start} 到 {args.end}")
    logger.info("=" * 50)
    
    try:
        # 加载配置
        config = load_config(args.config)
        logger.info("配置文件加载成功")
        
        # 初始化数据管理器
        data_manager = DataManager(config)
        
        # 获取数据
        logger.info(f"正在获取 {args.symbol} 数据...")
        data = data_manager.get_data(
            symbol=args.symbol,
            start_date=args.start,
            end_date=args.end
        )
        
        if data.empty:
            logger.error("无法获取数据，请检查网络连接或数据源配置")
            return
        
        logger.info(f"数据获取成功: {len(data)} 条记录")
        logger.info(f"数据时间范围: {data.index[0]} 到 {data.index[-1]}")
        
        # 初始化策略管理器
        strategy_manager = StrategyManager(config)
        
        # 加载策略
        strategy = strategy_manager.get_strategy(args.strategy)
        if not strategy:
            logger.error(f"策略 '{args.strategy}' 不存在")
            return
        
        logger.info(f"策略 '{args.strategy}' 加载成功")
        
        # 初始化回测引擎
        backtest_config = config['backtest'].copy()
        backtest_config['initial_capital'] = args.capital
        
        backtest_engine = BacktestEngine(backtest_config)
        
        # 运行回测
        logger.info("开始回测...")
        results = backtest_engine.run(
            data=data,
            strategy=strategy
        )
        
        # 输出结果
        logger.info("=" * 50)
        logger.info("回测结果:")
        logger.info(f"初始资金: ${args.capital:,.2f}")
        logger.info(f"最终资金: ${results['final_capital']:,.2f}")
        logger.info(f"总收益率: {results['total_return']:.2%}")
        logger.info(f"年化收益率: {results['annual_return']:.2%}")
        logger.info(f"夏普比率: {results['sharpe_ratio']:.2f}")
        logger.info(f"最大回撤: {results['max_drawdown']:.2%}")
        logger.info(f"胜率: {results['win_rate']:.2%}")
        logger.info(f"总交易次数: {results['total_trades']}")
        logger.info("=" * 50)
        
        # 保存结果
        results_file = f"results/{args.strategy}_{args.symbol}_{args.start}_{args.end}.pkl"
        Path("results").mkdir(exist_ok=True)
        import pickle
        with open(results_file, 'wb') as f:
            pickle.dump(results, f)
        logger.info(f"结果已保存到: {results_file}")
        
        # 绘制图表
        if args.plot:
            logger.info("生成图表...")
            plotter = Plotter(config)
            
            # 绘制价格和信号
            plotter.plot_price_signals(
                data=data,
                signals=results['signals'],
                title=f"{args.symbol} - {args.strategy} 策略"
            )
            
            # 绘制资金曲线
            plotter.plot_equity_curve(
                equity=results['equity_curve'],
                title="资金曲线"
            )
            
            # 绘制回撤
            plotter.plot_drawdown(
                drawdown=results['drawdown'],
                title="回撤分析"
            )
            
            logger.info("图表生成完成")
            
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        return 1
    
    logger.info("QuantStudio 运行完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())