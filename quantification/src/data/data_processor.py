"""
数据处理器
负责数据的清洗、转换和特征工程
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Optional, List, Dict, Any

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config):
        """
        初始化数据处理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("数据处理器初始化完成")
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        处理数据
        
        Args:
            data: 原始数据
            
        Returns:
            pandas.DataFrame: 处理后的数据
        """
        if data.empty:
            return data
        
        self.logger.info(f"开始处理数据，原始数据形状: {data.shape}")
        
        # 复制数据以避免修改原始数据
        processed_data = data.copy()
        
        # 1. 数据清洗
        processed_data = self._clean_data(processed_data)
        
        # 2. 处理缺失值
        processed_data = self._handle_missing_values(processed_data)
        
        # 3. 计算技术指标
        processed_data = self._calculate_technical_indicators(processed_data)
        
        # 4. 计算收益率
        processed_data = self._calculate_returns(processed_data)
        
        # 5. 添加时间特征
        processed_data = self._add_time_features(processed_data)
        
        # 6. 数据标准化（可选）
        # processed_data = self._normalize_data(processed_data)
        
        self.logger.info(f"数据处理完成，处理后数据形状: {processed_data.shape}")
        
        return processed_data
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗
        
        Args:
            data: 原始数据
            
        Returns:
            pandas.DataFrame: 清洗后的数据
        """
        self.logger.info("数据清洗...")
        
        # 检查必要的列
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            self.logger.warning(f"缺少必要列: {missing_columns}")
            # 尝试使用其他名称的列
            column_mapping = {
                'Open': 'open', 'High': 'high', 'Low': 'low', 
                'Close': 'close', 'Volume': 'volume'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in data.columns and new_col not in data.columns:
                    data[new_col] = data[old_col]
        
        # 确保索引是DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            self.logger.info("转换索引为DatetimeIndex")
            try:
                data.index = pd.to_datetime(data.index)
            except:
                self.logger.warning("无法转换索引为日期时间")
        
        # 按日期排序
        data = data.sort_index()
        
        # 移除重复的索引
        data = data[~data.index.duplicated(keep='first')]
        
        # 检查异常值（价格不能为负）
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in data.columns:
                invalid_mask = data[col] <= 0
                if invalid_mask.any():
                    self.logger.warning(f"发现 {invalid_mask.sum()} 个无效的{col}值")
                    # 使用前向填充处理无效值
                    data.loc[invalid_mask, col] = np.nan
        
        # 检查成交量异常
        if 'volume' in data.columns:
            # 成交量不能为负
            invalid_volume = data['volume'] < 0
            if invalid_volume.any():
                self.logger.warning(f"发现 {invalid_volume.sum()} 个无效的成交量值")
                data.loc[invalid_volume, 'volume'] = np.nan
        
        return data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            data: 数据
            
        Returns:
            pandas.DataFrame: 处理缺失值后的数据
        """
        self.logger.info("处理缺失值...")
        
        # 检查缺失值
        missing_counts = data.isnull().sum()
        if missing_counts.any():
            self.logger.info(f"缺失值统计:\n{missing_counts[missing_counts > 0]}")
        
        # 对于价格数据，使用前向填充，然后后向填充
        price_columns = ['open', 'high', 'low', 'close', 'adj_close']
        for col in price_columns:
            if col in data.columns:
                # 先前向填充
                data[col] = data[col].ffill()
                # 然后后向填充（处理开头缺失）
                data[col] = data[col].bfill()
        
        # 对于成交量，使用0填充或插值
        if 'volume' in data.columns:
            data['volume'] = data['volume'].fillna(0)
        
        # 对于技术指标，可能需要重新计算
        
        return data
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: 数据
            
        Returns:
            pandas.DataFrame: 添加技术指标后的数据
        """
        self.logger.info("计算技术指标...")
        
        if 'close' not in data.columns:
            self.logger.warning("没有收盘价数据，跳过技术指标计算")
            return data
        
        close_prices = data['close']
        
        # 1. 移动平均线
        data['sma_10'] = close_prices.rolling(window=10).mean()
        data['sma_20'] = close_prices.rolling(window=20).mean()
        data['sma_50'] = close_prices.rolling(window=50).mean()
        data['sma_200'] = close_prices.rolling(window=200).mean()
        
        # 2. 指数移动平均线
        data['ema_12'] = close_prices.ewm(span=12, adjust=False).mean()
        data['ema_26'] = close_prices.ewm(span=26, adjust=False).mean()
        
        # 3. 布林带
        sma_20 = data['sma_20']
        rolling_std = close_prices.rolling(window=20).std()
        data['bb_upper'] = sma_20 + (rolling_std * 2)
        data['bb_lower'] = sma_20 - (rolling_std * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / sma_20
        
        # 4. RSI (相对强弱指数)
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # 5. MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # 6. 成交量指标
        if 'volume' in data.columns:
            data['volume_sma'] = data['volume'].rolling(window=20).mean()
            data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        # 7. 波动率
        data['volatility'] = close_prices.pct_change().rolling(window=20).std() * np.sqrt(252)
        
        # 8. ATR (平均真实波幅)
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        data['atr'] = true_range.rolling(window=14).mean()
        
        return data
    
    def _calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算收益率
        
        Args:
            data: 数据
            
        Returns:
            pandas.DataFrame: 添加收益率后的数据
        """
        self.logger.info("计算收益率...")
        
        if 'close' not in data.columns:
            return data
        
        close_prices = data['close']
        
        # 日收益率
        data['daily_return'] = close_prices.pct_change()
        
        # 对数收益率
        data['log_return'] = np.log(close_prices / close_prices.shift(1))
        
        # 累计收益率
        data['cumulative_return'] = (1 + data['daily_return']).cumprod() - 1
        
        # 滚动收益率（20日）
        data['rolling_return_20'] = close_prices.pct_change(20)
        
        return data
    
    def _add_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        添加时间特征
        
        Args:
            data: 数据
            
        Returns:
            pandas.DataFrame: 添加时间特征后的数据
        """
        self.logger.info("添加时间特征...")
        
        if not isinstance(data.index, pd.DatetimeIndex):
            return data
        
        # 日期特征
        data['year'] = data.index.year
        data['month'] = data.index.month
        data['day'] = data.index.day
        data['dayofweek'] = data.index.dayofweek  # 周一=0, 周日=6
        data['dayofyear'] = data.index.dayofyear
        data['weekofyear'] = data.index.isocalendar().week
        data['quarter'] = data.index.quarter
        
        # 是否为月初/月末
        data['is_month_start'] = data.index.is_month_start.astype(int)
        data['is_month_end'] = data.index.is_month_end.astype(int)
        data['is_quarter_start'] = data.index.is_quarter_start.astype(int)
        data['is_quarter_end'] = data.index.is_quarter_end.astype(int)
        data['is_year_start'] = data.index.is_year_start.astype(int)
        data['is_year_end'] = data.index.is_year_end.astype(int)
        
        # 季节特征
        data['season'] = data['month'] % 12 // 3 + 1
        
        # 是否为周末
        data['is_weekend'] = (data['dayofweek'] >= 5).astype(int)
        
        # 月份正弦/余弦编码（处理周期性）
        data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
        data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)
        
        # 星期正弦/余弦编码
        data['week_sin'] = np.sin(2 * np.pi * data['dayofweek'] / 7)
        data['week_cos'] = np.cos(2 * np.pi * data['dayofweek'] / 7)
        
        return data
    
    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        数据标准化
        
        Args:
            data: 数据
            
        Returns:
            pandas.DataFrame: 标准化后的数据
        """
        self.logger.info("数据标准化...")
        
        # 选择需要标准化的列
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        # 排除不需要标准化的列（如收益率、技术指标等）
        exclude_columns = ['daily_return', 'log_return', 'cumulative_return', 
                          'rsi', 'macd', 'macd_signal', 'macd_histogram']
        
        columns_to_normalize = [col for col in numeric_columns 
                               if col not in exclude_columns]
        
        # 标准化（z-score）
        for col in columns_to_normalize:
            mean = data[col].mean()
            std = data[col].std()
            if std > 0:  # 避免除零
                data[f'{col}_normalized'] = (data[col] - mean) / std
        
        return data
    
    def get_feature_importance(self, data: pd.DataFrame, target_column='daily_return'):
        """
        获取特征重要性（基于相关性）
        
        Args:
            data: 数据
            target_column: 目标列
            
        Returns:
            pandas.Series: 特征相关性
        """
        if target_column not in data.columns:
            self.logger.warning(f"目标列 {target_column} 不存在")
            return pd.Series()
        
        # 计算与目标的相关性
        numeric_data = data.select_dtypes(include=[np.number])
        correlations = numeric_data.corr()[target_column].abs().sort_values(ascending=False)
        
        # 移除目标列自身
        correlations = correlations.drop(target_column, errors='ignore')
        
        return correlations
    
    def create_lagged_features(self, data: pd.DataFrame, columns=None, lags=[1, 2, 3, 5, 10]):
        """
        创建滞后特征
        
        Args:
            data: 数据
            columns: 需要创建滞后特征的列
            lags: 滞后周期列表
            
        Returns:
            pandas.DataFrame: 添加滞后特征后的数据
        """
        if columns is None:
            columns = ['close', 'volume', 'daily_return']
        
        lagged_data = data.copy()
        
        for col in columns:
            if col in lagged_data.columns:
                for lag in lags:
                    lagged_data[f'{col}_lag_{lag}'] = lagged_data[col].shift(lag)
        
        return lagged_data