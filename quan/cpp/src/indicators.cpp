#include "indicators.h"
#include <numeric>
#include <algorithm>

namespace quant {

constexpr double NaN = std::numeric_limits<double>::quiet_NaN();

// -----------------------------------------------------------------------
// SMA
// -----------------------------------------------------------------------

std::vector<double> sma(const std::vector<double>& close, int period) {
    int n = static_cast<int>(close.size());
    std::vector<double> result(n, NaN);
    if (period <= 0 || period > n) return result;

    double sum = 0.0;
    for (int i = 0; i < period; ++i) sum += close[i];
    result[period - 1] = sum / period;

    for (int i = period; i < n; ++i) {
        sum += close[i] - close[i - period];
        result[i] = sum / period;
    }
    return result;
}

// -----------------------------------------------------------------------
// EMA
// -----------------------------------------------------------------------

std::vector<double> ema(const std::vector<double>& close, int period) {
    int n = static_cast<int>(close.size());
    std::vector<double> result(n, NaN);
    if (period <= 0 || period > n) return result;

    double k = 2.0 / (period + 1);
    // 第一个EMA用SMA初始化
    double sum = 0.0;
    for (int i = 0; i < period; ++i) sum += close[i];
    result[period - 1] = sum / period;

    for (int i = period; i < n; ++i) {
        result[i] = close[i] * k + result[i - 1] * (1.0 - k);
    }
    return result;
}

// -----------------------------------------------------------------------
// MACD
// -----------------------------------------------------------------------

MACDResult macd(const std::vector<double>& close, int fast, int slow, int signal) {
    int n = static_cast<int>(close.size());
    MACDResult res;
    res.dif.resize(n, NaN);
    res.dea.resize(n, NaN);
    res.hist.resize(n, NaN);

    auto ema_fast = ema(close, fast);
    auto ema_slow = ema(close, slow);

    // DIF
    for (int i = 0; i < n; ++i) {
        if (!std::isnan(ema_fast[i]) && !std::isnan(ema_slow[i]))
            res.dif[i] = ema_fast[i] - ema_slow[i];
    }

    // DEA = EMA(DIF, signal) — 只在 DIF 有效的段计算
    double k = 2.0 / (signal + 1);
    int first_valid = -1;
    for (int i = 0; i < n; ++i) {
        if (!std::isnan(res.dif[i])) { first_valid = i; break; }
    }
    if (first_valid < 0) return res;

    // 用前 signal 个 DIF 均值初始化 DEA
    if (first_valid + signal - 1 < n) {
        double sum = 0.0;
        for (int i = first_valid; i < first_valid + signal; ++i) sum += res.dif[i];
        res.dea[first_valid + signal - 1] = sum / signal;
        for (int i = first_valid + signal; i < n; ++i)
            res.dea[i] = res.dif[i] * k + res.dea[i - 1] * (1.0 - k);
    }

    // HIST
    for (int i = 0; i < n; ++i) {
        if (!std::isnan(res.dif[i]) && !std::isnan(res.dea[i]))
            res.hist[i] = (res.dif[i] - res.dea[i]) * 2.0;
    }
    return res;
}

// -----------------------------------------------------------------------
// RSI
// -----------------------------------------------------------------------

std::vector<double> rsi(const std::vector<double>& close, int period) {
    int n = static_cast<int>(close.size());
    std::vector<double> result(n, NaN);
    if (n <= period) return result;

    double k = 1.0 / period;  // com=period-1 → alpha=1/period (Wilder smoothing)
    double avg_gain = 0.0, avg_loss = 0.0;

    // 初始化：用前 period 个差值的平均
    for (int i = 1; i <= period; ++i) {
        double diff = close[i] - close[i - 1];
        if (diff > 0) avg_gain += diff;
        else avg_loss -= diff;
    }
    avg_gain /= period;
    avg_loss /= period;

    auto calc_rsi = [](double g, double l) -> double {
        if (l == 0.0) return 100.0;
        return 100.0 - 100.0 / (1.0 + g / l);
    };

    result[period] = calc_rsi(avg_gain, avg_loss);

    for (int i = period + 1; i < n; ++i) {
        double diff = close[i] - close[i - 1];
        double gain = diff > 0 ? diff : 0.0;
        double loss = diff < 0 ? -diff : 0.0;
        avg_gain = avg_gain * (1.0 - k) + gain * k;
        avg_loss = avg_loss * (1.0 - k) + loss * k;
        result[i] = calc_rsi(avg_gain, avg_loss);
    }
    return result;
}

// -----------------------------------------------------------------------
// 布林带
// -----------------------------------------------------------------------

BollResult bollinger_bands(const std::vector<double>& close, int period, double k) {
    int n = static_cast<int>(close.size());
    BollResult res;
    res.mid.resize(n, NaN);
    res.upper.resize(n, NaN);
    res.lower.resize(n, NaN);

    for (int i = period - 1; i < n; ++i) {
        double sum = 0.0, sum2 = 0.0;
        for (int j = i - period + 1; j <= i; ++j) {
            sum += close[j];
            sum2 += close[j] * close[j];
        }
        double mean = sum / period;
        double var = sum2 / period - mean * mean;
        double std = std::sqrt(std::max(var, 0.0));
        res.mid[i] = mean;
        res.upper[i] = mean + k * std;
        res.lower[i] = mean - k * std;
    }
    return res;
}

// -----------------------------------------------------------------------
// ATR
// -----------------------------------------------------------------------

std::vector<double> atr(const std::vector<double>& high,
                        const std::vector<double>& low,
                        const std::vector<double>& close,
                        int period) {
    int n = static_cast<int>(close.size());
    std::vector<double> result(n, NaN);
    if (n < 2) return result;

    double alpha = 1.0 / period;
    double atr_val = NaN;

    for (int i = 1; i < n; ++i) {
        double tr = std::max({high[i] - low[i],
                              std::abs(high[i] - close[i - 1]),
                              std::abs(low[i] - close[i - 1])});
        if (std::isnan(atr_val)) atr_val = tr;
        else atr_val = atr_val * (1.0 - alpha) + tr * alpha;
        if (i >= period) result[i] = atr_val;
    }
    return result;
}

// -----------------------------------------------------------------------
// KDJ
// -----------------------------------------------------------------------

KDJResult kdj(const std::vector<double>& high,
              const std::vector<double>& low,
              const std::vector<double>& close,
              int n, int m1, int m2) {
    int sz = static_cast<int>(close.size());
    KDJResult res;
    res.k.resize(sz, NaN);
    res.d.resize(sz, NaN);
    res.j.resize(sz, NaN);

    double k_val = 50.0, d_val = 50.0;
    double k_factor = 1.0 / m1;
    double d_factor = 1.0 / m2;

    for (int i = n - 1; i < sz; ++i) {
        double h = *std::max_element(high.begin() + i - n + 1, high.begin() + i + 1);
        double l = *std::min_element(low.begin() + i - n + 1, low.begin() + i + 1);
        double rsv = (h == l) ? 50.0 : (close[i] - l) / (h - l) * 100.0;

        k_val = k_val * (1.0 - k_factor) + rsv * k_factor;
        d_val = d_val * (1.0 - d_factor) + k_val * d_factor;

        res.k[i] = k_val;
        res.d[i] = d_val;
        res.j[i] = 3.0 * k_val - 2.0 * d_val;
    }
    return res;
}

} // namespace quant
