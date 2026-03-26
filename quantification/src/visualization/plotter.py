"""
绘图器模块
负责生成各种可视化图表
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List
import seaborn as sns

class Plotter:
    """绘图器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化绘图器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 可视化配置
        vis_config = config.get('visualization', {})
        self.theme = vis_config.get('theme', 'dark')
        self.color_palette = vis_config.get('color_palette', 'viridis')
        self.figure_size = vis_config.get('figure_size', [12, 8])
        
        # 设置matplotlib样式
        self._setup_style()
        
        self.logger.info("绘图器初始化完成")
    
    def _setup_style(self):
        """设置绘图样式"""
        if self.theme == 'dark':
            plt.style.use('dark_background')
            self.bg_color = 'black'
            self.text_color = 'white'
            self.grid_color = 'gray'
        else:
            plt.style.use('seaborn-whitegrid')
            self.bg_color = 'white'
            self.text_color = 'black'
            self.grid_color = 'lightgray'
        
        # 设置颜色
        self.colors = {
            'buy': 'green',
            'sell': 'red',
            'hold': 'gray',
            'price': 'cyan',
            'equity': 'lime',
            'drawdown': 'orange',
            'signal': 'yellow',
            'ma_short': 'magenta',
            'ma_long': 'blue',
            'bb_upper': 'red',
            'bb_lower': 'red',
            'bb_middle': 'orange',
            'rsi': 'purple',
            'macd': 'cyan',
            'macd_signal': 'orange'
        }
    
    def plot_price_signals(self, data: pd.DataFrame, signals: pd.Series, 
                          title: str = "价格和信号", save_path: Optional[str] = None):
        """
        绘制价格和交易信号
        
        Args:
            data: 价格数据
            signals: 交易信号序列
            title: 图表标题
            save_path: 保存路径
        """
        if 'close' not in data.columns:
            self.logger.error("缺少收盘价数据")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size, 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制价格
        dates = data.index
        close_prices = data['close']
        
        ax1.plot(dates, close_prices, label='收盘价', color=self.colors['price'], linewidth=1.5)
        
        # 添加移动平均线（如果存在）
        if 'sma_20' in data.columns:
            ax1.plot(dates, data['sma_20'], label='20日均线', 
                    color=self.colors['ma_short'], linewidth=1, alpha=0.7)
        
        if 'sma_50' in data.columns:
            ax1.plot(dates, data['sma_50'], label='50日均线', 
                    color=self.colors['ma_long'], linewidth=1, alpha=0.7)
        
        # 添加布林带（如果存在）
        if all(col in data.columns for col in ['bb_upper', 'bb_middle', 'bb_lower']):
            ax1.plot(dates, data['bb_upper'], label='布林上轨', 
                    color=self.colors['bb_upper'], linewidth=0.8, alpha=0.5)
            ax1.plot(dates, data['bb_middle'], label='布林中轨', 
                    color=self.colors['bb_middle'], linewidth=0.8, alpha=0.5)
            ax1.plot(dates, data['bb_lower'], label='布林下轨', 
                    color=self.colors['bb_lower'], linewidth=0.8, alpha=0.5)
            ax1.fill_between(dates, data['bb_lower'], data['bb_upper'], 
                            alpha=0.1, color='gray')
        
        # 标记交易信号
        buy_signals = signals[signals == 1]
        sell_signals = signals[signals == -1]
        
        if not buy_signals.empty:
            buy_dates = buy_signals.index
            buy_prices = data.loc[buy_dates, 'close'] if 'close' in data.columns else None
            if buy_prices is not None:
                ax1.scatter(buy_dates, buy_prices, color=self.colors['buy'], 
                          marker='^', s=100, label='买入信号', zorder=5)
        
        if not sell_signals.empty:
            sell_dates = sell_signals.index
            sell_prices = data.loc[sell_dates, 'close'] if 'close' in data.columns else None
            if sell_prices is not None:
                ax1.scatter(sell_dates, sell_prices, color=self.colors['sell'], 
                          marker='v', s=100, label='卖出信号', zorder=5)
        
        ax1.set_title(title, fontsize=16, color=self.text_color)
        ax1.set_ylabel('价格', fontsize=12, color=self.text_color)
        ax1.legend(loc='upper left')
        ax1.grid(True, color=self.grid_color, alpha=0.3)
        
        # 格式化x轴日期
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 绘制成交量（如果存在）
        if 'volume' in data.columns:
            ax2.bar(dates, data['volume'], color='gray', alpha=0.5, width=1)
            ax2.set_ylabel('成交量', fontsize=12, color=self.text_color)
            ax2.grid(True, color=self.grid_color, alpha=0.3, axis='y')
        
        # 格式化底部x轴
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor=self.bg_color)
            self.logger.info(f"图表已保存: {save_path}")
        
        plt.show()
    
    def plot_equity_curve(self, equity: List[float], dates: Optional[List] = None,
                         title: str = "资金曲线", save_path: Optional[str] = None):
        """
        绘制资金曲线
        
        Args:
            equity: 权益序列
            dates: 日期序列
            title: 图表标题
            save_path: 保存路径
        """
        if not equity:
            self.logger.error("权益数据为空")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size, 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # 如果没有日期，使用索引
        if dates is None:
            dates = list(range(len(equity)))
        
        # 转换为pandas Series以便计算
        equity_series = pd.Series(equity, index=dates)
        
        # 绘制资金曲线
        ax1.plot(dates, equity_series, label='资金曲线', 
                color=self.colors['equity'], linewidth=2)
        
        # 计算并绘制移动平均线
        if len(equity) > 20:
            equity_ma = equity_series.rolling(window=20).mean()
            ax1.plot(dates, equity_ma, label='20日移动平均', 
                    color=self.colors['ma_short'], linewidth=1, alpha=0.7)
        
        # 标记高点和低点
        max_equity = equity_series.max()
        min_equity = equity_series.min()
        max_date = equity_series.idxmax()
        min_date = equity_series.idxmin()
        
        ax1.scatter([max_date], [max_equity], color='gold', s=100, 
                   label=f'最高点: {max_equity:,.2f}', zorder=5)
        ax1.scatter([min_date], [min_equity], color='silver', s=100, 
                   label=f'最低点: {min_equity:,.2f}', zorder=5)
        
        ax1.set_title(title, fontsize=16, color=self.text_color)
        ax1.set_ylabel('资金', fontsize=12, color=self.text_color)
        ax1.legend(loc='upper left')
        ax1.grid(True, color=self.grid_color, alpha=0.3)
        
        # 计算并绘制收益率
        returns = equity_series.pct_change().dropna()
        
        if not returns.empty:
            ax2.bar(returns.index, returns.values, 
                   color=np.where(returns >= 0, self.colors['buy'], self.colors['sell']),
                   alpha=0.6, width=1)
            ax2.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
            ax2.set_ylabel('日收益率', fontsize=12, color=self.text_color)
            ax2.grid(True, color=self.grid_color, alpha=0.3, axis='y')
        
        # 格式化x轴
        if isinstance(dates[0], (datetime, pd.Timestamp)):
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor=self.bg_color)
            self.logger.info(f"图表已保存: {save_path}")
        
        plt.show()
    
    def plot_drawdown(self, drawdown: List[float], dates: Optional[List] = None,
                     title: str = "回撤分析", save_path: Optional[str] = None):
        """
        绘制回撤分析
        
        Args:
            drawdown: 回撤序列
            dates: 日期序列
            title: 图表标题
            save_path: 保存路径
        """
        if not drawdown:
            self.logger.error("回撤数据为空")
            return
        
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # 如果没有日期，使用索引
        if dates is None:
            dates = list(range(len(drawdown)))
        
        # 转换为pandas Series以便计算
        drawdown_series = pd.Series(drawdown, index=dates)
        
        # 绘制回撤曲线
        ax.fill_between(dates, drawdown_series, 0, 
                       where=drawdown_series <= 0,
                       color=self.colors['drawdown'], alpha=0.5,
                       label='回撤')
        
        ax.plot(dates, drawdown_series, color=self.colors['drawdown'], 
               linewidth=1, alpha=0.8)
        
        # 标记最大回撤
        max_drawdown = drawdown_series.min()
        max_drawdown_date = drawdown_series.idxmin()
        
        ax.scatter([max_drawdown_date], [max_drawdown], color='red', s=100,
                  label=f'最大回撤: {max_drawdown:.2%}', zorder=5)
        
        # 添加水平线
        ax.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        ax.axhline(y=-0.1, color='yellow', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.axhline(y=-0.2, color='orange', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.axhline(y=-0.3, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
        
        ax.set_title(title, fontsize=16, color=self.text_color)
        ax.set_ylabel('回撤', fontsize=12, color=self.text_color)
        ax.set_xlabel('日期', fontsize=12, color=self.text_color)
        ax.legend(loc='lower left')
        ax.grid(True, color=self.grid_color, alpha=0.3)
        
        # 设置y轴为百分比格式
        from matplotlib.ticker import PercentFormatter
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        
        # 格式化x轴
        if isinstance(dates[0], (datetime, pd.Timestamp)):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor=self.bg_color)
            self.logger.info(f"图表已保存: {save_path}")
        
        plt.show()
    
    def plot_technical_indicators(self, data: pd.DataFrame, 
                                indicators: List[str] = None,
                                title: str = "技术指标", 
                                save_path: Optional[str] = None):
        """
        绘制技术指标
        
        Args:
            data: 包含技术指标的数据
            indicators: 要绘制的指标列表
            title: 图表标题
            save_path: 保存路径
        """
        if indicators is None:
            indicators = ['rsi', 'macd', 'bb_width']
        
        # 确定子图数量
        num_indicators = len([ind for ind in indicators if ind in data.columns])
        if num_indicators == 0:
            self.logger.warning("没有找到指定的技术指标")
            return
        
        fig, axes = plt.subplots(num_indicators, 1, figsize=self.figure_size)
        if num_indicators == 1:
            axes = [axes]
        
        dates = data.index
        current_ax = 0
        
        # 绘制RSI
        if 'rsi' in data.columns and 'rsi' in indicators:
            ax = axes[current_ax]
            ax.plot(dates, data['rsi'], label='RSI', color=self.colors['rsi'], linewidth=1.5)
            
            # 添加超买超卖线
            ax.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.7)
            ax.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.7)
            ax.axhline(y=50, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
            
            ax.fill_between(dates, 70, 100, color='red', alpha=0.1)
            ax.fill_between(dates, 0, 30, color='green', alpha=0.1)
            
            ax.set_ylabel('RSI', fontsize=12, color=self.text_color)
            ax.set_ylim(0, 100)
            ax.legend(loc='upper left')
            ax.grid(True, color=self.grid_color, alpha=0.3)
            current_ax += 1
        
        # 绘制MACD
        if all(col in data.columns for col in ['macd_line', 'macd_signal']) and 'macd' in indicators:
            ax = axes[current_ax]
            ax.plot(dates, data['macd_line'], label='MACD', color=self.colors['macd'], linewidth=1.5)
            ax.plot(dates, data['macd_signal'], label='信号线', color=self.colors['macd_signal'], linewidth=1.5)
            
            # 绘制柱状图
            if 'macd_histogram' in data.columns:
                colors = np.where(data['macd_histogram'] >= 0, self.colors['buy'], self.colors['sell'])
                ax.bar(dates, data['macd_histogram'], color=colors, alpha=0.3, width=1)
            
            ax.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
            ax.set_ylabel('MACD', fontsize=12, color=self.text_color)
            ax.legend(loc='upper left')
            ax.grid(True, color=self.grid_color, alpha=0.3)
            current_ax += 1
        
        # 绘制布林带宽度
        if 'bb_width' in data.columns and 'bb_width' in indicators:
            ax = axes[current_ax]
            ax.plot(dates, data['bb_width'], label='布林带宽度', color='orange', linewidth=1.5)
            ax.set_ylabel('带宽', fontsize=12, color=self.text_color)
            ax.legend(loc='upper left')
            ax.grid(