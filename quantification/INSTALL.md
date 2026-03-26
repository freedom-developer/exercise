# QuantStudio 安装指南

## 系统要求

- Python 3.8 或更高版本
- 4GB 以上内存
- 1GB 以上可用磁盘空间
- 网络连接（用于获取数据）

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd quantification
```

或直接下载ZIP文件并解压。

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 如果需要TA-Lib（技术分析库）
# Windows: 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载
# Linux/Mac: brew install ta-lib 或使用 conda
```

### 4. 配置

编辑 `config.yaml` 文件，配置数据源和其他参数：

```yaml
data_sources:
  yahoo_finance:
    enabled: true
    cache_days: 7
  
  alpha_vantage:
    enabled: false  # 设置为true并添加API密钥以启用
    api_key: "YOUR_ALPHA_VANTAGE_API_KEY"
```

### 5. 测试安装

```bash
# 运行示例
python example_usage.py

# 或运行简单回测
python main.py --strategy moving_average --symbol AAPL --start 2022-01-01 --end 2022-12-31
```

## 快速开始

### 1. 基本使用

```bash
# 查看帮助
python main.py --help

# 运行回测
python main.py --strategy moving_average --symbol AAPL --plot

# 使用命令行工具
python run.py backtest --strategy bollinger_bands --symbol GOOGL
```

### 2. 开发新策略

1. 在 `strategies/` 目录中创建新的策略文件
2. 继承 `BaseStrategy` 类
3. 实现 `generate_signals` 方法
4. 使用策略管理器加载策略

### 3. 数据管理

```bash
# 获取数据
python run.py data --symbol AAPL --start 2020-01-01 --end 2023-12-31

# 更新数据
python run.py data --symbol AAPL --update
```

## 故障排除

### 常见问题

1. **无法获取数据**
   - 检查网络连接
   - 确认股票代码正确
   - 检查Yahoo Finance是否可用

2. **依赖安装失败**
   - 确保使用最新版本的pip: `pip install --upgrade pip`
   - 尝试使用清华镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

3. **内存不足**
   - 减少回测数据量
   - 增加系统虚拟内存
   - 使用更高效的策略

### 获取帮助

- 查看详细文档
- 检查日志文件 `logs/quant_studio.log`
- 提交Issue到项目仓库

## 下一步

- 阅读 `README.md` 了解项目架构
- 查看 `example_usage.py` 学习API使用
- 探索 `notebooks/` 目录中的Jupyter Notebook示例
- 开发自己的交易策略