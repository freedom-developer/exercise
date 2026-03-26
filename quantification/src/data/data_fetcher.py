"""
数据获取器
负责从不同数据源获取数据
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
import time
from typing import Optional, Dict, Any

class DataFetcher:
    """数据获取器"""
    
    def __init__(self, config):
        """
        初始化数据获取器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 数据源配置
        self.data_sources = config.get('data_sources', {})
        
        # 请求限制
        self.request_count = 0
        self.last_request_time = time.time()
        
        self.logger.info("数据获取器初始化完成")
    
    def fetch_data(self, symbol, start_date, end_date, source='yahoo_finance'):
        """
        从指定数据源获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            source: 数据源名称
            
        Returns:
            pandas.DataFrame: 数据
        """
        source_config = self.data_sources.get(source, {})
        
        if not source_config.get('enabled', False):
            self.logger.warning(f"数据源 {source} 未启用")
            return pd.DataFrame()
        
        self._check_rate_limit(source_config)
        
        try:
            if source == 'yahoo_finance':
                data = self._fetch_from_yahoo(symbol, start_date, end_date)
            elif source == 'alpha_vantage':
                data = self._fetch_from_alpha_vantage(symbol, start_date, end_date)
            elif source == 'database':
                data = self._fetch_from_database(symbol, start_date, end_date)
            else:
                self.logger.error(f"不支持的数据源: {source}")
                return pd.DataFrame()
            
            self.request_count += 1
            self.last_request_time = time.time()
            
            return data
            
        except Exception as e:
            self.logger.error(f"获取数据失败 ({source}): {e}")
            return pd.DataFrame()
    
    def _fetch_from_yahoo(self, symbol, start_date, end_date):
        """
        从Yahoo Finance获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            pandas.DataFrame: 数据
        """
        self.logger.info(f"从Yahoo Finance获取 {symbol} 数据")
        
        try:
            ticker = yf.Ticker(symbol)
            
            # 获取历史数据
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval='1d',
                actions=True  # 包含分红和拆股信息
            )
            
            if data.empty:
                self.logger.warning(f"Yahoo Finance返回空数据: {symbol}")
                return pd.DataFrame()
            
            # 重命名列以保持一致性
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Dividends': 'dividend',
                'Stock Splits': 'split'
            })
            
            # 添加调整收盘价
            if 'Adj Close' in data.columns:
                data = data.rename(columns={'Adj Close': 'adj_close'})
            else:
                # 如果没有调整收盘价，使用收盘价
                data['adj_close'] = data['close']
            
            # 添加股票代码
            data['symbol'] = symbol
            
            self.logger.info(f"从Yahoo Finance获取到 {len(data)} 条 {symbol} 数据")
            return data
            
        except Exception as e:
            self.logger.error(f"Yahoo Finance获取失败: {e}")
            return pd.DataFrame()
    
    def _fetch_from_alpha_vantage(self, symbol, start_date, end_date):
        """
        从Alpha Vantage获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            pandas.DataFrame: 数据
        """
        self.logger.info(f"从Alpha Vantage获取 {symbol} 数据")
        
        # 这里需要Alpha Vantage API密钥
        api_key = self.data_sources['alpha_vantage'].get('api_key')
        
        if not api_key or api_key == 'YOUR_API_KEY':
            self.logger.error("请配置Alpha Vantage API密钥")
            return pd.DataFrame()
        
        try:
            # 这里实现Alpha Vantage API调用
            # 由于API限制，这里只返回空DataFrame
            # 实际使用时需要安装alpha_vantage包并实现具体逻辑
            
            self.logger.warning("Alpha Vantage数据源暂未实现")
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage获取失败: {e}")
            return pd.DataFrame()
    
    def _fetch_from_database(self, symbol, start_date, end_date):
        """
        从数据库获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            pandas.DataFrame: 数据
        """
        self.logger.info(f"从数据库获取 {symbol} 数据")
        
        # 这里需要数据库连接配置
        db_config = self.data_sources['database']
        
        try:
            # 这里实现数据库查询
            # 实际使用时需要根据数据库类型实现具体逻辑
            
            self.logger.warning("数据库数据源暂未实现")
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"数据库获取失败: {e}")
            return pd.DataFrame()
    
    def _check_rate_limit(self, source_config):
        """
        检查请求频率限制
        
        Args:
            source_config: 数据源配置
        """
        rate_limit = source_config.get('rate_limit', 5)  # 默认每分钟5次
        
        if rate_limit <= 0:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_request_time
        
        # 如果距离上次请求不到1分钟，且请求次数超过限制，则等待
        if time_diff < 60 and self.request_count >= rate_limit:
            wait_time = 60 - time_diff
            self.logger.info(f"达到请求频率限制，等待 {wait_time:.1f} 秒")
            time.sleep(wait_time)
            self.request_count = 0
    
    def get_available_intervals(self):
        """
        获取可用的数据频率
        
        Returns:
            list: 频率列表
        """
        return ['1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo']
    
    def get_market_status(self):
        """
        获取市场状态
        
        Returns:
            dict: 市场状态信息
        """
        # 这里可以扩展为获取实时市场状态
        # 例如：开市时间、休市日等
        
        return {
            'status': 'unknown',
            'message': '市场状态检查未实现'
        }