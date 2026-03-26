"""
布林带策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    """布林带策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化布林带策略
        
        Args:
            config: 策略配置
        """
        super().__init__(config)
        
        # 策略参数
        self.window = config.get('window', 20)
        self.num_std = config.get('num_std', 2)
        
        self.logger.info(f"布林带策略初始化: window={self.window}, num_std={self.num_std}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成布林带策略信号
        
        策略逻辑：
        1. 当价格触及下轨时，买入信号（超卖）
        2. 当价格触及上轨时，卖出信号（超买）
        3. 价格在中轨附近时，持有信号
        
        Args:
            data: 包含收盘价的数据
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            self.logger.error("缺少收盘价数据")
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data['close']
        
        # 计算布林带
        middle_band = close_prices.rolling(window=self.window).mean()
        std = close_prices.rolling(window=self.window).std()
        upper_band = middle_band + (std * self.num_std)
        lower_band = middle_band - (std * self.num_std)
        
        # 计算%b指标（价格在布林带中的位置）
        bb_percent = (close_prices - lower_band) / (upper_band - lower_band)
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成信号
        for i in range(self.window, len(data)):
            current_price = close_prices.iloc[i]
            current_upper = upper_band.iloc[i]
            current_lower = lower_band.iloc[i]
            current_bb_percent = bb_percent.iloc[i]
            
            # 买入信号：价格触及下轨或%b < 0.2
            if (current_price <= current_lower or current_bb_percent < 0.2):
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 卖出信号：价格触及上轨或%b > 0.8
            elif (current_price >= current_upper or current_bb_percent > 0.8):
                signals.iloc[i] = self.SIGNAL_SELL
        
        # 过滤信号
        signals = self._filter_signals(signals, bb_percent)
        
        self.logger.info(f"生成 {signals[signals != self.SIGNAL_HOLD].count()} 个交易信号")
        
        return signals
    
    def _filter_signals(self, signals: pd.Series, bb_percent: pd.Series) -> pd.Series:
        """
        过滤信号，基于布林带位置
        
        Args:
            signals: 原始信号序列
            bb_percent: %b指标序列
            
        Returns:
            pd.Series: 过滤后的信号序列
        """
        filtered_signals = signals.copy()
        last_signal = self.SIGNAL_HOLD
        last_signal_idx = -1
        
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals.iloc[i]
            current_bb = bb_percent.iloc[i] if i < len(bb_percent) else 0.5
            
            if current_signal != self.SIGNAL_HOLD:
                # 检查信号质量
                if current_signal == self.SIGNAL_BUY:
                    # 买入信号需要%b足够低
                    if current_bb > 0.3:  # 如果%b不够低，过滤掉
                        filtered_signals.iloc[i] = self.SIGNAL_HOLD
                        continue
                
                elif current_signal == self.SIGNAL_SELL:
                    # 卖出信号需要%b足够高
                    if current_bb < 0.7:  # 如果%b不够高，过滤掉
                        filtered_signals.iloc[i] = self.SIGNAL_HOLD
                        continue
                
                # 检查是否与上一个信号相同且距离太近
                if current_signal == last_signal and i - last_signal_idx < 10:
                    filtered_signals.iloc[i] = self.SIGNAL_HOLD
                else:
                    last_signal = current_signal
                    last_signal_idx = i
        
        return filtered_signals
    
    def get_required_data(self) -> list:
        """
        获取策略需要的必要数据列
        
        Returns:
            list: 必要数据列名称列表
        """
        return ['close']
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        Returns:
            dict: 策略参数
        """
        base_params = super().get_parameters()
        strategy_params = {
            'window': self.window,
            'num_std': self.num_std,
            'strategy_type': 'mean_reversion',
            'description': '布林带均值回归策略'
        }
        base_params.update(strategy_params)
        return base_params
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            str: 策略描述
        """
        return (f"布林带策略 (窗口:{self.window}天, 标准差倍数:{self.num_std})\n"
                f"当价格触及布林带下轨时买入（超卖），触及上轨时卖出（超买）。")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算布林带指标
        
        Args:
            data: 原始数据
            
        Returns:
            pd.DataFrame: 添加布林带指标后的数据
        """
        if 'close' not in data.columns:
            return data
        
        result = data.copy()
        close_prices = result['close']
        
        # 计算布林带
        result['bb_middle'] = close_prices.rolling(window=self.window).mean()
        bb_std = close_prices.rolling(window=self.window).std()
        result['bb_upper'] = result['bb_middle'] + (bb_std * self.num_std)
        result['bb_lower'] = result['bb_middle'] - (bb_std * self.num_std)
        
        # 计算带宽
        result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / result['bb_middle']
        
        # 计算%b指标
        result['bb_percent'] = (close_prices - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'])
        
        # 计算价格与布林带的关系
        result['bb_position'] = 0
        result.loc[close_prices > result['bb_upper'], 'bb_position'] = 1  # 上轨之上
        result.loc[close_prices < result['bb_lower'], 'bb_position'] = -1  # 下轨之下
        
        return result
    
    def get_bandwidth_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        获取布林带带宽统计
        
        Args:
            data: 包含布林带指标的数据
            
        Returns:
            dict: 带宽统计信息
        """
        if 'bb_width' not in data.columns:
            data = self.calculate_indicators(data)
        
        if 'bb_width' not in data.columns:
            return {}
        
        bb_width = data['bb_width'].dropna()
        
        return {
            'mean': bb_width.mean(),
            'std': bb_width.std(),
            'min': bb_width.min(),
            'max': bb_width.max(),
            'current': bb_width.iloc[-1] if len(bb_width) > 0 else 0,
            'percentile_25': bb_width.quantile(0.25),
            'percentile_75': bb_width.quantile(0.75)
        }
    
    def generate_band_squeeze_signals(self, data: pd.DataFrame, 
                                     squeeze_threshold: float = 0.5) -> pd.Series:
        """
        生成布林带挤压信号（波动率突破策略）
        
        策略逻辑：
        1. 当布林带宽度收缩到历史低位时（挤压），准备突破
        2. 当价格突破上轨时买入，跌破下轨时卖出
        
        Args:
            data: 包含收盘价的数据
            squeeze_threshold: 挤压阈值（带宽百分位）
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 计算布林带指标
        data_with_bb = self.calculate_indicators(data)
        
        if 'bb_width' not in data_with_bb.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data_with_bb['close']
        bb_width = data_with_bb['bb_width']
        bb_upper = data_with_bb['bb_upper']
        bb_lower = data_with_bb['bb_lower']
        
        # 计算带宽百分位
        bb_width_percentile = bb_width.rolling(window=100).apply(
            lambda x: (x.iloc[-1] <= x.quantile(squeeze_threshold)) if len(x) > 20 else False
        )
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成挤压突破信号
        for i in range(100, len(data_with_bb)):
            # 检查是否处于挤压状态
            if bb_width_percentile.iloc[i]:
                current_price = close_prices.iloc[i]
                prev_price = close_prices.iloc[i-1]
                
                # 向上突破
                if (prev_price <= bb_upper.iloc[i-1] and 
                    current_price > bb_upper.iloc[i]):
                    signals.iloc[i] = self.SIGNAL_BUY
                
                # 向下突破
                elif (prev_price >= bb_lower.iloc[i-1] and 
                      current_price < bb_lower.iloc[i]):
                    signals.iloc[i] = self.SIGNAL_SELL
        
        return signals