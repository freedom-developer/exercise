#!/bin/bash
# 编译 C++ 指标模块
# 用法: bash build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
make install

echo ""
echo "编译完成！"
echo "生成的 .so 文件已复制到 exercise/quan/"
echo "在 Python 中使用: import quan_indicators"
