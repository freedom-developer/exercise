"""
策略管理器
负责策略的加载、管理和执行
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base_strategy import BaseStrategy
from .moving_average_strategy import MovingAverageStrategy
from .bollinger_bands_strategy import BollingerBandsStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy

class StrategyManager:
    """策略管理器"""
    
    def __init__(self, config):
        """
        初始化策略管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 注册策略类
        self.strategy_classes = {
            'moving_average': MovingAverageStrategy,
            'bollinger_bands': BollingerBandsStrategy,
            'rsi': RSIStrategy,
            'macd': MACDStrategy
        }
        
        # 策略实例缓存
        self.strategy_cache = {}
        
        # 策略配置
        self.strategy_configs = config.get('strategies', {})
        
        self.logger.info("策略管理器初始化完成")
        self.logger.info(f"可用策略: {list(self.strategy_classes.keys())}")
    
    def get_strategy(self, strategy_name: str, **kwargs) -> Optional[BaseStrategy]:
        """
        获取策略实例
        
        Args:
            strategy_name: 策略名称
            **kwargs: 额外参数
            
        Returns:
            BaseStrategy: 策略实例，如果不存在则返回None
        """
        # 检查缓存
        cache_key = f"{strategy_name}_{str(kwargs)}"
        if cache_key in self.strategy_cache:
            self.logger.debug(f"从缓存获取策略: {strategy_name}")
            return self.strategy_cache[cache_key]
        
        # 检查策略是否存在
        if strategy_name not in self.strategy_classes:
            self.logger.error(f"策略 '{strategy_name}' 不存在")
            self.logger.info(f"可用策略: {list(self.strategy_classes.keys())}")
            return None
        
        # 检查策略是否启用
        strategy_config = self.strategy_configs.get(strategy_name, {})
        if not strategy_config.get('enabled', True):
            self.logger.warning(f"策略 '{strategy_name}' 未启用")
            return None
        
        try:
            # 合并配置
            config = strategy_config.copy()
            config.update(kwargs)
            
            # 创建策略实例
            strategy_class = self.strategy_classes[strategy_name]
            strategy = strategy_class(config)
            
            # 缓存策略实例
            self.strategy_cache[cache_key] = strategy
            
            self.logger.info(f"策略 '{strategy_name}' 创建成功")
            return strategy
            
        except Exception as e:
            self.logger.error(f"创建策略 '{strategy_name}' 失败: {e}")
            return None
    
    def get_all_strategies(self) -> Dict[str, BaseStrategy]:
        """
        获取所有启用的策略
        
        Returns:
            dict: 策略名称到策略实例的映射
        """
        strategies = {}
        
        for strategy_name in self.strategy_classes:
            strategy = self.get_strategy(strategy_name)
            if strategy:
                strategies[strategy_name] = strategy
        
        return strategies
    
    def register_strategy(self, strategy_name: str, strategy_class):
        """
        注册新策略
        
        Args:
            strategy_name: 策略名称
            strategy_class: 策略类
            
        Returns:
            bool: 是否注册成功
        """
        if not issubclass(strategy_class, BaseStrategy):
            self.logger.error(f"策略类必须继承自 BaseStrategy")
            return False
        
        if strategy_name in self.strategy_classes:
            self.logger.warning(f"策略 '{strategy_name}' 已存在，将被覆盖")
        
        self.strategy_classes[strategy_name] = strategy_class
        self.logger.info(f"策略 '{strategy_name}' 注册成功")
        
        return True
    
    def unregister_strategy(self, strategy_name: str) -> bool:
        """
        取消注册策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            bool: 是否取消成功
        """
        if strategy_name not in self.strategy_classes:
            self.logger.warning(f"策略 '{strategy_name}' 不存在")
            return False
        
        del self.strategy_classes[strategy_name]
        
        # 从缓存中移除
        keys_to_remove = [k for k in self.strategy_cache.keys() 
                         if k.startswith(strategy_name)]
        for key in keys_to_remove:
            del self.strategy_cache[key]
        
        self.logger.info(f"策略 '{strategy_name}' 已取消注册")
        return True
    
    def load_strategy_from_file(self, file_path: str) -> bool:
        """
        从文件加载策略
        
        Args:
            file_path: 策略文件路径
            
        Returns:
            bool: 是否加载成功
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.error(f"策略文件不存在: {file_path}")
            return False
        
        try:
            # 动态导入策略模块
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                file_path.stem, file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找策略类（假设类名与文件名相同）
            strategy_class_name = file_path.stem
            if hasattr(module, strategy_class_name):
                strategy_class = getattr(module, strategy_class_name)
                
                # 注册策略
                return self.register_strategy(strategy_class_name, strategy_class)
            else:
                self.logger.error(f"在文件 {file_path} 中未找到策略类 {strategy_class_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"加载策略文件失败 {file_path}: {e}")
            return False
    
    def load_strategies_from_directory(self, directory: str) -> List[str]:
        """
        从目录加载所有策略
        
        Args:
            directory: 策略目录
            
        Returns:
            list: 成功加载的策略名称列表
        """
        directory = Path(directory)
        
        if not directory.exists():
            self.logger.error(f"策略目录不存在: {directory}")
            return []
        
        loaded_strategies = []
        
        # 查找所有Python文件
        strategy_files = list(directory.glob("*.py"))
        
        for file_path in strategy_files:
            # 跳过__init__.py
            if file_path.name == "__init__.py":
                continue
            
            self.logger.info(f"加载策略文件: {file_path}")
            if self.load_strategy_from_file(file_path):
                loaded_strategies.append(file_path.stem)
        
        self.logger.info(f"从目录加载了 {len(loaded_strategies)} 个策略")
        return loaded_strategies
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """
        获取策略信息
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            dict: 策略信息
        """
        strategy = self.get_strategy(strategy_name)
        
        if not strategy:
            return {}
        
        return {
            'name': strategy_name,
            'description': strategy.get_description(),
            'parameters': strategy.get_parameters(),
            'required_data': strategy.get_required_data(),
            'signal_types': strategy.get_signal_types()
        }
    
    def validate_strategy(self, strategy_name: str, data) -> Dict[str, Any]:
        """
        验证策略是否适用于给定数据
        
        Args:
            strategy_name: 策略名称
            data: 数据
            
        Returns:
            dict: 验证结果
        """
        strategy = self.get_strategy(strategy_name)
        
        if not strategy:
            return {
                'valid': False,
                'message': f"策略 '{strategy_name}' 不存在"
            }
        
        return strategy.validate_data(data)
    
    def clear_cache(self):
        """清空策略缓存"""
        self.strategy_cache.clear()
        self.logger.info("策略缓存已清空")