"""
RSI策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    """RSI（相对强弱指数）策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化RSI策略
        
        Args:
            config: 策略配置
        """
        super().__init__(config)
        
        # 策略参数
        self.period = config.get('period', 14)
        self.oversold = config.get('oversold', 30)
        self.overbought = config.get('overbought', 70)
        
        # 验证参数
        if self.oversold >= self.overbought:
            self.logger.warning("超卖阈值应小于超买阈值，自动调整")
            self.oversold = min(self.oversold, self.overbought - 10)
            self.overbought = max(self.overbought, self.oversold + 10)
        
        self.logger.info(f"RSI策略初始化: period={self.period}, oversold={self.oversold}, overbought={self.overbought}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成RSI策略信号
        
        策略逻辑：
        1. 当RSI低于超卖线时，买入信号
        2. 当RSI高于超买线时，卖出信号
        3. RSI在中间区域时，持有信号
        
        Args:
            data: 包含收盘价的数据
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            self.logger.error("缺少收盘价数据")
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data['close']
        
        # 计算RSI
        rsi = self._calculate_rsi(close_prices)
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成信号
        for i in range(self.period, len(data)):
            current_rsi = rsi.iloc[i] if i < len(rsi) else 50
            
            # 买入信号：RSI低于超卖线
            if current_rsi < self.oversold:
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 卖出信号：RSI高于超买线
            elif current_rsi > self.overbought:
                signals.iloc[i] = self.SIGNAL_SELL
        
        # 过滤信号
        signals = self._filter_signals(signals, rsi)
        
        self.logger.info(f"生成 {signals[signals != self.SIGNAL_HOLD].count()} 个交易信号")
        
        return signals
    
    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            prices: 价格序列
            
        Returns:
            pd.Series: RSI序列
        """
        # 计算价格变化
        delta = prices.diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # 计算相对强度
        rs = gain / loss
        
        # 计算RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _filter_signals(self, signals: pd.Series, rsi: pd.Series) -> pd.Series:
        """
        过滤RSI信号
        
        Args:
            signals: 原始信号序列
            rsi: RSI序列
            
        Returns:
            pd.Series: 过滤后的信号序列
        """
        filtered_signals = signals.copy()
        last_signal = self.SIGNAL_HOLD
        last_signal_idx = -1
        
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals.iloc[i]
            current_rsi = rsi.iloc[i] if i < len(rsi) else 50
            
            if current_signal != self.SIGNAL_HOLD:
                # 检查信号强度
                if current_signal == self.SIGNAL_BUY:
                    # 买入信号需要RSI足够低
                    if current_rsi > self.oversold + 5:  # 增加缓冲
                        filtered_signals.iloc[i] = self.SIGNAL_HOLD
                        continue
                
                elif current_signal == self.SIGNAL_SELL:
                    # 卖出信号需要RSI足够高
                    if current_rsi < self.overbought - 5:  # 增加缓冲
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
            'period': self.period,
            'oversold': self.oversold,
            'overbought': self.overbought,
            'strategy_type': 'oscillator',
            'description': 'RSI振荡器策略'
        }
        base_params.update(strategy_params)
        return base_params
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            str: 策略描述
        """
        return (f"RSI策略 (周期:{self.period}天, 超卖:{self.oversold}, 超买:{self.overbought})\n"
                f"当RSI低于{self.oversold}时买入（超卖），高于{self.overbought}时卖出（超买）。")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算RSI相关指标
        
        Args:
            data: 原始数据
            
        Returns:
            pd.DataFrame: 添加RSI指标后的数据
        """
        if 'close' not in data.columns:
            return data
        
        result = data.copy()
        close_prices = result['close']
        
        # 计算RSI
        result['rsi'] = self._calculate_rsi(close_prices)
        
        # 计算RSI信号
        result['rsi_signal'] = 0
        result.loc[result['rsi'] < self.oversold, 'rsi_signal'] = 1  # 超卖
        result.loc[result['rsi'] > self.overbought, 'rsi_signal'] = -1  # 超买
        
        # 计算RSI背离
        result['rsi_divergence'] = self._calculate_divergence(close_prices, result['rsi'])
        
        return result
    
    def _calculate_divergence(self, prices: pd.Series, rsi: pd.Series, lookback: int = 20) -> pd.Series:
        """
        计算RSI背离
        
        Args:
            prices: 价格序列
            rsi: RSI序列
            lookback: 回溯周期
            
        Returns:
            pd.Series: 背离信号序列
        """
        divergence = pd.Series(index=prices.index, data=0)
        
        for i in range(lookback, len(prices)):
            # 检查看涨背离（价格新低，RSI未新低）
            price_window = prices.iloc[i-lookback:i+1]
            rsi_window = rsi.iloc[i-lookback:i+1]
            
            if len(price_window) > 0 and len(rsi_window) > 0:
                price_low_idx = price_window.argmin()
                rsi_low_idx = rsi_window.argmin()
                
                # 看涨背离
                if (price_low_idx == len(price_window) - 1 and  # 价格创新低
                    rsi_low_idx != len(rsi_window) - 1):  # RSI未创新低
                    divergence.iloc[i] = 1
                
                # 看跌背离（价格新高，RSI未新高）
                price_high_idx = price_window.argmax()
                rsi_high_idx = rsi_window.argmax()
                
                if (price_high_idx == len(price_window) - 1 and  # 价格创新高
                    rsi_high_idx != len(rsi_window) - 1):  # RSI未创新高
                    divergence.iloc[i] = -1
        
        return divergence
    
    def generate_divergence_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成RSI背离信号
        
        Args:
            data: 包含收盘价的数据
            
        Returns:
            pd.Series: 背离交易信号序列
        """
        if 'close' not in data.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 计算RSI指标
        data_with_rsi = self.calculate_indicators(data)
        
        if 'rsi_divergence' not in data_with_rsi.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        divergence = data_with_rsi['rsi_divergence']
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成背离信号
        for i in range(len(divergence)):
            if divergence.iloc[i] == 1:  # 看涨背离
                signals.iloc[i] = self.SIGNAL_BUY
            elif divergence.iloc[i] == -1:  # 看跌背离
                signals.iloc[i] = self.SIGNAL_SELL
        
        return signals