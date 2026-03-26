"""
性能指标计算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

class PerformanceMetrics:
    """性能指标计算器"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        初始化性能指标计算器
        
        Args:
            risk_free_rate: 无风险利率
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_all_metrics(self, equity_curve: List[float], 
                            returns: List[float],
                            trades: List[Dict[str, Any]],
                            dates: Optional[List] = None) -> Dict[str, Any]:
        """
        计算所有性能指标
        
        Args:
            equity_curve: 权益曲线
            returns: 收益率序列
            trades: 交易记录
            dates: 日期序列
            
        Returns:
            dict: 所有性能指标
        """
        metrics = {}
        
        # 基本指标
        metrics.update(self._calculate_basic_metrics(equity_curve, returns, trades, dates))
        
        # 风险调整收益指标
        metrics.update(self._calculate_risk_adjusted_metrics(returns))
        
        # 交易统计指标
        metrics.update(self._calculate_trade_metrics(trades))
        
        # 时间相关指标
        if dates:
            metrics.update(self._calculate_time_metrics(equity_curve, returns, dates))
        
        return metrics
    
    def _calculate_basic_metrics(self, equity_curve: List[float], 
                               returns: List[float],
                               trades: List[Dict[str, Any]],
                               dates: Optional[List] = None) -> Dict[str, Any]:
        """计算基本指标"""
        if not equity_curve:
            return {}
        
        initial_equity = equity_curve[0]
        final_equity = equity_curve[-1]
        total_return = (final_equity - initial_equity) / initial_equity
        
        # 计算年化收益率
        annual_return = 0
        if dates and len(dates) > 1:
            try:
                if isinstance(dates[0], str):
                    start_date = datetime.strptime(dates[0], '%Y-%m-%d')
                    end_date = datetime.strptime(dates[-1], '%Y-%m-%d')
                else:
                    start_date = dates[0]
                    end_date = dates[-1]
                
                days = (end_date - start_date).days
                years = days / 365.25
                
                if years > 0:
                    annual_return = (1 + total_return) ** (1 / years) - 1
            except:
                annual_return = 0
        
        # 计算最大回撤
        max_drawdown, drawdown_series = self.calculate_max_drawdown(equity_curve)
        
        return {
            'initial_capital': initial_equity,
            'final_capital': final_equity,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'drawdown_series': drawdown_series
        }
    
    def _calculate_risk_adjusted_metrics(self, returns: List[float]) -> Dict[str, Any]:
        """计算风险调整收益指标"""
        if not returns:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0,
                'volatility': 0,
                'var_95': 0,
                'cvar_95': 0
            }
        
        returns_series = pd.Series(returns)
        
        # 夏普比率
        sharpe = self.calculate_sharpe_ratio(returns_series)
        
        # 索提诺比率
        sortino = self.calculate_sortino_ratio(returns_series)
        
        # 波动率
        volatility = returns_series.std() * np.sqrt(252)
        
        # VaR和CVaR
        var_95 = self.calculate_var(returns_series, confidence_level=0.95)
        cvar_95 = self.calculate_cvar(returns_series, confidence_level=0.95)
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'volatility': volatility,
            'var_95': var_95,
            'cvar_95': cvar_95
        }
    
    def _calculate_trade_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算交易统计指标"""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'avg_trade': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0
            }
        
        # 提取交易结果
        trade_results = []
        for trade in trades:
            if 'return' in trade:
                trade_results.append(trade['return'])
            elif 'net_proceeds' in trade and 'cost' in trade:
                # 计算收益率
                if trade['cost'] > 0:
                    return_pct = trade['net_proceeds'] / trade['cost']
                    trade_results.append(return_pct)
        
        if not trade_results:
            return {
                'total_trades': len(trades),
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'avg_trade': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0
            }
        
        # 计算赢亏
        winning_trades = [r for r in trade_results if r > 0]
        losing_trades = [r for r in trade_results if r < 0]
        
        total_trades = len(trade_results)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        total_win = sum(winning_trades) if winning_trades else 0
        total_loss = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        avg_trade = np.mean(trade_results) if trade_results else 0
        
        # 计算连续赢/输
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for r in trade_results:
            if r > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            elif r < 0:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_trade': avg_trade,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
    
    def _calculate_time_metrics(self, equity_curve: List[float], 
                              returns: List[float],
                              dates: List) -> Dict[str, Any]:
        """计算时间相关指标"""
        if not dates or len(dates) < 2:
            return {}
        
        try:
            # 计算时间范围
            if isinstance(dates[0], str):
                start_date = datetime.strptime(dates[0], '%Y-%m-%d')
                end_date = datetime.strptime(dates[-1], '%Y-%m-%d')
            else:
                start_date = dates[0]
                end_date = dates[-1]
            
            total_days = (end_date - start_date).days
            total_years = total_days / 365.25
            
            # 计算月度收益率
            monthly_returns = self._calculate_period_returns(returns, dates, 'monthly')
            
            # 计算胜率（月度）
            positive_months = sum(1 for r in monthly_returns if r > 0)
            monthly_win_rate = positive_months / len(monthly_returns) if monthly_returns else 0
            
            # 计算最大月度亏损
            max_monthly_loss = min(monthly_returns) if monthly_returns else 0
            
            return {
                'total_days': total_days,
                'total_years': total_years,
                'monthly_returns': monthly_returns,
                'monthly_win_rate': monthly_win_rate,
                'max_monthly_loss': max_monthly_loss,
                'avg_monthly_return': np.mean(monthly_returns) if monthly_returns else 0
            }
            
        except Exception as e:
            print(f"计算时间指标时出错: {e}")
            return {}
    
    def _calculate_period_returns(self, returns: List[float], dates: List, 
                                 period: str = 'monthly') -> List[float]:
        """计算周期收益率"""
        if not returns or not dates or len(returns) != len(dates):
            return []
        
        df = pd.DataFrame({
            'date': dates,
            'return': returns
        })
        
        # 确保日期格式
        if isinstance(dates[0], str):
            df['date'] = pd.to_datetime(df['date'])
        
        df.set_index('date', inplace=True)
        
        # 按周期重采样
        if period == 'monthly':
            period_returns = df['return'].resample('M').apply(
                lambda x: (1 + x).prod() - 1
            )
        elif period == 'weekly':
            period_returns = df['return'].resample('W').apply(
                lambda x: (1 + x).prod() - 1
            )
        elif period == 'quarterly':
            period_returns = df['return'].resample('Q').apply(
                lambda x: (1 + x).prod() - 1
            )
        else:
            period_returns = pd.Series()
        
        return period_returns.dropna().tolist()
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """计算夏普比率"""
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        excess_returns = returns - self.risk_free_rate / 252
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """计算索提诺比率"""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - self.risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
        return sortino
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Tuple[float, List[float]]:
        """计算最大回撤"""
        if not equity_curve:
            return 0.0, []
        
        equity_series = pd.Series(equity_curve)
        
        # 计算累计最大值
        cumulative_max = equity_series.expanding().max()
        
        # 计算回撤
        drawdown = (equity_series - cumulative_max) / cumulative_max
        
        # 最大回撤
        max_drawdown = drawdown.min()
        
        return abs(max_drawdown), drawdown.tolist()
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """计算在险价值"""
        if len(returns) == 0:
            return 0
        
        # 历史模拟法
        var = -np.percentile(returns, (1 - confidence_level) * 100)
        return var
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """计算条件在险价值"""
        if len(returns) == 0:
            return 0
        
        var = self.calculate_var(returns, confidence_level)
        
        # 计算超过VaR的损失的平均值
        losses_beyond_var = returns[returns < -var]
        
        if len(losses_beyond_var) == 0:
            return var
        
        cvar = -losses_beyond_var.mean()
        return cvar
    
    def calculate_benchmark_metrics(self, strategy_returns: pd.Series,
                                   benchmark_returns: pd.Series) -> Dict[str, Any]:
        """计算相对于基准的指标"""
        if len(strategy_returns) == 0 or len(benchmark_returns) == 0:
            return {}
        
        # 确保长度一致
        min_len = min(len(strategy_returns), len(benchmark_returns))
        strategy_returns = strategy_returns.iloc[:min_len]
        benchmark_returns = benchmark_returns.iloc[:min_len]
        
        # 计算贝塔
        covariance = np.cov(strategy_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
        
        # 计算阿尔法
        strategy_mean = strategy_returns.mean() * 252
        benchmark_mean = benchmark_returns.mean() * 252
        alpha = (strategy_mean - self.risk_free_rate) - beta * (benchmark_mean - self.risk_free_rate)
        
        # 计算信息比率
        active_returns = strategy_returns - benchmark_returns
        information_ratio = np.sqrt(252) * active_returns.mean() / active_returns.std() if active_returns.std() != 0 else 0
        
        # 计算跟踪误差
        tracking_error = active_returns.std() * np.sqrt(252)
        
        # 计算R平方
        correlation = np.corrcoef(strategy_returns, benchmark_returns)[0, 1]
        r_squared = correlation ** 2
        
        return {
            'beta': beta,
            'alpha': alpha,
            'information_ratio': information_ratio,
            'tracking_error': tracking_error,
            'r_squared': r_squared,
            'correlation': correlation
        }