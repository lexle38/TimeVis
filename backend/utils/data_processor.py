import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict, List, Optional, Union
import os
import json
from datetime import datetime, timedelta
from loguru import logger

class TimeSeriesProcessor:
    """时间序列数据处理工具"""
    
    def __init__(self):
        self.scaler = None
        self.data_info = {}
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """加载数据文件"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_path}")
            
            logger.info(f"数据加载成功: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            raise
    
    def analyze_data(self, df: pd.DataFrame) -> Dict:
        """分析数据基本信息"""
        analysis = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'statistics': df.describe().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        # 检测时间列
        datetime_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col])
                    datetime_columns.append(col)
                except:
                    pass
        
        analysis['datetime_columns'] = datetime_columns
        
        # 检测数值列
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        analysis['numeric_columns'] = numeric_columns
        
        self.data_info = analysis
        logger.info(f"数据分析完成: {analysis['shape'][0]} 行, {analysis['shape'][1]} 列")
        
        return analysis
    
    def clean_data(self, df: pd.DataFrame, 
                   remove_duplicates: bool = True,
                   fill_missing: str = 'forward',
                   remove_outliers: bool = False,
                   outlier_method: str = 'iqr') -> pd.DataFrame:
        """数据清洗"""
        df_cleaned = df.copy()
        
        logger.info("开始数据清洗...")
        
        # 移除重复行
        if remove_duplicates:
            before = len(df_cleaned)
            df_cleaned = df_cleaned.drop_duplicates()
            after = len(df_cleaned)
            if before != after:
                logger.info(f"移除了 {before - after} 个重复行")
        
        # 处理缺失值
        if fill_missing == 'forward':
            df_cleaned = df_cleaned.fillna(method='ffill')
        elif fill_missing == 'backward':
            df_cleaned = df_cleaned.fillna(method='bfill')
        elif fill_missing == 'mean':
            for col in df_cleaned.select_dtypes(include=[np.number]).columns:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
        elif fill_missing == 'median':
            for col in df_cleaned.select_dtypes(include=[np.number]).columns:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
        elif fill_missing == 'drop':
            df_cleaned = df_cleaned.dropna()
        
        # 移除异常值
        if remove_outliers:
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if outlier_method == 'iqr':
                    Q1 = df_cleaned[col].quantile(0.25)
                    Q3 = df_cleaned[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
                    df_cleaned = df_cleaned[~outliers]
                    
                elif outlier_method == 'zscore':
                    z_scores = np.abs((df_cleaned[col] - df_cleaned[col].mean()) / df_cleaned[col].std())
                    df_cleaned = df_cleaned[z_scores < 3]
        
        logger.info(f"数据清洗完成，最终数据形状: {df_cleaned.shape}")
        return df_cleaned
    
    def normalize_data(self, df: pd.DataFrame, method: str = 'minmax',
                      target_column: Optional[str] = None) -> Tuple[pd.DataFrame, object]:
        """数据归一化"""
        df_normalized = df.copy()
        
        # 选择归一化方法
        if method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'standard':
            scaler = StandardScaler()
        else:
            raise ValueError(f"不支持的归一化方法: {method}")
        
        # 确定要归一化的列
        if target_column:
            columns_to_scale = [target_column]
        else:
            columns_to_scale = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 应用归一化
        df_normalized[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
        
        self.scaler = scaler
        logger.info(f"数据归一化完成，使用方法: {method}")
        
        return df_normalized, scaler
    
    def create_sequences(self, data: pd.DataFrame, 
                        target_column: str,
                        sequence_length: int = 10,
                        prediction_horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """创建时间序列序列"""
        
        if target_column not in data.columns:
            raise ValueError(f"目标列 '{target_column}' 不存在于数据中")
        
        values = data[target_column].values
        
        X, y = [], []
        
        for i in range(len(values) - sequence_length - prediction_horizon + 1):
            # 输入序列
            X.append(values[i:i + sequence_length])
            # 目标值
            if prediction_horizon == 1:
                y.append(values[i + sequence_length])
            else:
                y.append(values[i + sequence_length:i + sequence_length + prediction_horizon])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"创建序列完成: X形状 {X.shape}, y形状 {y.shape}")
        
        return X, y
    
    def split_data(self, X: np.ndarray, y: np.ndarray, 
                   train_ratio: float = 0.7, val_ratio: float = 0.15,
                   test_ratio: float = 0.15, random_state: int = 42) -> Tuple:
        """分割数据集"""
        
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("训练、验证和测试比例之和必须等于1")
        
        # 首先分割出训练集和临时集（验证+测试）
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=(val_ratio + test_ratio), random_state=random_state, shuffle=False
        )
        
        # 然后分割临时集为验证集和测试集
        val_size = val_ratio / (val_ratio + test_ratio)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=(1 - val_size), random_state=random_state, shuffle=False
        )
        
        logger.info(f"数据分割完成 - 训练: {X_train.shape[0]}, 验证: {X_val.shape[0]}, 测试: {X_test.shape[0]}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def generate_sample_data(self, data_type: str, num_samples: int = 1000, 
                           save_path: Optional[str] = None) -> pd.DataFrame:
        """生成示例数据"""
        
        np.random.seed(42)
        
        # 创建时间索引
        start_date = datetime(2020, 1, 1)
        dates = [start_date + timedelta(hours=i) for i in range(num_samples)]
        
        if data_type == 'weather':
            # 温度数据，带有季节性和随机噪声
            base_temp = 20
            seasonal = 10 * np.sin(2 * np.pi * np.arange(num_samples) / (24 * 365.25))  # 年度周期
            daily = 5 * np.sin(2 * np.pi * np.arange(num_samples) / 24)  # 日周期
            noise = np.random.normal(0, 2, num_samples)
            temperature = base_temp + seasonal + daily + noise
            
            df = pd.DataFrame({
                'datetime': dates,
                'temperature': temperature,
                'humidity': np.random.uniform(30, 90, num_samples),
                'pressure': np.random.uniform(990, 1030, num_samples)
            })
            
        elif data_type == 'electricity':
            # 电力负荷数据
            base_load = 1000
            # 工作日vs周末模式
            weekday_pattern = np.array([0.7, 0.6, 0.6, 0.7, 0.8, 1.0, 1.2, 1.0, 0.9, 0.8] * (num_samples // 10 + 1))[:num_samples]
            seasonal = 200 * np.sin(2 * np.pi * np.arange(num_samples) / (24 * 365.25))
            noise = np.random.normal(0, 50, num_samples)
            load = base_load * weekday_pattern + seasonal + noise
            
            df = pd.DataFrame({
                'datetime': dates,
                'load': np.maximum(load, 0),  # 确保负荷为正
                'voltage': np.random.uniform(220, 240, num_samples),
                'frequency': np.random.uniform(49.5, 50.5, num_samples)
            })
            
        elif data_type == 'traffic':
            # 交通流量数据
            base_flow = 500
            # 工作时间高峰
            hour_pattern = np.array([0.3, 0.2, 0.2, 0.3, 0.5, 0.8, 1.2, 1.5, 1.0, 0.8, 0.9, 1.0, 
                                   1.1, 1.0, 0.9, 1.0, 1.3, 1.5, 1.2, 0.8, 0.6, 0.5, 0.4, 0.3] * (num_samples // 24 + 1))[:num_samples]
            noise = np.random.normal(0, 30, num_samples)
            flow = base_flow * hour_pattern + noise
            
            df = pd.DataFrame({
                'datetime': dates,
                'flow': np.maximum(flow, 0),  # 确保流量为正
                'speed': np.random.uniform(20, 80, num_samples),
                'occupancy': np.random.uniform(0, 100, num_samples)
            })
            
        else:
            raise ValueError(f"不支持的数据类型: {data_type}")
        
        if save_path:
            df.to_csv(save_path, index=False)
            logger.info(f"示例数据已保存至: {save_path}")
        
        logger.info(f"生成{data_type}示例数据完成: {df.shape}")
        return df
    
    def visualize_data(self, df: pd.DataFrame, target_column: str, 
                      save_path: Optional[str] = None, figsize: Tuple[int, int] = (15, 10)):
        """数据可视化"""
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f'时间序列数据分析 - {target_column}', fontsize=16)
        
        # 时间序列图
        axes[0, 0].plot(df.index, df[target_column])
        axes[0, 0].set_title('时间序列')
        axes[0, 0].set_xlabel('时间')
        axes[0, 0].set_ylabel(target_column)
        axes[0, 0].grid(True)
        
        # 分布直方图
        axes[0, 1].hist(df[target_column], bins=30, alpha=0.7)
        axes[0, 1].set_title('数值分布')
        axes[0, 1].set_xlabel(target_column)
        axes[0, 1].set_ylabel('频次')
        axes[0, 1].grid(True)
        
        # 箱线图
        axes[1, 0].boxplot(df[target_column])
        axes[1, 0].set_title('箱线图')
        axes[1, 0].set_ylabel(target_column)
        axes[1, 0].grid(True)
        
        # 自相关图（简化版）
        if len(df) > 50:
            lags = min(50, len(df) // 4)
            autocorr = [df[target_column].autocorr(lag=i) for i in range(1, lags)]
            axes[1, 1].plot(range(1, lags), autocorr)
            axes[1, 1].set_title('自相关')
            axes[1, 1].set_xlabel('滞后')
            axes[1, 1].set_ylabel('自相关系数')
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"可视化图像已保存至: {save_path}")
        
        return fig
    
    def export_processed_data(self, df: pd.DataFrame, output_path: str):
        """导出处理后的数据"""
        df.to_csv(output_path, index=False)
        
        # 保存处理信息
        info_path = output_path.replace('.csv', '_info.json')
        with open(info_path, 'w') as f:
            json.dump(self.data_info, f, indent=2, default=str)
        
        logger.info(f"处理后数据已导出至: {output_path}")

# 数据验证工具
class DataValidator:
    """数据验证工具"""
    
    @staticmethod
    def validate_time_series(df: pd.DataFrame, target_column: str) -> Dict[str, bool]:
        """验证时间序列数据"""
        results = {}
        
        # 检查目标列是否存在
        results['target_column_exists'] = target_column in df.columns
        
        # 检查是否有数值数据
        results['has_numeric_data'] = df[target_column].dtype in [np.float64, np.int64] if target_column in df.columns else False
        
        # 检查缺失值比例
        if target_column in df.columns:
            missing_ratio = df[target_column].isnull().sum() / len(df)
            results['low_missing_ratio'] = missing_ratio < 0.1
        else:
            results['low_missing_ratio'] = False
        
        # 检查数据长度
        results['sufficient_length'] = len(df) >= 100
        
        # 检查是否有异常值
        if target_column in df.columns and results['has_numeric_data']:
            Q1 = df[target_column].quantile(0.25)
            Q3 = df[target_column].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[target_column] < (Q1 - 1.5 * IQR)) | 
                       (df[target_column] > (Q3 + 1.5 * IQR))).sum()
            results['reasonable_outliers'] = outliers / len(df) < 0.05
        else:
            results['reasonable_outliers'] = False
        
        return results
    
    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict:
        """检查数据质量"""
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values_per_column': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        }
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            quality_report['numeric_statistics'] = df[numeric_cols].describe().to_dict()
        
        return quality_report
