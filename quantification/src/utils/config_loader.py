"""
配置文件加载器
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        dict: 配置字典
    """
    logger = logging.getLogger(__name__)
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
        return get_default_config()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                config = json.load(f)
            else:
                logger.error(f"不支持的配置文件格式: {config_file.suffix}")
                return get_default_config()
        
        logger.info(f"配置文件加载成功: {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"加载配置文件失败 {config_path}: {e}")
        return get_default_config()

def save_config(config: Dict[str, Any], config_path: str = 'config.yaml'):
    """
    保存配置文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    logger = logging.getLogger(__name__)
    
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            elif config_file.suffix.lower() == '.json':
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                logger.error(f"不支持的配置文件格式: {config_file.suffix}")
                return False
        
        logger.info(f"配置文件保存成功: {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存配置文件失败 {config_path}: {e}")
        return False

def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        dict: 默认配置
    """
    return {
        'data_sources': {
            'yahoo_finance': {
                'enabled': True,
                'cache_days': 7
            },
            'alpha_vantage': {
                'enabled': False,
                'api_key': 'YOUR_API_KEY',
                'rate_limit': 5
            }
        },
        'backtest': {
            'initial_capital': 100000.0,
            'commission': 0.001,
            'slippage': 0.001,
            'start_date': '2020-01-01',
            'end_date': '2023-12-31',
            'frequency': 'daily'
        },
        'risk_management': {
            'max_position_size': 0.1,
            'stop_loss': 0.05,
            'take_profit': 0.15,
            'max_drawdown': 0.2
        },
        'strategies': {
            'moving_average': {
                'enabled': True,
                'short_window': 20,
                'long_window': 50
            },
            'bollinger_bands': {
                'enabled': True,
                'window': 20,
                'num_std': 2
            }
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/quant_studio.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'cache': {
            'enabled': True,
            'directory': 'data/cache',
            'ttl_days': 30
        }
    }

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并配置（深度合并）
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
        
    Returns:
        dict: 合并后的配置
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证配置
    
    Args:
        config: 要验证的配置
        
    Returns:
        dict: 验证结果
    """
    errors = []
    warnings = []
    
    # 检查必要配置
    required_sections = ['data_sources', 'backtest', 'strategies']
    for section in required_sections:
        if section not in config:
            errors.append(f"缺少必要配置节: {section}")
    
    # 检查数据源配置
    if 'data_sources' in config:
        data_sources = config['data_sources']
        
        # 检查是否至少有一个数据源启用
        enabled_sources = [name for name, source in data_sources.items() 
                          if source.get('enabled', False)]
        
        if not enabled_sources:
            warnings.append("没有启用任何数据源")
        
        # 检查Alpha Vantage API密钥
        if data_sources.get('alpha_vantage', {}).get('enabled', False):
            api_key = data_sources['alpha_vantage'].get('api_key', '')
            if not api_key or api_key == 'YOUR_API_KEY':
                warnings.append("Alpha Vantage已启用但未配置有效的API密钥")
    
    # 检查回测配置
    if 'backtest' in config:
        backtest = config['backtest']
        
        if backtest.get('initial_capital', 0) <= 0:
            errors.append("初始资金必须大于0")
        
        if not 0 <= backtest.get('commission', 0) <= 1:
            errors.append("手续费率必须在0到1之间")
        
        if not 0 <= backtest.get('slippage', 0) <= 1:
            errors.append("滑点必须在0到1之间")
    
    # 检查风险管理配置
    if 'risk_management' in config:
        risk = config['risk_management']
        
        if not 0 < risk.get('max_position_size', 0) <= 1:
            errors.append("最大仓位比例必须在0到1之间")
        
        if not 0 <= risk.get('stop_loss', 0) <= 1:
            errors.append("止损比例必须在0到1之间")
        
        if not 0 <= risk.get('take_profit', 0) <= 1:
            errors.append("止盈比例必须在0到1之间")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }