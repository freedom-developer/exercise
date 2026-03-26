"""
回测引擎
负责执行策略回测和绩效评估
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional, Tuple
from ..strategy.base_strategy import BaseStrategy

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化回测引擎
        
        Args:
            config: 回测配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 回测参数
        self.initial_capital = config.get('initial_capital', 100000.0)
        self.commission = config.get('commission', 0.001)  # 手续费率
        self.slippage = config.get('slippage', 0.001)  # 滑点
        self.frequency = config.get('frequency', 'daily')  # 数据频率
        
        # 风险管理参数
        self.max_position_size = config.get('max_position_size', 0.1)
        self.stop_loss = config.get('stop_loss', 0.05)
        self.take_profit = config.get('take_profit', 0.15)
        
        # 回测状态
        self.cash = self.initial_capital
        self.positions = {}  # 持仓 {symbol: quantity}
        self.trades = []  # 交易记录
        self.equity_curve = []  # 权益曲线
        self.drawdown = []  # 回撤曲线
        
        self.logger.info("回测引擎初始化完成")
        self.logger.info(f"初始资金: ${self.initial_capital:,.2f}")
        self.logger.info(f"手续费率: {self.commission:.3%}, 滑点: {self.slippage:.3%}")
    
    def run(self, data: pd.DataFrame, strategy: BaseStrategy) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            data: 回测数据
            strategy: 交易策略
            
        Returns:
            dict: 回测结果
        """
        self.logger.info("开始回测...")
        
        # 重置状态
        self._reset_state()
        
        # 验证数据
        validation = strategy.validate_data(data)
        if not validation['valid']:
            self.logger.error(f"数据验证失败: {validation['message']}")
            return self._create_empty_result()
        
        # 生成交易信号
        self.logger.info("生成交易信号...")
        signals = strategy.generate_signals(data)
        
        if signals.empty or signals[signals != strategy.SIGNAL_HOLD].count() == 0:
            self.logger.warning("未生成有效交易信号")
            return self._create_empty_result()
        
        # 执行回测
        self.logger.info("执行回测...")
        self._execute_backtest(data, signals, strategy)
        
        # 计算绩效指标
        self.logger.info("计算绩效指标...")
        results = self._calculate_results(data, strategy)
        
        self.logger.info("回测完成")
        return results
    
    def _reset_state(self):
        """重置回测状态"""
        self.cash = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self.equity_curve.clear()
        self.drawdown.clear()
    
    def _execute_backtest(self, data: pd.DataFrame, signals: pd.Series, strategy: BaseStrategy):
        """
        执行回测
        
        Args:
            data: 回测数据
            signals: 交易信号
            strategy: 交易策略
        """
        dates = data.index
        close_prices = data['close'] if 'close' in data.columns else pd.Series(index=dates, data=0)
        
        # 假设只有一个交易标的
        symbol = data.get('symbol', 'UNKNOWN').iloc[0] if 'symbol' in data.columns else 'UNKNOWN'
        
        for i, date in enumerate(dates):
            current_price = close_prices.iloc[i] if i < len(close_prices) else 0
            signal = signals.iloc[i] if i < len(signals) else strategy.SIGNAL_HOLD
            
            # 计算当前权益
            position_value = 0
            if symbol in self.positions:
                position_value = self.positions[symbol] * current_price
            
            current_equity = self.cash + position_value
            self.equity_curve.append({
                'date': date,
                'equity': current_equity,
                'cash': self.cash,
                'position_value': position_value
            })
            
            # 执行交易信号
            if signal != strategy.SIGNAL_HOLD and current_price > 0:
                self._execute_trade(
                    date=date,
                    symbol=symbol,
                    price=current_price,
                    signal=signal,
                    strategy=strategy,
                    current_equity=current_equity
                )
    
    def _execute_trade(self, date, symbol, price, signal, strategy, current_equity):
        """
        执行交易
        
        Args:
            date: 交易日期
            symbol: 交易标的
            price: 当前价格
            signal: 交易信号
            strategy: 交易策略
            current_equity: 当前权益
        """
        # 计算交易价格（考虑滑点）
        if signal == strategy.SIGNAL_BUY:
            trade_price = price * (1 + self.slippage)
        else:  # SELL
            trade_price = price * (1 - self.slippage)
        
        # 计算仓位大小
        position_size = strategy.calculate_position_size(
            signal=signal,
            equity=current_equity,
            price=trade_price,
            risk_per_trade=self.max_position_size
        )
        
        # 调整仓位大小考虑现有持仓
        current_position = self.positions.get(symbol, 0)
        
        if signal == strategy.SIGNAL_BUY:
            # 买入：增加多头仓位或减少空头仓位
            target_position = current_position + position_size
            
            # 确保不会过度杠杆
            max_position_value = current_equity * self.max_position_size
            max_shares = max_position_value / trade_price
            
            target_position = min(target_position, max_shares)
            
            # 计算实际交易数量
            trade_quantity = target_position - current_position
            
            if trade_quantity > 0 and self.cash >= trade_quantity * trade_price:
                # 执行买入
                cost = trade_quantity * trade_price
                commission = cost * self.commission
                total_cost = cost + commission
                
                if self.cash >= total_cost:
                    self.cash -= total_cost
                    self.positions[symbol] = target_position
                    
                    self.trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': trade_quantity,
                        'price': trade_price,
                        'cost': cost,
                        'commission': commission,
                        'total_cost': total_cost,
                        'signal': 'BUY'
                    })
        
        elif signal == strategy.SIGNAL_SELL:
            # 卖出：减少多头仓位或增加空头仓位
            if current_position > 0:  # 有多头仓位
                # 平仓部分或全部多头
                sell_quantity = min(current_position, abs(position_size))
                
                if sell_quantity > 0:
                    # 执行卖出
                    proceeds = sell_quantity * trade_price
                    commission = proceeds * self.commission
                    net_proceeds = proceeds - commission
                    
                    self.cash += net_proceeds
                    self.positions[symbol] = current_position - sell_quantity
                    
                    self.trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': sell_quantity,
                        'price': trade_price,
                        'proceeds': proceeds,
                        'commission': commission,
                        'net_proceeds': net_proceeds,
                        'signal': 'SELL'
                    })
    
    def _calculate_results(self, data: pd.DataFrame, strategy: BaseStrategy) -> Dict[str, Any]:
        """
        计算回测结果
        
        Args:
            data: 回测数据
            strategy: 交易策略
            
        Returns:
            dict: 回测结果
        """
        if not self.equity_curve:
            return self._create_empty_result()
        
        # 提取权益数据
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('date', inplace=True)
        
        # 计算基本指标
        initial_equity = self.initial_capital
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - initial_equity) / initial_equity
        
        # 计算年化收益率
        days = (equity_df.index[-1] - equity_df.index[0]).days
        years = days / 365.25
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 计算收益率序列
        equity_series = equity_df['equity']
        returns = equity_series.pct_change().dropna()
        
        # 计算夏普比率
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        
        # 计算最大回撤
        max_drawdown, drawdown_series = self._calculate_max_drawdown(equity_series)
        
        # 计算胜率
        win_rate = self._calculate_win_rate()
        
        # 计算盈亏比
        profit_factor = self._calculate_profit_factor()
        
        # 计算索提诺比率
        sortino_ratio = self._calculate_sortino_ratio(returns)
        
        # 计算Calmar比率
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        # 准备结果
        results = {
            # 资金相关
            'initial_capital': initial_equity,
            'final_capital': final_equity,
            'total_return': total_return,
            'annual_return': annual_return,
            
            # 风险调整收益
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            
            # 风险指标
            'max_drawdown': max_drawdown,
            'volatility': returns.std() * np.sqrt(252),
            
            # 交易统计
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': 0,
            'avg_loss': 0,
            
            # 详细数据
            'equity_curve': equity_df['equity'].tolist(),
            'drawdown': drawdown_series.tolist(),
            'trades': self.trades,
            'dates': equity_df.index.strftime('%Y-%m-%d').tolist(),
            
            # 策略信息
            'strategy_name': strategy.name,
            'strategy_params': strategy.get_parameters(),
            
            # 回测配置
            'backtest_config': self.config
        }
        
        # 计算平均赢亏
        if self.trades:
            winning_trades = [t for t in self.trades if 'net_proceeds' in t and t.get('net_proceeds', 0) > 0]
            losing_trades = [t for t in self.trades if 'net_proceeds' in t and t.get('net_proceeds', 0) < 0]
            
            if winning_trades:
                results['avg_win'] = np.mean([t['net_proceeds'] for t in winning_trades])
            if losing_trades:
                results['avg_loss'] = np.mean([abs(t['net_proceeds']) for t in losing_trades])
        
        return results
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
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
        
        excess_returns = returns - risk_free_rate / 252
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return sharpe
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
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
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
        return sortino
    
    def _calculate_max_drawdown(self, equity_series: pd.Series) -> Tuple[float, pd.Series]:
        """
        计算最大回撤
        
        Args:
            equity_series: 权益序列
            
        Returns:
            tuple: (最大回撤, 回撤序列)
        """
        if len(equity_series) == 0:
            return 0, pd.Series()
        
        # 计算累计最大值
        cumulative_max = equity_series.expanding().max()
        
        # 计算回撤
        drawdown = (equity_series - cumulative_max) / cumulative_max
        
        # 最大回撤
        max_drawdown = drawdown.min()
        
        return abs(max_drawdown), drawdown
    
    def _calculate_win_rate(self) -> float:
        """
        计算胜率
        
        Returns:
            float: 胜率
        """
        if not self.trades:
            return 0
        
        winning_trades = 0
        for trade in self.trades:
            if 'net_proceeds' in trade and trade['net_proceeds'] > 0:
                winning_trades += 1
        
        return winning_trades / len(self.trades)
    
    def _calculate_profit_factor(self) -> float:
        """
        计算盈亏比
        
        Returns:
            float: 盈亏比
        """
        if not self.trades:
            return 0
        
        total_profit = 0
        total_loss = 0
        
        for trade in self.trades:
            if 'net_proceeds' in trade:
                if trade['net_proceeds'] > 0:
                    total_profit += trade['net_proceeds']
                else:
                    total_loss += abs(trade['net_proceeds'])
        
        if total_loss == 0:
            return float('inf') if total_profit > 0 else 0
        
        return total_profit / total_loss
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """
        创建空结果
        
        Returns:
            dict: 空结果
        """
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.initial_capital,
            'total_return': 0,
            'annual_return': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'calmar_ratio': 0,
            'max_drawdown': 0,
            'volatility': 0,
            'total_trades': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'equity_curve': [],
            'drawdown': [],
            'trades': [],
            'dates': [],
            'strategy_name': '',
            'strategy_params': {},
            'backtest_config': self.config
        }
    
    def get_trade_summary(self) -> pd.DataFrame:
        """
        获取交易摘要
        
        Returns:
            pd.DataFrame: 交易摘要
        """
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trades)
    
    def plot_results(self, results: Dict[str, Any]):
        """
        绘制回测结果
        
        Args:
            results: 回测结果
        """
        # 这里可以调用可视化模块
        # 实际使用时需要实现具体的绘图逻辑
        self.logger.info("结果绘图功能需要可视化模块支持")