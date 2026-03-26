"""
回测绩效指标计算
"""
import numpy as np
import pandas as pd
from typing import Optional


class PerformanceMetrics:
    """
    计算并展示回测绩效指标
    输入：净值曲线 DataFrame（index=date, columns含 equity/daily_return）
    """

    def __init__(self, equity_df: pd.DataFrame, risk_free_rate: float = 0.03):
        self.df = equity_df.copy()
        self.risk_free_rate = risk_free_rate  # 年化无风险利率
        self._metrics: Optional[dict] = None

    def calculate(self) -> dict:
        if self._metrics is not None:
            return self._metrics

        df = self.df
        if df.empty or "equity" not in df.columns:
            return {}

        equity = df["equity"]
        daily_ret = df["daily_return"].dropna()

        # 基础指标
        total_return = (equity.iloc[-1] - equity.iloc[0]) / equity.iloc[0]
        n_days = (df.index[-1] - df.index[0]).days
        n_years = n_days / 365.0
        annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

        # 波动率
        annual_vol = daily_ret.std() * np.sqrt(252)

        # Sharpe
        daily_rf = self.risk_free_rate / 252
        excess = daily_ret - daily_rf
        sharpe = (excess.mean() / excess.std() * np.sqrt(252)) if excess.std() > 0 else 0

        # Sortino（只考虑下行波动）
        downside = daily_ret[daily_ret < 0]
        sortino_std = downside.std() * np.sqrt(252)
        sortino = ((annual_return - self.risk_free_rate) / sortino_std) if sortino_std > 0 else 0

        # 最大回撤
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()
        max_dd_date = drawdown.idxmin()

        # 回撤持续时间
        dd_duration = self._max_drawdown_duration(equity)

        # Calmar
        calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # 胜率（正收益天数）
        win_rate = (daily_ret > 0).mean()

        # 盈亏比
        avg_win = daily_ret[daily_ret > 0].mean() if (daily_ret > 0).any() else 0
        avg_loss = daily_ret[daily_ret < 0].mean() if (daily_ret < 0).any() else 0
        profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        self._metrics = {
            "总收益率":     f"{total_return:.2%}",
            "年化收益率":   f"{annual_return:.2%}",
            "年化波动率":   f"{annual_vol:.2%}",
            "Sharpe比率":  f"{sharpe:.3f}",
            "Sortino比率": f"{sortino:.3f}",
            "Calmar比率":  f"{calmar:.3f}",
            "最大回撤":    f"{max_drawdown:.2%}",
            "最大回撤日期": str(max_dd_date.date()) if hasattr(max_dd_date, 'date') else str(max_dd_date),
            "最大回撤持续": f"{dd_duration}天",
            "日胜率":      f"{win_rate:.2%}",
            "盈亏比":      f"{profit_loss_ratio:.2f}",
            "回测天数":    n_days,
        }
        return self._metrics

    @staticmethod
    def _max_drawdown_duration(equity: pd.Series) -> int:
        """最大回撤持续天数"""
        peak = equity.cummax()
        in_drawdown = equity < peak
        max_dur = 0
        cur_dur = 0
        for v in in_drawdown:
            if v:
                cur_dur += 1
                max_dur = max(max_dur, cur_dur)
            else:
                cur_dur = 0
        return max_dur

    def print_report(self):
        """打印绩效报告"""
        m = self.calculate()
        print("\n" + "=" * 45)
        print("         回测绩效报告")
        print("=" * 45)
        for k, v in m.items():
            print(f"  {k:<12}: {v}")
        print("=" * 45)

    def get_drawdown_series(self) -> pd.Series:
        equity = self.df["equity"]
        peak = equity.cummax()
        return (equity - peak) / peak
