cmake_minimum_required(VERSION 3.15)
project(quan_indicators CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译优化
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# 查找 pybind11
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
  # 尝试通过 pip 安装路径查找
  execute_process(
    COMMAND python3 -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )
  find_package(pybind11 CONFIG REQUIRED HINTS ${pybind11_DIR})
endif()

# 构建 Python 扩展模块
pybind11_add_module(quan_indicators
  src/indicators.cpp
  src/bindings.cpp
)

target_include_directories(quan_indicators PRIVATE include)

# 安装到项目根目录（让 Python 可直接 import）
install(TARGETS quan_indicators
  LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/..
)
