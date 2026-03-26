#!/usr/bin/env python3
"""
测试QuantStudio安装
"""

import sys
import importlib

def test_imports():
    """测试必要的导入"""
    print("测试Python包导入...")
    
    required_packages = [
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib'),
        ('yfinance', 'yfinance'),
        ('scipy', 'scipy'),
        ('sklearn', 'sklearn'),
        ('flask', 'flask'),
        ('plotly', 'plotly'),
        ('yaml', 'yaml')
    ]
    
    all_ok = True
    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (未安装)")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """测试项目结构"""
    print("\n测试项目结构...")
    
    import os
    from pathlib import Path
    
    required_dirs = [
        'src',
        'src/data',
        'src/strategy', 
        'src/backtest',
        'src/utils',
        'strategies',
        'data',
        'logs',
        'results'
    ]
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/data/__init__.py',
        'src/strategy/__init__.py',
        'src/backtest/__init__.py'
    ]
    
    all_ok = True
    
    # 检查目录
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ 目录: {dir_path}")
        else:
            print(f"  ✗ 目录: {dir_path} (不存在)")
            all_ok = False
    
    # 检查文件
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ 文件: {file_path}")
        else:
            print(f"  ✗ 文件: {file_path} (不存在)")
            all_ok = False
    
    return all_ok

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        # 测试配置加载
        from src.utils.config_loader import get_default_config
        config = get_default_config()
        print("  ✓ 配置加载")
        
        # 测试策略管理器
        from src.strategy.strategy_manager import StrategyManager
        strategy_manager = StrategyManager(config)
        print("  ✓ 策略管理器初始化")
        
        # 测试获取策略
        strategy = strategy_manager.get_strategy('moving_average')
        if strategy:
            print("  ✓ 移动平均线策略加载")
        else:
            print("  ✗ 移动平均线策略加载失败")
            return False
        
        print("  ✓ 基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 基本功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("QuantStudio 安装测试")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # 运行测试
    if test_imports():
        tests_passed += 1
    
    if test_project_structure():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    # 显示结果
    print("\n" + "=" * 60)
    print(f"测试结果: {tests_passed}/{total_tests} 通过")
    
    if tests_passed == total_tests:
        print("✓ 所有测试通过！QuantStudio 安装成功。")
        print("\n下一步:")
        print("1. 运行示例: python example_usage.py")
        print("2. 查看帮助: python main.py --help")
        print("3. 开始开发你的策略！")
    else:
        print("✗ 有些测试失败，请检查安装。")
        print("\n建议:")
        print("1. 确保安装了所有依赖: pip install -r requirements.txt")
        print("2. 检查项目结构是否完整")
        print("3. 查看错误信息并修复问题")
    
    print("=" * 60)

if __name__ == "__main__":
    main()