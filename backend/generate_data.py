"""
生成示例数据的脚本
用于为系统提供测试数据
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加后端路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import TimeSeriesProcessor

def generate_all_sample_data():
    """生成所有类型的示例数据"""
    
    # 创建数据目录
    data_dir = "../data/samples"
    os.makedirs(data_dir, exist_ok=True)
    
    processor = TimeSeriesProcessor()
    
    # 生成天气数据
    print("生成天气数据...")
    weather_data = processor.generate_sample_data(
        data_type='weather',
        num_samples=2000,
        save_path=os.path.join(data_dir, 'weather_sample.csv')
    )
    print(f"天气数据生成完成: {weather_data.shape}")
    
    # 生成电力数据
    print("生成电力数据...")
    electricity_data = processor.generate_sample_data(
        data_type='electricity', 
        num_samples=2000,
        save_path=os.path.join(data_dir, 'electricity_sample.csv')
    )
    print(f"电力数据生成完成: {electricity_data.shape}")
    
    # 生成交通数据
    print("生成交通数据...")
    traffic_data = processor.generate_sample_data(
        data_type='traffic',
        num_samples=2000, 
        save_path=os.path.join(data_dir, 'traffic_sample.csv')
    )
    print(f"交通数据生成完成: {traffic_data.shape}")
    
    # 生成可视化图
    print("生成数据可视化图...")
    
    # 天气数据可视化
    weather_fig = processor.visualize_data(
        weather_data, 
        'temperature',
        save_path=os.path.join(data_dir, 'weather_visualization.png')
    )
    
    # 电力数据可视化
    electricity_fig = processor.visualize_data(
        electricity_data,
        'load', 
        save_path=os.path.join(data_dir, 'electricity_visualization.png')
    )
    
    # 交通数据可视化
    traffic_fig = processor.visualize_data(
        traffic_data,
        'flow',
        save_path=os.path.join(data_dir, 'traffic_visualization.png')
    )
    
    print("所有示例数据生成完成！")
    print(f"数据保存位置: {os.path.abspath(data_dir)}")

def generate_test_sequences():
    """生成用于测试的小规模数据"""
    
    test_dir = "../data/test"
    os.makedirs(test_dir, exist_ok=True)
    
    # 生成小规模测试数据
    np.random.seed(42)
    
    # 简单趋势数据
    dates = pd.date_range('2023-01-01', periods=100, freq='H')
    trend = np.linspace(10, 20, 100)
    noise = np.random.normal(0, 0.5, 100)
    values = trend + noise
    
    test_df = pd.DataFrame({
        'datetime': dates,
        'value': values
    })
    
    test_df.to_csv(os.path.join(test_dir, 'simple_trend.csv'), index=False)
    
    # 周期性数据
    seasonal = 5 * np.sin(2 * np.pi * np.arange(100) / 24)  # 24小时周期
    seasonal_values = 15 + seasonal + np.random.normal(0, 0.3, 100)
    
    seasonal_df = pd.DataFrame({
        'datetime': dates,
        'value': seasonal_values
    })
    
    seasonal_df.to_csv(os.path.join(test_dir, 'seasonal_pattern.csv'), index=False)
    
    print("测试数据生成完成！")

if __name__ == '__main__':
    print("开始生成示例数据...")
    generate_all_sample_data()
    generate_test_sequences()
    print("数据生成脚本执行完成！")
