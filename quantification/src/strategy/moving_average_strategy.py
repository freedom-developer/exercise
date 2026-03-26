"""
移动平均线策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    """移动平均线策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化移动平均线策略
        
        Args:
            config: 策略配置
        """
        super().__init__(config)
        
        # 策略参数
        self.short_window = config.get('short_window', 20)
        self.long_window = config.get('long_window', 50)
        
        # 验证参数
        if self.short_window >= self.long_window:
            self.logger.warning("短期窗口应小于长期窗口，自动调整")
            self.short_window = min(self.short_window, self.long_window - 1)
        
        self.logger.info(f"移动平均线策略初始化: short={self.short_window}, long={self.long_window}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成移动平均线策略信号
        
        策略逻辑：
        1. 当短期均线上穿长期均线时，买入信号
        2. 当短期均线下穿长期均线时，卖出信号
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
        
        # 计算移动平均线
        short_ma = close_prices.rolling(window=self.short_window).mean()
        long_ma = close_prices.rolling(window=self.long_window).mean()
        
        # 初始化信号序列
        signals = pd.Series(index=data.index, data=self.SIGNAL_HOLD)
        
        # 生成信号
        for i in range(1, len(data)):
            # 确保有足够的数据计算均线
            if i < self.long_window:
                continue
            
            # 金叉：短期均线上穿长期均线
            if (short_ma.iloc[i-1] <= long_ma.iloc[i-1] and 
                short_ma.iloc[i] > long_ma.iloc[i]):
                signals.iloc[i] = self.SIGNAL_BUY
            
            # 死叉：短期均线下穿长期均线
            elif (short_ma.iloc[i-1] >= long_ma.iloc[i-1] and 
                  short_ma.iloc[i] < long_ma.iloc[i]):
                signals.iloc[i] = self.SIGNAL_SELL
        
        # 过滤信号：避免频繁交易
        signals = self._filter_signals(signals)
        
        self.logger.info(f"生成 {signals[signals != self.SIGNAL_HOLD].count()} 个交易信号")
        
        return signals
    
    def _filter_signals(self, signals: pd.Series) -> pd.Series:
        """
        过滤信号，避免频繁交易
        
        Args:
            signals: 原始信号序列
            
        Returns:
            pd.Series: 过滤后的信号序列
        """
        filtered_signals = signals.copy()
        last_signal = self.SIGNAL_HOLD
        last_signal_idx = -1
        
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals.iloc[i]
            
            if current_signal != self.SIGNAL_HOLD:
                # 检查是否与上一个信号相同
                if current_signal == last_signal:
                    # 如果是相同信号，且距离上次信号太近，则过滤掉
                    if i - last_signal_idx < 5:  # 至少间隔5个交易日
                        filtered_signals.iloc[i] = self.SIGNAL_HOLD
                    else:
                        last_signal = current_signal
                        last_signal_idx = i
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
            'short_window': self.short_window,
            'long_window': self.long_window,
            'strategy_type': 'trend_following',
            'description': '移动平均线交叉策略'
        }
        base_params.update(strategy_params)
        return base_params
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            str: 策略描述
        """
        return (f"移动平均线策略 (短期:{self.short_window}天, 长期:{self.long_window}天)\n"
                f"当短期均线上穿长期均线时买入，下穿时卖出。")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算策略需要的技术指标
        
        Args:
            data: 原始数据
            
        Returns:
            pd.DataFrame: 添加技术指标后的数据
        """
        if 'close' not in data.columns:
            return data
        
        result = data.copy()
        close_prices = result['close']
        
        # 计算移动平均线
        result['ma_short'] = close_prices.rolling(window=self.short_window).mean()
        result['ma_long'] = close_prices.rolling(window=self.long_window).mean()
        
        # 计算均线差值
        result['ma_diff'] = result['ma_short'] - result['ma_long']
        
        # 计算均线交叉信号
        result['ma_cross'] = 0
        result.loc[result['ma_diff'] > 0, 'ma_cross'] = 1  # 短期在长期之上
        result.loc[result['ma_diff'] < 0, 'ma_cross'] = -1  # 短期在长期之下
        
        # 计算交叉点
        result['ma_cross_signal'] = result['ma_cross'].diff()
        
        return result
    
    def optimize_parameters(self, data: pd.DataFrame, 
                           short_range=(5, 50), 
                           long_range=(20, 200)) -> Dict[str, Any]:
        """
        优化策略参数
        
        Args:
            data: 历史数据
            short_range: 短期窗口范围
            long_range: 长期窗口范围
            
        Returns:
            dict: 最优参数和绩效
        """
        best_sharpe = -float('inf')
        best_params = {}
        best_signals = None
        
        # 参数网格搜索
        for short in range(short_range[0], short_range[1] + 1, 5):
            for long in range(max(long_range[0], short + 10), long_range[1] + 1, 10):
                if short >= long:
                    continue
                
                # 更新参数
                self.short_window = short
                self.long_window = long
                
                # 生成信号
                signals = self.generate_signals(data)
                
                # 计算绩效（简化版）
                if 'close' in data.columns:
                    # 计算策略收益率
                    strategy_returns = self._calculate_strategy_returns(signals, data['close'])
                    
                    if len(strategy_returns) > 0:
                        sharpe = self._calculate_sharpe_ratio(strategy_returns)
                        
                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_params = {
                                'short_window': short,
                                'long_window': long
                            }
                            best_signals = signals
        
        # 恢复最优参数
        if best_params:
            self.short_window = best_params['short_window']
            self.long_window = best_params['long_window']
        
        return {
            'best_params': best_params,
            'best_sharpe': best_sharpe,
            'optimized': bool(best_params)
        }
    
    def _calculate_strategy_returns(self, signals: pd.Series, prices: pd.Series) -> pd.Series:
        """
        计算策略收益率
        
        Args:
            signals: 交易信号
            prices: 价格序列
            
        Returns:
            pd.Series: 策略收益率序列
        """
        returns = pd.Series(index=prices.index, data=0.0)
        position = 0
        
        for i in range(1, len(prices)):
            if signals.iloc[i] == self.SIGNAL_BUY:
                position = 1
            elif signals.iloc[i] == self.SIGNAL_SELL:
                position = 0
            
            # 计算当日收益率
            if position != 0 and i > 0:
                daily_return = (prices.iloc[i] - prices.iloc[i-1]) / prices.iloc[i-1]
                returns.iloc[i] = daily_return * position
        
        return returns
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 夏普比率
        """
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252  # 日化无风险利率
        if excess_returns.std() == 0:
            return 0
        
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return sharpe