"""
基础策略类
所有策略都应该继承这个类
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import logging

class BaseStrategy(ABC):
    """基础策略抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            config: 策略配置
        """
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        
        # 信号类型
        self.SIGNAL_BUY = 1
        self.SIGNAL_SELL = -1
        self.SIGNAL_HOLD = 0
        
        # 策略状态
        self.initialized = False
        self.position = 0  # 当前仓位：1=多头，-1=空头，0=空仓
        
        self.logger.debug(f"策略 {self.name} 初始化")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 包含必要指标的数据
            
        Returns:
            pd.Series: 交易信号序列
        """
        pass
    
    def calculate_position_size(self, signal: int, equity: float, 
                               price: float, risk_per_trade: float = 0.02) -> float:
        """
        计算仓位大小
        
        Args:
            signal: 交易信号
            equity: 当前权益
            price: 当前价格
            risk_per_trade: 每笔交易风险比例
            
        Returns:
            float: 仓位大小（股票数量）
        """
        if signal == self.SIGNAL_HOLD:
            return 0
        
        # 基于风险管理的仓位计算
        position_value = equity * risk_per_trade
        
        # 计算股票数量
        position_size = position_value / price
        
        # 确保仓位方向正确
        if signal == self.SIGNAL_SELL:
            position_size = -position_size
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, signal: int, 
                           stop_loss_pct: float = 0.05) -> float:
        """
        计算止损价
        
        Args:
            entry_price: 入场价格
            signal: 交易信号
            stop_loss_pct: 止损百分比
            
        Returns:
            float: 止损价格
        """
        if signal == self.SIGNAL_BUY:
            return entry_price * (1 - stop_loss_pct)
        elif signal == self.SIGNAL_SELL:
            return entry_price * (1 + stop_loss_pct)
        else:
            return 0
    
    def calculate_take_profit(self, entry_price: float, signal: int,
                             take_profit_pct: float = 0.15) -> float:
        """
        计算止盈价
        
        Args:
            entry_price: 入场价格
            signal: 交易信号
            take_profit_pct: 止盈百分比
            
        Returns:
            float: 止盈价格
        """
        if signal == self.SIGNAL_BUY:
            return entry_price * (1 + take_profit_pct)
        elif signal == self.SIGNAL_SELL:
            return entry_price * (1 - take_profit_pct)
        else:
            return 0
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据是否满足策略要求
        
        Args:
            data: 要验证的数据
            
        Returns:
            dict: 验证结果
        """
        required_columns = self.get_required_data()
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            return {
                'valid': False,
                'message': f"缺少必要数据列: {missing_columns}",
                'missing_columns': missing_columns
            }
        
        # 检查数据长度
        min_data_points = self.config.get('min_data_points', 100)
        if len(data) < min_data_points:
            return {
                'valid': False,
                'message': f"数据点不足，需要至少 {min_data_points} 个，当前 {len(data)} 个",
                'min_required': min_data_points,
                'current': len(data)
            }
        
        # 检查数据质量
        nan_counts = data[required_columns].isnull().sum()
        if nan_counts.any():
            return {
                'valid': False,
                'message': f"数据存在缺失值",
                'nan_counts': nan_counts[nan_counts > 0].to_dict()
            }
        
        return {
            'valid': True,
            'message': "数据验证通过"
        }
    
    def get_required_data(self) -> list:
        """
        获取策略需要的必要数据列
        
        Returns:
            list: 必要数据列名称列表
        """
        return ['open', 'high', 'low', 'close', 'volume']
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        Returns:
            dict: 策略参数
        """
        return self.config.copy()
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            str: 策略描述
        """
        return f"{self.name} 策略"
    
    def get_signal_types(self) -> Dict[str, int]:
        """
        获取信号类型
        
        Returns:
            dict: 信号类型映射
        """
        return {
            'BUY': self.SIGNAL_BUY,
            'SELL': self.SIGNAL_SELL,
            'HOLD': self.SIGNAL_HOLD
        }
    
    def backtest_report(self, signals: pd.Series, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成策略回测报告
        
        Args:
            signals: 交易信号序列
            data: 原始数据
            
        Returns:
            dict: 回测报告
        """
        if 'close' not in data.columns:
            self.logger.error("无法生成报告：缺少收盘价数据")
            return {}
        
        # 计算交易
        trades = self._extract_trades(signals, data['close'])
        
        # 计算绩效指标
        metrics = self._calculate_metrics(trades, data)
        
        return {
            'trades': trades,
            'metrics': metrics,
            'signals': signals.tolist(),
            'total_trades': len(trades)
        }
    
    def _extract_trades(self, signals: pd.Series, prices: pd.Series) -> list:
        """
        从信号序列中提取交易
        
        Args:
            signals: 交易信号序列
            prices: 价格序列
            
        Returns:
            list: 交易列表
        """
        trades = []
        current_position = 0
        entry_price = 0
        entry_date = None
        
        for date, signal in signals.items():
            price = prices.get(date, 0)
            
            if current_position == 0 and signal != self.SIGNAL_HOLD:
                # 开仓
                current_position = signal
                entry_price = price
                entry_date = date
                
            elif current_position != 0 and signal == -current_position:
                # 平仓
                exit_price = price
                exit_date = date
                
                # 计算交易结果
                if current_position == self.SIGNAL_BUY:
                    pct_return = (exit_price - entry_price) / entry_price
                else:  # SELL
                    pct_return = (entry_price - exit_price) / entry_price
                
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'position': 'LONG' if current_position == self.SIGNAL_BUY else 'SHORT',
                    'return': pct_return,
                    'holding_days': (exit_date - entry_date).days
                })
                
                # 重置状态
                current_position = 0
                entry_price = 0
                entry_date = None
        
        return trades
    
    def _calculate_metrics(self, trades: list, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算绩效指标
        
        Args:
            trades: 交易列表
            data: 原始数据
            
        Returns:
            dict: 绩效指标
        """
        if not trades:
            return {
                'total_return': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0
            }
        
        # 提取收益率
        returns = [trade['return'] for trade in trades]
        winning_trades = [r for r in returns if r > 0]
        losing_trades = [r for r in returns if r < 0]
        
        # 计算指标
        total_return = sum(returns)
        win_rate = len(winning_trades) / len(returns) if returns else 0
        
        total_win = sum(winning_trades) if winning_trades else 0
        total_loss = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        # 计算连续赢/输
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for r in returns:
            if r > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            elif r < 0:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name}({self.config})"