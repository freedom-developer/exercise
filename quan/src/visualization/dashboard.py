"""
可视化模块
绘制回测结果：净值曲线、回撤、成交记录、K线+信号
"""
import logging
from typing import Optional, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class Dashboard:
    """
    回测结果可视化
    """

    def __init__(self, equity_df: pd.DataFrame, trades_df: pd.DataFrame = None):
        self.equity_df = equity_df
        self.trades_df = trades_df if trades_df is not None else pd.DataFrame()

    def plot_equity(self, title: str = "策略回测结果", save_path: str = None):
        """绘制净值曲线 + 回撤图"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.gridspec as gridspec
            import matplotlib.dates as mdates
        except ImportError:
            logger.error("请安装 matplotlib: pip install matplotlib")
            return

        plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

        fig = plt.figure(figsize=(14, 8), layout="constrained")
        gs = gridspec.GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.05)

        eq = self.equity_df["equity"]
        dates = self.equity_df.index

        # ------ 净值曲线 ------
        ax1 = fig.add_subplot(gs[0])
        ax1.plot(dates, eq, color="#2196F3", linewidth=1.5, label="策略净值")

        # 标记买卖点
        if not self.trades_df.empty:
            buys = self.trades_df[self.trades_df["side"] == "buy"]
            sells = self.trades_df[self.trades_df["side"] == "sell"]
            for date in buys.index:
                if date in self.equity_df.index:
                    ax1.axvline(date, color="#4CAF50", alpha=0.3, linewidth=0.8)
            for date in sells.index:
                if date in self.equity_df.index:
                    ax1.axvline(date, color="#F44336", alpha=0.3, linewidth=0.8)

        ax1.set_title(title, fontsize=14, pad=10)
        ax1.set_ylabel("账户净值 (元)")
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.setp(ax1.get_xticklabels(), visible=False)

        # ------ 日收益率 ------
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        daily_ret = self.equity_df["daily_return"].dropna()
        colors = ["#4CAF50" if r >= 0 else "#F44336" for r in daily_ret]
        ax2.bar(daily_ret.index, daily_ret * 100, color=colors, alpha=0.7, width=1)
        ax2.axhline(0, color="black", linewidth=0.5)
        ax2.set_ylabel("日收益 (%)")
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.get_xticklabels(), visible=False)

        # ------ 回撤曲线 ------
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        peak = eq.cummax()
        drawdown = (eq - peak) / peak * 100
        ax3.fill_between(dates, drawdown, 0, color="#FF5722", alpha=0.5, label="回撤")
        ax3.set_ylabel("回撤 (%)")
        ax3.set_xlabel("日期")
        ax3.legend(loc="lower left")
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.setp(ax3.get_xticklabels(), rotation=30, ha="right")

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            logger.info(f"图表已保存: {save_path}")
        else:
            plt.show()

    def plot_candlestick(
        self,
        feed_df: pd.DataFrame,
        symbol: str = "",
        save_path: str = None,
    ):
        """绘制K线图 + 均线 + 买卖信号"""
        try:
            import mplfinance as mpf
        except ImportError:
            logger.error("请安装 mplfinance: pip install mplfinance")
            return

        # mplfinance 需要 OHLCV 且列名为标准格式
        df = feed_df[["open", "high", "low", "close", "volume"]].copy()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        # 叠加均线
        add_plots = []
        for col, color in [("ma5", "#FF9800"), ("ma20", "#2196F3"), ("ma60", "#9C27B0")]:
            if col in feed_df.columns:
                add_plots.append(
                    mpf.make_addplot(feed_df[col], color=color, width=1, label=col.upper())
                )

        # 买卖点标记
        if not self.trades_df.empty:
            buys = self.trades_df[self.trades_df["side"] == "buy"]["price"].reindex(df.index)
            sells = self.trades_df[self.trades_df["side"] == "sell"]["price"].reindex(df.index)
            if buys.notna().any():
                add_plots.append(mpf.make_addplot(buys, type="scatter", markersize=80,
                                                   marker="^", color="#4CAF50"))
            if sells.notna().any():
                add_plots.append(mpf.make_addplot(sells, type="scatter", markersize=80,
                                                   marker="v", color="#F44336"))

        kwargs = dict(
            type="candle",
            addplot=add_plots if add_plots else None,
            title=f"{symbol} K线图",
            style="yahoo",
            volume=True,
            figsize=(16, 8),
        )
        if save_path:
            kwargs["savefig"] = save_path
        mpf.plot(df, **kwargs)

    def print_trade_summary(self):
        """打印成交汇总"""
        if self.trades_df.empty:
            print("无成交记录")
            return

        total = len(self.trades_df)
        buys = (self.trades_df["side"] == "buy").sum()
        sells = (self.trades_df["side"] == "sell").sum()
        sell_trades = self.trades_df[self.trades_df["side"] == "sell"]
        win_trades = (sell_trades["pnl"] > 0).sum() if not sell_trades.empty else 0
        win_rate = win_trades / len(sell_trades) if len(sell_trades) > 0 else 0
        total_pnl = sell_trades["pnl"].sum() if not sell_trades.empty else 0

        print(f"\n  成交汇总:")
        print(f"    总成交笔数:   {total} (买{buys}/卖{sells})")
        print(f"    卖出胜率:     {win_rate:.1%}")
        print(f"    总已实现盈亏: {total_pnl:,.0f} 元")
