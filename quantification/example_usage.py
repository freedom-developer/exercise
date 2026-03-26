#!/usr/bin/env python3
"""
QuantStudio 使用示例
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.data_manager import DataManager
from src.strategy.strategy_manager import StrategyManager
from src.backtest.backtest_engine import BacktestEngine
from src.utils.config_loader import get_default_config

def main():
    """主函数"""
    print("=" * 60)
    print("QuantStudio 量化交易软件 - 使用示例")
    print("=" * 60)
    
    # 创建默认配置
    config = get_default_config()
    
    # 1. 初始化数据管理器
    print("\n1. 初始化数据管理器...")
    data_manager = DataManager(config)
    
    # 2. 获取数据
    print("\n2. 获取AAPL数据 (2022-01-01 到 2022-12-31)...")
    data = data_manager.get_data(
        symbol='AAPL',
        start_date='2022-01-01',
        end_date='2022-12-31'
    )
    
    if data.empty:
        print("  错误: 无法获取数据，请检查网络连接")
        return
    
    print(f"  获取到 {len(data)} 条数据")
    print(f"  数据列: {list(data.columns)}")
    print(f"  时间范围: {data.index[0]} 到 {data.index[-1]}")
    
    # 3. 初始化策略管理器
    print("\n3. 初始化策略管理器...")
    strategy_manager = StrategyManager(config)
    
    # 4. 获取移动平均线策略
    print("\n4. 加载移动平均线策略...")
    strategy = strategy_manager.get_strategy('moving_average')
    
    if not strategy:
        print("  错误: 无法加载策略")
        return
    
    print(f"  策略: {strategy.get_description()}")
    print(f"  参数: {strategy.get_parameters()}")
    
    # 5. 验证数据
    print("\n5. 验证数据...")
    validation = strategy.validate_data(data)
    if validation['valid']:
        print("  ✓ 数据验证通过")
    else:
        print(f"  ✗ 数据验证失败: {validation['message']}")
        return
    
    # 6. 生成交易信号
    print("\n6. 生成交易信号...")
    signals = strategy.generate_signals(data)
    
    signal_counts = signals.value_counts()
    print(f"  买入信号: {signal_counts.get(1, 0)} 个")
    print(f"  卖出信号: {signal_counts.get(-1, 0)} 个")
    print(f"  持有信号: {signal_counts.get(0, 0)} 个")
    
    # 7. 初始化回测引擎
    print("\n7. 初始化回测引擎...")
    backtest_engine = BacktestEngine(config['backtest'])
    
    # 8. 运行回测
    print("\n8. 运行回测...")
    results = backtest_engine.run(data, strategy)
    
    # 9. 显示结果
    print("\n9. 回测结果:")
    print("  " + "-" * 40)
    print(f"  初始资金: ${results['initial_capital']:,.2f}")
    print(f"  最终资金: ${results['final_capital']:,.2f}")
    print(f"  总收益率: {results['total_return']:.2%}")
    print(f"  年化收益率: {results['annual_return']:.2%}")
    print(f"  夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {results['max_drawdown']:.2%}")
    print(f"  胜率: {results['win_rate']:.2%}")
    print(f"  总交易次数: {results['total_trades']}")
    print("  " + "-" * 40)
    
    # 10. 保存结果
    print("\n10. 保存结果...")
    import pickle
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    results_file = results_dir / "example_backtest_results.pkl"
    with open(results_file, 'wb') as f:
        pickle.dump(results, f)
    
    print(f"  结果已保存到: {results_file}")
    
    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()