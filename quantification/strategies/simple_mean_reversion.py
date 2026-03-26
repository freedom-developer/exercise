"""
简单均值回归策略示例
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class SimpleMeanReversion:
    """简单均值回归策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            config: 策略配置
        """
        self.config = config
        self.lookback = config.get('lookback', 20)
        self.std_threshold = config.get('std_threshold', 2)
        
        # 信号类型
        self.SIGNAL_BUY = 1
        self.SIGNAL_SELL = -1
        self.SIGNAL_HOLD = 0
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        策略逻辑：
        1. 当价格低于均值减去N倍标准差时买入（超卖）
        2. 当价格高于均值加上N倍标准差时卖出（超买）
        
        Args:
            data: 包含收盘价的数据
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data['close']
        
        # 计算滚动均值和标准差
        rolling_mean = close_prices.rolling(window=self.lookback).mean()
        rolling_std = close_prices.rolling(window=self.lookback).std()
        
        # 计算上下轨
        upper_band = rolling_mean + (rolling_std * self.std_threshold)
        lower_band = rolling_mean - (rolling_std * self.std_threshold)
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成信号
        for i in range(self.lookback, len(data)):
            current_price = close_prices.iloc[i]
            
            # 买入信号：价格低于下轨
            if current_price < lower_band.iloc[i]:
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 卖出信号：价格高于上轨
            elif current_price > upper_band.iloc[i]:
                signals.iloc[i] = self.SIGNAL_SELL
        
        return signals
    
    def get_description(self) -> str:
        """获取策略描述"""
        return f"简单均值回归策略 (lookback={self.lookback}, std_threshold={self.std_threshold})"
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {
            'lookback': self.lookback,
            'std_threshold': self.std_threshold,
            'strategy_type': 'mean_reversion'
        }