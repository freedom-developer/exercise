"""
数据管理器
负责数据的获取、处理和缓存
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path
import pickle
import hashlib

from .data_fetcher import DataFetcher
from .data_processor import DataProcessor

class DataManager:
    """数据管理器"""
    
    def __init__(self, config):
        """
        初始化数据管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.fetcher = DataFetcher(config)
        self.processor = DataProcessor(config)
        
        # 缓存配置
        self.cache_enabled = config.get('cache', {}).get('enabled', True)
        self.cache_dir = Path(config.get('cache', {}).get('directory', 'data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("数据管理器初始化完成")
    
    def get_data(self, symbol, start_date, end_date, force_refresh=False):
        """
        获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            force_refresh: 是否强制刷新缓存
            
        Returns:
            pandas.DataFrame: 数据
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(symbol, start_date, end_date)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # 检查缓存
        if not force_refresh and self.cache_enabled and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            cache_ttl = timedelta(days=self.config.get('cache', {}).get('ttl_days', 7))
            
            if cache_age < cache_ttl:
                self.logger.info(f"从缓存加载数据: {symbol}")
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    return data
                except Exception as e:
                    self.logger.warning(f"缓存加载失败: {e}")
        
        # 从数据源获取数据
        self.logger.info(f"从数据源获取数据: {symbol}")
        data = self.fetcher.fetch_data(symbol, start_date, end_date)
        
        if data.empty:
            self.logger.error(f"无法获取 {symbol} 的数据")
            return pd.DataFrame()
        
        # 处理数据
        data = self.processor.process(data)
        
        # 保存到缓存
        if self.cache_enabled:
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
                self.logger.info(f"数据已缓存: {cache_file}")
            except Exception as e:
                self.logger.warning(f"缓存保存失败: {e}")
        
        return data
    
    def get_multiple_data(self, symbols, start_date, end_date):
        """
        获取多个标的的数据
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 每个标的的数据字典
        """
        data_dict = {}
        
        for symbol in symbols:
            self.logger.info(f"获取 {symbol} 数据...")
            data = self.get_data(symbol, start_date, end_date)
            if not data.empty:
                data_dict[symbol] = data
            else:
                self.logger.warning(f"跳过 {symbol}，数据获取失败")
        
        return data_dict
    
    def update_data(self, symbol, end_date=None):
        """
        更新数据到最新
        
        Args:
            symbol: 股票代码
            end_date: 结束日期，默认为今天
            
        Returns:
            pandas.DataFrame: 更新后的数据
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 获取缓存中的最新数据日期
        cache_files = list(self.cache_dir.glob(f"{symbol}_*.pkl"))
        if cache_files:
            # 找到最新的缓存文件
            latest_cache = max(cache_files, key=lambda x: x.stat().st_mtime)
            
            # 从缓存加载数据
            with open(latest_cache, 'rb') as f:
                cached_data = pickle.load(f)
            
            # 获取缓存数据的最后日期
            last_date = cached_data.index[-1].strftime('%Y-%m-%d')
            
            # 如果缓存数据已经是最新的，直接返回
            if last_date >= end_date:
                self.logger.info(f"{symbol} 数据已是最新")
                return cached_data
            
            # 获取增量数据
            start_date = (cached_data.index[-1] + timedelta(days=1)).strftime('%Y-%m-%d')
            self.logger.info(f"获取增量数据: {symbol} ({start_date} 到 {end_date})")
            
            new_data = self.fetcher.fetch_data(symbol, start_date, end_date)
            
            if not new_data.empty:
                # 合并数据
                updated_data = pd.concat([cached_data, new_data])
                updated_data = self.processor.process(updated_data)
                
                # 更新缓存
                cache_key = self._generate_cache_key(symbol, updated_data.index[0].strftime('%Y-%m-%d'), end_date)
                cache_file = self.cache_dir / f"{cache_key}.pkl"
                
                with open(cache_file, 'wb') as f:
                    pickle.dump(updated_data, f)
                
                return updated_data
        
        # 如果没有缓存或更新失败，重新获取全部数据
        self.logger.info(f"重新获取全部数据: {symbol}")
        return self.get_data(symbol, '2000-01-01', end_date)
    
    def _generate_cache_key(self, symbol, start_date, end_date):
        """
        生成缓存键
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            str: 缓存键
        """
        key_str = f"{symbol}_{start_date}_{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_available_symbols(self):
        """
        获取可用的股票代码列表
        
        Returns:
            list: 股票代码列表
        """
        # 这里可以根据实际情况实现
        # 例如从配置文件、数据库或API获取
        return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META']
    
    def cleanup_cache(self, days_old=30):
        """
        清理旧的缓存文件
        
        Args:
            days_old: 清理多少天前的缓存
        """
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        cache_files = list(self.cache_dir.glob("*.pkl"))
        deleted_count = 0
        
        for cache_file in cache_files:
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    self.logger.warning(f"删除缓存文件失败 {cache_file}: {e}")
        
        self.logger.info(f"清理了 {deleted_count} 个缓存文件")