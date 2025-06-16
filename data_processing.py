"""
时间序列数据处理脚本
用于处理天气数据和用电量数据，为模型训练做准备
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesDataProcessor:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.processed_dir = os.path.join(data_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
        
    def analyze_weather_data(self):
        """分析天气数据"""
        print("=" * 60)
        print("开始分析天气数据...")
        print("=" * 60)
        
        # 读取数据
        df = pd.read_csv(os.path.join(self.data_dir, 'weather.csv'))
        print(f"原始数据形状: {df.shape}")
        
        # 转换日期列
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 基本信息
        print(f"\n数据时间范围: {df.index.min()} 到 {df.index.max()}")
        print(f"数据频率: 每10分钟一个记录")
        print(f"总时长: {(df.index.max() - df.index.min()).days} 天")
        
        # 检查缺失值
        missing_info = df.isnull().sum()
        print(f"\n缺失值统计:")
        for col, missing_count in missing_info.items():
            if missing_count > 0:
                print(f"  {col}: {missing_count} ({missing_count/len(df)*100:.2f}%)")
        
        # 主要特征统计
        print(f"\n主要特征统计:")
        key_features = ['T (degC)', 'rh (%)', 'wv (m/s)', 'rain (mm)', 'SWDR (W/m²)']
        available_features = [f for f in key_features if f in df.columns]
        
        if not available_features:
            # 如果没有找到完全匹配的列名，显示所有数值列
            available_features = df.select_dtypes(include=[np.number]).columns[:10].tolist()
        
        print(df[available_features].describe())
        
        # 处理数据
        processed_df = self._process_weather_data(df)
        
        # 保存处理后的数据
        output_path = os.path.join(self.processed_dir, 'weather_processed.csv')
        processed_df.to_csv(output_path)
        print(f"\n处理后的天气数据已保存到: {output_path}")
        
        # 生成简化版用于演示
        demo_df = processed_df.resample('1H').mean().dropna()  # 转为小时数据
        demo_path = os.path.join(self.processed_dir, 'weather_demo.csv')
        demo_df.to_csv(demo_path)
        print(f"演示用天气数据已保存到: {demo_path}")
        
        return processed_df, demo_df
    
    def analyze_electricity_data(self, sample_size=100000):
        """分析用电量数据（采样处理大文件）"""
        print("=" * 60)
        print("开始分析用电量数据...")
        print("=" * 60)
        
        # 由于文件较大，先读取前几行了解结构
        sample_df = pd.read_csv(os.path.join(self.data_dir, 'electricity.csv'), nrows=10)
        print(f"数据列: {sample_df.columns.tolist()}")
        print(f"样本数据:\n{sample_df.head()}")
        
        # 读取采样数据进行分析
        print(f"\n读取前 {sample_size} 行数据进行分析...")
        df = pd.read_csv(os.path.join(self.data_dir, 'electricity.csv'), nrows=sample_size)
        print(f"采样数据形状: {df.shape}")
        
        # 检查是否有时间列
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp'])]
        if date_columns:
            print(f"发现时间列: {date_columns}")
            # 尝试转换第一个时间列
            try:
                df[date_columns[0]] = pd.to_datetime(df[date_columns[0]])
                df = df.set_index(date_columns[0])
                print(f"成功设置时间索引: {date_columns[0]}")
            except:
                print(f"无法解析时间列 {date_columns[0]}，将使用数值索引")
        
        # 数值列分析
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        print(f"\n数值列: {numeric_columns.tolist()}")
        
        if len(numeric_columns) > 0:
            print(f"\n数值特征统计:")
            print(df[numeric_columns].describe())
            
            # 处理数据
            processed_df = self._process_electricity_data(df)
            
            # 保存处理后的数据
            output_path = os.path.join(self.processed_dir, 'electricity_processed.csv')
            processed_df.to_csv(output_path)
            print(f"\n处理后的用电量数据已保存到: {output_path}")
            
            # 生成小样本用于演示
            demo_df = processed_df.head(10000)  # 取前10000行
            demo_path = os.path.join(self.processed_dir, 'electricity_demo.csv')
            demo_df.to_csv(demo_path)
            print(f"演示用用电量数据已保存到: {demo_path}")
            
            return processed_df, demo_df
        else:
            print("未发现数值列，请检查数据格式")
            return None, None
    
    def _process_weather_data(self, df):
        """处理天气数据"""
        print("\n处理天气数据...")
        
        # 删除包含特殊字符的列（如果有的话）
        problematic_cols = [col for col in df.columns if any(char in col for char in ['�', '°'])]
        if problematic_cols:
            print(f"删除包含特殊字符的列: {problematic_cols}")
            df = df.drop(columns=problematic_cols)
        
        # 选择主要的数值特征
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 保留前10个最重要的数值特征
        if len(numeric_cols) > 10:
            numeric_cols = numeric_cols[:10]
        
        df_processed = df[numeric_cols].copy()
        
        # 处理缺失值
        df_processed = df_processed.fillna(method='forward').fillna(method='backward')
        
        # 异常值处理（使用IQR方法）
        for col in numeric_cols:
            Q1 = df_processed[col].quantile(0.25)
            Q3 = df_processed[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 将异常值替换为边界值
            df_processed[col] = df_processed[col].clip(lower_bound, upper_bound)
        
        print(f"处理完成，保留 {len(numeric_cols)} 个特征: {numeric_cols}")
        return df_processed
    
    def _process_electricity_data(self, df):
        """处理用电量数据"""
        print("\n处理用电量数据...")
        
        # 选择数值特征
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 如果列太多，选择前20个
        if len(numeric_cols) > 20:
            numeric_cols = numeric_cols[:20]
        
        df_processed = df[numeric_cols].copy()
        
        # 处理缺失值
        df_processed = df_processed.fillna(method='forward').fillna(method='backward')
        
        # 异常值处理
        for col in numeric_cols:
            Q1 = df_processed[col].quantile(0.25)
            Q3 = df_processed[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            df_processed[col] = df_processed[col].clip(lower_bound, upper_bound)
        
        print(f"处理完成，保留 {len(numeric_cols)} 个特征: {numeric_cols}")
        return df_processed
    
    def create_training_datasets(self):
        """创建训练数据集"""
        print("=" * 60)
        print("创建训练数据集...")
        print("=" * 60)
        
        datasets_info = []
        
        # 处理天气数据
        try:
            weather_df, weather_demo = self.analyze_weather_data()
            
            # 为天气数据创建目标变量（以温度为预测目标）
            temp_col = None
            for col in weather_df.columns:
                if 'T' in col and 'deg' in col:
                    temp_col = col
                    break
            
            if temp_col is None:
                # 如果没找到温度列，使用第一个数值列
                temp_col = weather_df.columns[0]
            
            # 创建训练数据集
            weather_train = self._create_univariate_dataset(weather_df, temp_col, 'weather_temperature')
            datasets_info.append({
                'name': 'weather_temperature',
                'description': f'天气数据-{temp_col}预测',
                'target_column': temp_col,
                'samples': len(weather_train),
                'features': weather_df.shape[1]
            })
            
        except Exception as e:
            print(f"处理天气数据时出错: {e}")
        
        # 处理用电量数据
        try:
            elec_df, elec_demo = self.analyze_electricity_data()
            
            if elec_df is not None:
                # 选择第一个数值列作为预测目标
                target_col = elec_df.columns[0]
                
                # 创建训练数据集
                elec_train = self._create_univariate_dataset(elec_df, target_col, 'electricity_consumption')
                datasets_info.append({
                    'name': 'electricity_consumption',
                    'description': f'用电量数据-{target_col}预测',
                    'target_column': target_col,
                    'samples': len(elec_train),
                    'features': elec_df.shape[1]
                })
                
        except Exception as e:
            print(f"处理用电量数据时出错: {e}")
        
        # 保存数据集信息
        import json
        info_path = os.path.join(self.processed_dir, 'datasets_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(datasets_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n数据集信息已保存到: {info_path}")
        print("\n可用的训练数据集:")
        for info in datasets_info:
            print(f"  - {info['name']}: {info['description']}")
            print(f"    目标列: {info['target_column']}")
            print(f"    样本数: {info['samples']}")
            print(f"    特征数: {info['features']}")
        
        return datasets_info
    
    def _create_univariate_dataset(self, df, target_col, dataset_name):
        """创建单变量时间序列数据集"""
        # 确保目标列存在
        if target_col not in df.columns:
            target_col = df.columns[0]
        
        # 创建简化的数据集，只包含时间索引和目标变量
        dataset = pd.DataFrame({
            'timestamp': df.index,
            'value': df[target_col].values
        })
        
        # 重新设置索引
        dataset = dataset.reset_index(drop=True)
        
        # 保存数据集
        output_path = os.path.join(self.processed_dir, f'{dataset_name}.csv')
        dataset.to_csv(output_path, index=False)
        print(f"训练数据集已保存: {output_path}")
        
        return dataset
    
    def generate_visualization_report(self):
        """生成数据可视化报告"""
        print("=" * 60)
        print("生成数据可视化报告...")
        print("=" * 60)
        
        import matplotlib.pyplot as plt
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('TimeVis 数据集分析报告', fontsize=16)
        
        # 天气数据可视化
        try:
            weather_demo_path = os.path.join(self.processed_dir, 'weather_demo.csv')
            if os.path.exists(weather_demo_path):
                weather_df = pd.read_csv(weather_demo_path, index_col=0, parse_dates=True)
                
                # 选择第一个数值列进行可视化
                target_col = weather_df.columns[0]
                axes[0, 0].plot(weather_df.index[:1000], weather_df[target_col][:1000])
                axes[0, 0].set_title(f'天气数据 - {target_col}')
                axes[0, 0].set_xlabel('时间')
                axes[0, 0].set_ylabel(target_col)
                axes[0, 0].tick_params(axis='x', rotation=45)
                
                # 分布图
                axes[0, 1].hist(weather_df[target_col].dropna(), bins=50, alpha=0.7)
                axes[0, 1].set_title(f'{target_col} 分布')
                axes[0, 1].set_xlabel(target_col)
                axes[0, 1].set_ylabel('频次')
        except Exception as e:
            print(f"天气数据可视化失败: {e}")
        
        # 用电量数据可视化
        try:
            elec_demo_path = os.path.join(self.processed_dir, 'electricity_demo.csv')
            if os.path.exists(elec_demo_path):
                elec_df = pd.read_csv(elec_demo_path, index_col=0, parse_dates=True)
                
                # 选择第一个数值列进行可视化
                target_col = elec_df.columns[0]
                axes[1, 0].plot(elec_df.index[:1000], elec_df[target_col][:1000])
                axes[1, 0].set_title(f'用电量数据 - {target_col}')
                axes[1, 0].set_xlabel('时间')
                axes[1, 0].set_ylabel(target_col)
                axes[1, 0].tick_params(axis='x', rotation=45)
                
                # 分布图
                axes[1, 1].hist(elec_df[target_col].dropna(), bins=50, alpha=0.7)
                axes[1, 1].set_title(f'{target_col} 分布')
                axes[1, 1].set_xlabel(target_col)
                axes[1, 1].set_ylabel('频次')
        except Exception as e:
            print(f"用电量数据可视化失败: {e}")
        
        plt.tight_layout()
        
        # 保存图片
        report_path = os.path.join(self.processed_dir, 'data_analysis_report.png')
        plt.savefig(report_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"数据分析报告已保存: {report_path}")

def main():
    """主函数"""
    print("TimeVis 数据处理工具")
    print("作者: TimeVis Team")
    print("功能: 处理天气和用电量时间序列数据")
    print("=" * 60)
    
    # 创建处理器
    processor = TimeSeriesDataProcessor()
    
    # 创建训练数据集
    datasets_info = processor.create_training_datasets()
    
    # 生成可视化报告
    processor.generate_visualization_report()
    
    print("\n" + "=" * 60)
    print("数据处理完成！")
    print("=" * 60)
    print("\n处理结果:")
    print(f"- 处理后的数据保存在: data/processed/")
    print(f"- 数据集信息: data/processed/datasets_info.json")
    print(f"- 可视化报告: data/processed/data_analysis_report.png")
    
    print("\n下一步:")
    print("1. 查看处理后的数据文件")
    print("2. 使用 python model_training.py 开始模型训练")
    print("3. 启动Web应用: python backend/app.py")

if __name__ == "__main__":
    main()
