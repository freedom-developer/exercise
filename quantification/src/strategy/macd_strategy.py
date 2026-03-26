"""
MACD策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    """MACD（移动平均收敛发散）策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化MACD策略
        
        Args:
            config: 策略配置
        """
        super().__init__(config)
        
        # 策略参数
        self.fast_period = config.get('fast_period', 12)
        self.slow_period = config.get('slow_period', 26)
        self.signal_period = config.get('signal_period', 9)
        
        # 验证参数
        if self.fast_period >= self.slow_period:
            self.logger.warning("快速周期应小于慢速周期，自动调整")
            self.fast_period = min(self.fast_period, self.slow_period - 1)
        
        self.logger.info(f"MACD策略初始化: fast={self.fast_period}, slow={self.slow_period}, signal={self.signal_period}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成MACD策略信号
        
        策略逻辑：
        1. 当MACD线上穿信号线时，买入信号
        2. 当MACD线下穿信号线时，卖出信号
        3. 其他情况，持有信号
        
        Args:
            data: 包含收盘价的数据
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            self.logger.error("缺少收盘价数据")
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data['close']
        
        # 计算MACD
        macd_line, signal_line, histogram = self._calculate_macd(close_prices)
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成信号
        for i in range(1, len(data)):
            # 确保有足够的数据计算MACD
            if i < self.slow_period + self.signal_period:
                continue
            
            # 金叉：MACD线上穿信号线
            if (macd_line.iloc[i-1] <= signal_line.iloc[i-1] and 
                macd_line.iloc[i] > signal_line.iloc[i]):
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 死叉：MACD线下穿信号线
            elif (macd_line.iloc[i-1] >= signal_line.iloc[i-1] and 
                  macd_line.iloc[i] < signal_line.iloc[i]):
                signals.iloc[i] = self.SIGNAL_SELL
        
        # 过滤信号
        signals = self._filter_signals(signals, histogram)
        
        self.logger.info(f"生成 {signals[signals != self.SIGNAL_HOLD].count()} 个交易信号")
        
        return signals
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """
        计算MACD指标
        
        Args:
            prices: 价格序列
            
        Returns:
            tuple: (MACD线, 信号线, 柱状图)
        """
        # 计算EMA
        ema_fast = prices.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow_period, adjust=False).mean()
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _filter_signals(self, signals: pd.Series, histogram: pd.Series) -> pd.Series:
        """
        过滤MACD信号
        
        Args:
            signals: 原始信号序列
            histogram: MACD柱状图序列
            
        Returns:
            pd.Series: 过滤后的信号序列
        """
        filtered_signals = signals.copy()
        last_signal = self.SIGNAL_HOLD
        last_signal_idx = -1
        
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals.iloc[i]
            current_histogram = histogram.iloc[i] if i < len(histogram) else 0
            
            if current_signal != self.SIGNAL_HOLD:
                # 检查信号强度（柱状图大小）
                if current_signal == self.SIGNAL_BUY:
                    # 买入信号需要柱状图为正或接近转正
                    if current_histogram < -0.1:  # 如果柱状图仍然很负，过滤掉
                        filtered_signals.iloc[i] = self.SIGNAL_HOLD
                        continue
                
                elif current_signal == self.SIGNAL_SELL:
                    # 卖出信号需要柱状图为负或接近转负
                    if current_histogram > 0.1:  # 如果柱状图仍然很正，过滤掉
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
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'signal_period': self.signal_period,
            'strategy_type': 'trend_momentum',
            'description': 'MACD趋势动量策略'
        }
        base_params.update(strategy_params)
        return base_params
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            str: 策略描述
        """
        return (f"MACD策略 (快速:{self.fast_period}天, 慢速:{self.slow_period}天, 信号:{self.signal_period}天)\n"
                f"当MACD线上穿信号线时买入，下穿时卖出。")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算MACD相关指标
        
        Args:
            data: 原始数据
            
        Returns:
            pd.DataFrame: 添加MACD指标后的数据
        """
        if 'close' not in data.columns:
            return data
        
        result = data.copy()
        close_prices = result['close']
        
        # 计算MACD
        macd_line, signal_line, histogram = self._calculate_macd(close_prices)
        
        result['macd_line'] = macd_line
        result['macd_signal'] = signal_line
        result['macd_histogram'] = histogram
        
        # 计算MACD交叉信号
        result['macd_cross'] = 0
        result.loc[macd_line > signal_line, 'macd_cross'] = 1  # MACD在信号线之上
        result.loc[macd_line < signal_line, 'macd_cross'] = -1  # MACD在信号线之下
        
        # 计算交叉点
        result['macd_cross_signal'] = result['macd_cross'].diff()
        
        # 计算MACD背离
        result['macd_divergence'] = self._calculate_divergence(close_prices, macd_line)
        
        return result
    
    def _calculate_divergence(self, prices: pd.Series, macd_line: pd.Series, lookback: int = 20) -> pd.Series:
        """
        计算MACD背离
        
        Args:
            prices: 价格序列
            macd_line: MACD线序列
            lookback: 回溯周期
            
        Returns:
            pd.Series: 背离信号序列
        """
        divergence = pd.Series(index=prices.index, data=0)
        
        for i in range(lookback, len(prices)):
            # 检查看涨背离（价格新低，MACD未新低）
            price_window = prices.iloc[i-lookback:i+1]
            macd_window = macd_line.iloc[i-lookback:i+1]
            
            if len(price_window) > 0 and len(macd_window) > 0:
                price_low_idx = price_window.argmin()
                macd_low_idx = macd_window.argmin()
                
                # 看涨背离
                if (price_low_idx == len(price_window) - 1 and  # 价格创新低
                    macd_low_idx != len(macd_window) - 1):  # MACD未创新低
                    divergence.iloc[i] = 1
                
                # 看跌背离（价格新高，MACD未新高）
                price_high_idx = price_window.argmax()
                macd_high_idx = macd_window.argmax()
                
                if (price_high_idx == len(price_window) - 1 and  # 价格创新高
                    macd_high_idx != len(macd_window) - 1):  # MACD未创新高
                    divergence.iloc[i] = -1
        
        return divergence
    
    def generate_zero_cross_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成MACD零轴交叉信号
        
        策略逻辑：
        1. 当MACD线上穿零轴时，买入信号
        2. 当MACD线下穿零轴时，卖出信号
        
        Args:
            data: 包含收盘价的数据
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data['close']
        
        # 计算MACD
        macd_line, _, _ = self._calculate_macd(close_prices)
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成零轴交叉信号
        for i in range(1, len(data)):
            if i < self.slow_period:
                continue
            
            # 上穿零轴
            if macd_line.iloc[i-1] <= 0 and macd_line.iloc[i] > 0:
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 下穿零轴
            elif macd_line.iloc[i-1] >= 0 and macd_line.iloc[i] < 0:
                signals.iloc[i] = self.SIGNAL_SELL
        
        return signals
    
    def generate_histogram_signals(self, data: pd.DataFrame, threshold: float = 0.1) -> pd.Series:
        """
        生成MACD柱状图信号
        
        策略逻辑：
        1. 当柱状图由负转正时，买入信号
        2. 当柱状图由正转负时，卖出信号
        
        Args:
            data: 包含收盘价的数据
            threshold: 阈值
            
        Returns:
            pd.Series: 交易信号序列
        """
        if 'close' not in data.columns:
            return pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        close_prices = data['close']
        
        # 计算MACD
        _, _, histogram = self._calculate_macd(close_prices)
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成柱状图信号
        for i in range(1, len(data)):
            if i < self.slow_period + self.signal_period:
                continue
            
            prev_hist = histogram.iloc[i-1]
            curr_hist = histogram.iloc[i]
            
            # 柱状图由负转正
            if prev_hist < -threshold and curr_hist > -threshold:
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 柱状图由正转负
            elif prev_hist > threshold and curr_hist < threshold:
                signals.iloc[i] = self.SIGNAL_SELL
        
        return signals