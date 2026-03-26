/**
 * pybind11 绑定
 * 将 C++ 指标函数暴露为 Python 模块 `quan_indicators`
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "indicators.h"

namespace py = pybind11;
using namespace quant;

PYBIND11_MODULE(quan_indicators, m) {
    m.doc() = "量化交易技术指标 C++ 加速模块";

    // SMA
    m.def("sma", &sma,
          py::arg("close"), py::arg("period"),
          "简单移动平均 Simple Moving Average");

    // EMA
    m.def("ema", &ema,
          py::arg("close"), py::arg("period"),
          "指数移动平均 Exponential Moving Average");

    // RSI
    m.def("rsi", &rsi,
          py::arg("close"), py::arg("period") = 14,
          "相对强弱指数 RSI");

    // ATR
    m.def("atr", &atr,
          py::arg("high"), py::arg("low"), py::arg("close"), py::arg("period") = 14,
          "平均真实波幅 ATR");

    // MACD — 返回包含 dif/dea/hist 三个列表的字典
    m.def("macd",
          [](const std::vector<double>& close, int fast, int slow, int signal) {
              auto r = macd(close, fast, slow, signal);
              py::dict d;
              d["dif"]  = r.dif;
              d["dea"]  = r.dea;
              d["hist"] = r.hist;
              return d;
          },
          py::arg("close"),
          py::arg("fast") = 12,
          py::arg("slow") = 26,
          py::arg("signal") = 9,
          "MACD 指标，返回 dict(dif, dea, hist)");

    // 布林带 — 返回字典
    m.def("bollinger_bands",
          [](const std::vector<double>& close, int period, double k) {
              auto r = bollinger_bands(close, period, k);
              py::dict d;
              d["mid"]   = r.mid;
              d["upper"] = r.upper;
              d["lower"] = r.lower;
              return d;
          },
          py::arg("close"), py::arg("period") = 20, py::arg("k") = 2.0,
          "布林带，返回 dict(mid, upper, lower)");

    // KDJ — 返回字典
    m.def("kdj",
          [](const std::vector<double>& high,
             const std::vector<double>& low,
             const std::vector<double>& close,
             int n, int m1, int m2) {
              auto r = kdj(high, low, close, n, m1, m2);
              py::dict d;
              d["k"] = r.k;
              d["d"] = r.d;
              d["j"] = r.j;
              return d;
          },
          py::arg("high"), py::arg("low"), py::arg("close"),
          py::arg("n") = 9, py::arg("m1") = 3, py::arg("m2") = 3,
          "KDJ 随机指标，返回 dict(k, d, j)");
}
