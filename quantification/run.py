#!/usr/bin/env python3
"""
QuantStudio 启动脚本
"""

import sys
import argparse
from pathlib import Path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QuantStudio - 量化交易软件')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 运行回测命令
    backtest_parser = subparsers.add_parser('backtest', help='运行回测')
    backtest_parser.add_argument('--strategy', type=str, default='moving_average',
                               help='策略名称')
    backtest_parser.add_argument('--symbol', type=str, default='AAPL',
                               help='交易标的')
    backtest_parser.add_argument('--start', type=str, default='2020-01-01',
                               help='开始日期')
    backtest_parser.add_argument('--end', type=str, default='2023-12-31',
                               help='结束日期')
    backtest_parser.add_argument('--capital', type=float, default=100000.0,
                               help='初始资金')
    
    # 数据获取命令
    data_parser = subparsers.add_parser('data', help='数据管理')
    data_parser.add_argument('--symbol', type=str, required=True,
                           help='股票代码')
    data_parser.add_argument('--start', type=str, default='2020-01-01',
                           help='开始日期')
    data_parser.add_argument('--end', type=str, default='2023-12-31',
                           help='结束日期')
    data_parser.add_argument('--update', action='store_true',
                           help='更新数据')
    
    # 策略管理命令
    strategy_parser = subparsers.add_parser('strategy', help='策略管理')
    strategy_parser.add_argument('--list', action='store_true',
                               help='列出所有策略')
    strategy_parser.add_argument('--info', type=str,
                               help='查看策略信息')
    strategy_parser.add_argument('--load', type=str,
                               help='从文件加载策略')
    
    # 示例命令
    subparsers.add_parser('example', help='运行示例')
    
    args = parser.parse_args()
    
    if args.command == 'backtest':
        run_backtest(args)
    elif args.command == 'data':
        manage_data(args)
    elif args.command == 'strategy':
        manage_strategy(args)
    elif args.command == 'example':
        run_example()
    else:
        parser.print_help()

def run_backtest(args):
    """运行回测"""
    print(f"运行回测: {args.strategy} 策略, 标的: {args.symbol}")
    print(f"时间范围: {args.start} 到 {args.end}")
    print(f"初始资金: ${args.capital:,.2f}")
    
    # 这里调用主程序的回测功能
    import subprocess
    cmd = [
        sys.executable, 'main.py',
        '--strategy', args.strategy,
        '--symbol', args.symbol,
        '--start', args.start,
        '--end', args.end,
        '--capital', str(args.capital),
        '--plot'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"回测运行失败: {e}")
    except FileNotFoundError:
        print("错误: 找不到 main.py，请确保在项目根目录运行")

def manage_data(args):
    """数据管理"""
    if args.update:
        print(f"更新 {args.symbol} 数据...")
        # 这里实现数据更新逻辑
    else:
        print(f"获取 {args.symbol} 数据 ({args.start} 到 {args.end})...")
        # 这里实现数据获取逻辑

def manage_strategy(args):
    """策略管理"""
    if args.list:
        print("可用策略:")
        print("  - moving_average: 移动平均线策略")
        print("  - bollinger_bands: 布林带策略")
        print("  - rsi: RSI策略")
        print("  - macd: MACD策略")
    elif args.info:
        print(f"查看策略信息: {args.info}")
        # 这里实现策略信息查看
    elif args.load:
        print(f"加载策略文件: {args.load}")
        # 这里实现策略加载

def run_example():
    """运行示例"""
    print("运行示例程序...")
    import subprocess
    cmd = [sys.executable, 'example_usage.py']
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"示例运行失败: {e}")
    except FileNotFoundError:
        print("错误: 找不到 example_usage.py")

if __name__ == "__main__":
    main()