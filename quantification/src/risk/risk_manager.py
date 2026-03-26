"""
风险管理器
负责风险控制和资金管理
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List, Tuple

class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化风险管理器
        
        Args:
            config: 风险配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 风险参数
        self.max_position_size = config.get('max_position_size', 0.1)  # 最大仓位比例
        self.stop_loss = config.get('stop_loss', 0.05)  # 止损比例
        self.take_profit = config.get('take_profit', 0.15)  # 止盈比例
        self.max_drawdown = config.get('max_drawdown', 0.2)  # 最大回撤限制
        self.max_leverage = config.get('max_leverage', 1.0)  # 最大杠杆
        
        # 风险状态
        self.current_drawdown = 0.0
        self.highest_equity = 0.0
        self.risk_free_rate = 0.02  # 无风险利率
        
        self.logger.info("风险管理器初始化完成")
        self.logger.info(f"最大仓位: {self.max_position_size:.1%}, 止损: {self.stop_loss:.1%}, "
                        f"止盈: {self.take_profit:.1%}, 最大回撤: {self.max_drawdown:.1%}")
    
    def calculate_position_size(self, equity: float, entry_price: float, 
                               risk_per_trade: Optional[float] = None) -> float:
        """
        计算仓位大小
        
        Args:
            equity: 当前权益
            entry_price: 入场价格
            risk_per_trade: 每笔交易风险比例，默认为配置值
            
        Returns:
            float: 仓位大小（股票数量）
        """
        if risk_per_trade is None:
            risk_per_trade = self.max_position_size
        
        # 基于风险的资金分配
        risk_amount = equity * risk_per_trade
        
        # 计算股票数量
        position_size = risk_amount / entry_price
        
        # 应用杠杆限制
        max_position = equity * self.max_leverage / entry_price
        position_size = min(position_size, max_position)
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, position_type: str = 'long',
                           stop_loss_pct: Optional[float] = None) -> float:
        """
        计算止损价
        
        Args:
            entry_price: 入场价格
            position_type: 仓位类型 ('long' 或 'short')
            stop_loss_pct: 止损百分比，默认为配置值
            
        Returns:
            float: 止损价格
        """
        if stop_loss_pct is None:
            stop_loss_pct = self.stop_loss
        
        if position_type == 'long':
            return entry_price * (1 - stop_loss_pct)
        elif position_type == 'short':
            return entry_price * (1 + stop_loss_pct)
        else:
            return entry_price
    
    def calculate_take_profit(self, entry_price: float, position_type: str = 'long',
                             take_profit_pct: Optional[float] = None) -> float:
        """
        计算止盈价
        
        Args:
            entry_price: 入场价格
            position_type: 仓位类型 ('long' 或 'short')
            take_profit_pct: 止盈百分比，默认为配置值
            
        Returns:
            float: 止盈价格
        """
        if take_profit_pct is None:
            take_profit_pct = self.take_profit
        
        if position_type == 'long':
            return entry_price * (1 + take_profit_pct)
        elif position_type == 'short':
            return entry_price * (1 - take_profit_pct)
        else:
            return entry_price
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算在险价值 (Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            float: VaR值
        """
        if len(returns) == 0:
            return 0
        
        # 参数法（正态分布假设）
        mean = returns.mean()
        std = returns.std()
        
        # 使用分位数
        var_param = -(mean + std * np.percentile(np.random.randn(10000), (1 - confidence_level) * 100))
        
        # 历史模拟法
        var_historical = -np.percentile(returns, (1 - confidence_level) * 100)
        
        # 返回两者中较保守的值
        return max(var_param, var_historical)
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算条件在险价值 (Conditional Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            float: CVaR值
        """
        if len(returns) == 0:
            return 0
        
        var = self.calculate_var(returns, confidence_level)
        
        # 计算超过VaR的损失的平均值
        losses_beyond_var = returns[returns < -var]
        
        if len(losses_beyond_var) == 0:
            return var
        
        cvar = -losses_beyond_var.mean()
        return cvar
    
    def calculate_max_drawdown(self, equity_series: pd.Series) -> Tuple[float, pd.Series]:
        """
        计算最大回撤
        
        Args:
            equity_series: 权益序列
            
        Returns:
            tuple: (最大回撤, 回撤序列)
        """
        if len(equity_series) == 0:
            return 0.0, pd.Series()
        
        # 计算累计最大值
        cumulative_max = equity_series.expanding().max()
        
        # 计算回撤
        drawdown = (equity_series - cumulative_max) / cumulative_max
        
        # 最大回撤
        max_drawdown = drawdown.min()
        
        return abs(max_drawdown), drawdown
    
    def update_drawdown(self, current_equity: float) -> bool:
        """
        更新回撤状态并检查是否触发风险限制
        
        Args:
            current_equity: 当前权益
            
        Returns:
            bool: 是否触发风险限制（True=触发，应停止交易）
        """
        # 更新最高权益
        if current_equity > self.highest_equity:
            self.highest_equity = current_equity
        
        # 计算当前回撤
        if self.highest_equity > 0:
            self.current_drawdown = (self.highest_equity - current_equity) / self.highest_equity
        else:
            self.current_drawdown = 0.0
        
        # 检查是否超过最大回撤限制
        if self.current_drawdown > self.max_drawdown:
            self.logger.warning(f"触发最大回撤限制: {self.current_drawdown:.2%} > {self.max_drawdown:.2%}")
            return True
        
        return False
    
    def calculate_sharpe_ratio(self, returns: pd.Series, 
                              risk_free_rate: Optional[float] = None) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 夏普比率
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        excess_returns = returns - risk_free_rate / 252  # 日化无风险利率
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series,
                               risk_free_rate: Optional[float] = None) -> float:
        """
        计算索提诺比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 索提诺比率
        """
        if len(returns) == 0:
            return 0
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
        return sortino
    
    def calculate_calmar_ratio(self, annual_return: float, max_drawdown: float) -> float:
        """
        计算Calmar比率
        
        Args:
            annual_return: 年化收益率
            max_drawdown: 最大回撤
            
        Returns:
            float: Calmar比率
        """
        if max_drawdown == 0:
            return float('inf') if annual_return > 0 else 0
        
        return annual_return / max_drawdown
    
    def calculate_volatility(self, returns: pd.Series, annualized: bool = True) -> float:
        """
        计算波动率
        
        Args:
            returns: 收益率序列
            annualized: 是否年化
            
        Returns:
            float: 波动率
        """
        if len(returns) == 0:
            return 0
        
        volatility = returns.std()
        
        if annualized:
            volatility *= np.sqrt(252)
        
        return volatility
    
    def calculate_beta(self, strategy_returns: pd.Series, 
                      benchmark_returns: pd.Series) -> float:
        """
        计算贝塔系数
        
        Args:
            strategy_returns: 策略收益率序列
            benchmark_returns: 基准收益率序列
            
        Returns:
            float: 贝塔系数
        """
        if len(strategy_returns) == 0 or len(benchmark_returns) == 0:
            return 0
        
        # 确保长度一致
        min_len = min(len(strategy_returns), len(benchmark_returns))
        strategy_returns = strategy_returns.iloc[:min_len]
        benchmark_returns = benchmark_returns.iloc[:min_len]
        
        # 计算协方差和方差
        covariance = np.cov(strategy_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        
        if benchmark_variance == 0:
            return 0
        
        beta = covariance / benchmark_variance
        return beta
    
    def calculate_alpha(self, strategy_returns: pd.Series, 
                       benchmark_returns: pd.Series,
                       risk_free_rate: Optional[float] = None) -> float:
        """
        计算阿尔法系数
        
        Args:
            strategy_returns: 策略收益率序列
            benchmark_returns: 基准收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 阿尔法系数
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        beta = self.calculate_beta(strategy_returns, benchmark_returns)
        
        # 计算平均收益率
        strategy_mean = strategy_returns.mean() * 252  # 年化
        benchmark_mean = benchmark_returns.mean() * 252  # 年化
        
        # 计算阿尔法
        alpha = (strategy_mean - risk_free_rate) - beta * (benchmark_mean - risk_free_rate)
        
        return alpha
    
    def calculate_treynor_ratio(self, strategy_returns: pd.Series,
                               benchmark_returns: pd.Series,
                               risk_free_rate: Optional[float] = None) -> float:
        """
        计算特雷诺比率
        
        Args:
            strategy_returns: 策略收益率序列
            benchmark_returns: 基准收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 特雷诺比率
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        beta = self.calculate_beta(strategy_returns, benchmark_returns)
        
        if beta == 0:
            return 0
        
        # 计算超额收益率
        excess_return = strategy_returns.mean() * 252 - risk_free_rate
        
        treynor = excess_return / beta
        return treynor
    
    def generate_risk_report(self, equity_series: pd.Series, 
                            returns: pd.Series,
                            benchmark_returns: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        生成风险报告
        
        Args:
            equity_series: 权益序列
            returns: 收益率序列
            benchmark_returns: 基准收益率序列
            
        Returns:
            dict: 风险报告
        """
        report = {}
        
        # 基本风险指标
        report['current_drawdown'] = self.current_drawdown
        report['highest_equity'] = self.highest_equity
        
        # 计算最大回撤
        max_dd, dd_series = self.calculate_max_drawdown(equity_series)
        report['max_drawdown'] = max_dd
        report['drawdown_series'] = dd_series.tolist() if not dd_series.empty else []
        
        # 计算波动率
        report['volatility'] = self.calculate_volatility(returns)
        report['volatility_annualized'] = self.calculate_volatility(returns, annualized=True)
        
        # 计算VaR和CVaR
        report['var_95'] = self.calculate_var(returns, confidence_level=0.95)
        report['cvar_95'] = self.calculate_cvar(returns, confidence_level=0.95)
        report['var_99'] = self.calculate_var(returns, confidence_level=0.99)
        report['cvar_99'] = self.calculate_cvar(returns, confidence_level=0.99)
        
        # 计算风险调整收益指标
        report['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
        report['sortino_ratio'] = self.calculate_sortino_ratio(returns)
        
        # 如果有基准，计算相对指标
        if benchmark_returns is not None:
            report['beta'] = self.calculate_beta(returns, benchmark_returns)
            report['alpha'] = self.calculate_alpha(returns, benchmark_returns)
            report['treynor_ratio'] = self.calculate_treynor_ratio(returns, benchmark_returns)
        
        # 计算Calmar比率
        if len(returns) > 0:
            annual_return = (1 + returns.mean()) ** 252 - 1
            report['calmar_ratio'] = self.calculate_calmar_ratio(annual_return, max_dd)
        
        # 风险状态
        report['risk_limit_triggered'] = self.update_drawdown(equity_series.iloc[-1] if not equity_series.empty else 0)
        
        return report
    
    def apply_position_sizing(self, signals: pd.Series, equity: float, 
                             prices: pd.Series) -> pd.Series:
        """
        应用仓位大小到信号
        
        Args:
            signals: 原始信号序列
            equity: 当前权益
            prices: 价格序列
            
        Returns:
            pd.Series: 带有仓位大小的信号序列
        """
        if signals.empty or prices.empty:
            return pd.Series()
        
        position_sizes = pd.Series(index=signals.index, data=0.0)
        
        for i, (date, signal) in enumerate(signals.items()):
            if signal != 0 and i < len(prices):
                price = prices.iloc[i]
                position_size = self.calculate_position_size(equity, price)
                position_sizes.iloc[i] = position_size * signal
        
        return position_sizes