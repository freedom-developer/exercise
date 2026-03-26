#pragma once
#include <vector>
#include <cmath>
#include <stdexcept>
#include <limits>

namespace quant {

// -----------------------------------------------------------------------
// 移动平均
// -----------------------------------------------------------------------

/// 简单移动平均 (SMA)
std::vector<double> sma(const std::vector<double>& close, int period);

/// 指数移动平均 (EMA)
std::vector<double> ema(const std::vector<double>& close, int period);

// -----------------------------------------------------------------------
// MACD
// -----------------------------------------------------------------------

struct MACDResult {
    std::vector<double> dif;   // DIF = EMA(fast) - EMA(slow)
    std::vector<double> dea;   // DEA = EMA(DIF, signal)
    std::vector<double> hist;  // MACD柱 = (DIF - DEA) * 2
};

MACDResult macd(const std::vector<double>& close,
                int fast = 12, int slow = 26, int signal = 9);

// -----------------------------------------------------------------------
// RSI
// -----------------------------------------------------------------------

/// RSI(period)，返回与 close 等长的序列，前 period 个为 NaN(用 -1 表示)
std::vector<double> rsi(const std::vector<double>& close, int period = 14);

// -----------------------------------------------------------------------
// 布林带
// -----------------------------------------------------------------------

struct BollResult {
    std::vector<double> mid;
    std::vector<double> upper;
    std::vector<double> lower;
};

BollResult bollinger_bands(const std::vector<double>& close,
                           int period = 20, double k = 2.0);

// -----------------------------------------------------------------------
// ATR
// -----------------------------------------------------------------------

std::vector<double> atr(const std::vector<double>& high,
                        const std::vector<double>& low,
                        const std::vector<double>& close,
                        int period = 14);

// -----------------------------------------------------------------------
// KDJ
// -----------------------------------------------------------------------

struct KDJResult {
    std::vector<double> k;
    std::vector<double> d;
    std::vector<double> j;
};

KDJResult kdj(const std::vector<double>& high,
              const std::vector<double>& low,
              const std::vector<double>& close,
              int n = 9, int m1 = 3, int m2 = 3);

} // namespace quant
