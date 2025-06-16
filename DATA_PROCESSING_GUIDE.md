# TimeVis 数据处理与模型微调指南

本文档详细介绍如何使用TimeVis系统进行数据处理、模型微调和系统运行。

## 📊 数据集概览

### 1. weather.csv (7MB)
- **描述**: 天气数据，包含气象观测指标
- **时间范围**: 2020年1月开始，每10分钟一个记录点
- **主要特征**: 温度、湿度、气压、风速、降雨量、太阳辐射等
- **数据质量**: 高质量气象观测数据，适合时间序列预测

### 2. electricity.csv (95MB)
- **描述**: 用电量数据，包含电力消耗相关指标
- **数据量**: 大规模时间序列数据
- **特征**: 多维度电力消耗指标
- **用途**: 电力负荷预测、能源管理

## 🚀 快速开始

### 第一步: 环境准备

```bash
# 1. 进入项目目录
cd d:\pycharm-project\TimeVis

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')"
python -c "import pandas; print(f'Pandas版本: {pandas.__version__}')"
```

### 第二步: 数据处理

```bash
# 运行数据处理脚本
python data_processing.py
```

**数据处理过程说明：**

1. **天气数据处理**:
   - 解析时间戳，设置时间索引
   - 清理包含特殊字符的列
   - 选择主要数值特征（温度、湿度、风速等）
   - 处理缺失值和异常值
   - 生成小时级汇总数据用于演示

2. **用电量数据处理**:
   - 采样处理大文件（避免内存溢出）
   - 自动检测时间列和数值特征
   - 数据清洗和异常值处理
   - 生成小样本数据用于快速测试

3. **输出文件**:
   - `data/processed/weather_processed.csv` - 处理后的完整天气数据
   - `data/processed/weather_demo.csv` - 演示用天气数据（小时级）
   - `data/processed/electricity_processed.csv` - 处理后的用电量数据
   - `data/processed/electricity_demo.csv` - 演示用用电量数据
   - `data/processed/datasets_info.json` - 数据集信息摘要
   - `data/processed/data_analysis_report.png` - 数据可视化报告

### 第三步: 模型微调

```bash
# 运行模型微调脚本
python model_training.py
```

**模型微调过程：**

#### LSTM模型微调
- **架构**: 多层LSTM + Dropout + 全连接层
- **默认参数**:
  - 序列长度: 60个时间步
  - 隐藏层大小: 128
  - LSTM层数: 2层
  - 学习率: 0.001
  - 批次大小: 32
  - 训练轮数: 100（含早停）

#### Transformer模型微调（模拟Qwen）
- **架构**: 编码器型Transformer
- **默认参数**:
  - 序列长度: 60个时间步
  - 隐藏层大小: 256
  - 注意力头数: 8
  - Transformer层数: 4
  - 学习率: 0.0001
  - 批次大小: 16

#### 训练特性
- **自动化流程**: 自动处理所有检测到的数据集
- **智能优化**: 
  - 学习率调度（ReduceLROnPlateau）
  - 早停机制（防止过拟合）
  - 梯度裁剪（Transformer模型）
- **评估指标**: MSE、MAE、R²分数
- **可视化**: 自动生成训练曲线和预测对比图

### 第四步: 启动Web应用

#### 后端启动
```bash
# 启动Redis服务（Windows）
# 请确保Redis已安装并启动

# 启动Celery工作进程
python backend/celery_worker.py

# 新开一个终端，启动Flask应用
python backend/app.py
```

#### 前端启动
```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

访问地址：http://localhost:3000

## 📈 结果分析

### 模型性能指标

**评估指标说明：**
- **MSE (均方误差)**: 越小越好，衡量预测值与真实值的平方差
- **MAE (平均绝对误差)**: 越小越好，衡量预测值与真实值的绝对差
- **R² (决定系数)**: 越接近1越好，衡量模型解释数据变异的能力

**预期性能：**
- 天气数据：R² > 0.85，适合温度预测
- 用电量数据：R² > 0.80，适合负荷预测

### 输出文件说明

#### 训练结果文件
- `results/lstm_[dataset]_[timestamp].json` - LSTM训练结果
- `results/transformer_[dataset]_[timestamp].json` - Transformer训练结果
- `results/lstm_[dataset]_[timestamp].png` - LSTM可视化结果
- `results/model_comparison_[timestamp].csv` - 模型对比报告

#### 模型文件
- `models/lstm_[dataset]_best.pth` - 最佳LSTM模型
- `models/transformer_[dataset]_best.pth` - 最佳Transformer模型

## 🔧 高级配置

### 自定义超参数

可以修改`model_training.py`中的默认参数：

```python
# LSTM超参数
lstm_params = {
    'sequence_length': 120,    # 增加序列长度
    'hidden_size': 256,        # 增加隐藏层大小
    'num_layers': 3,           # 增加层数
    'learning_rate': 0.0005,   # 调整学习率
    'batch_size': 64,          # 增加批次大小
    'epochs': 200              # 增加训练轮数
}

# Transformer超参数
transformer_params = {
    'sequence_length': 120,
    'hidden_size': 512,        # 增加模型容量
    'num_heads': 16,           # 增加注意力头
    'num_layers': 6,           # 增加层数
    'learning_rate': 0.00005,  # 降低学习率
    'batch_size': 8            # 减小批次（GPU内存限制）
}
```

### GPU加速配置

如果有NVIDIA GPU：

```bash
# 检查CUDA可用性
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU数量: {torch.cuda.device_count()}')"

# 如果CUDA不可用，安装GPU版本PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 数据预处理自定义

修改`data_processing.py`中的处理逻辑：

```python
# 自定义特征选择
def custom_feature_selection(df):
    # 对于天气数据，选择特定特征
    weather_features = ['T (degC)', 'rh (%)', 'wv (m/s)', 'rain (mm)']
    available_features = [f for f in weather_features if f in df.columns]
    return df[available_features]

# 自定义时间窗口
def create_custom_sequences(data, lookback=90, horizon=7):
    # lookback: 历史窗口长度
    # horizon: 预测步长
    pass
```

## 🐛 常见问题

### 1. 内存不足
**问题**: 处理大文件时内存溢出
**解决**: 
```python
# 在data_processing.py中调整采样大小
processor = TimeSeriesDataProcessor()
# 减少采样大小
elec_df, elec_demo = processor.analyze_electricity_data(sample_size=50000)
```

### 2. GPU内存不足
**问题**: 训练Transformer时GPU内存不足
**解决**:
```python
# 减小批次大小
transformer_params = {
    'batch_size': 4,  # 从16减到4
    'hidden_size': 128,  # 减小模型大小
}
```

### 3. 收敛缓慢
**问题**: 模型训练收敛很慢
**解决**:
- 调整学习率（尝试0.01, 0.001, 0.0001）
- 增加训练轮数
- 检查数据归一化
- 尝试不同的优化器（SGD, RMSprop）

### 4. 过拟合问题
**问题**: 训练集性能好，测试集性能差
**解决**:
- 增加Dropout比例
- 减小模型复杂度
- 增加训练数据
- 使用L2正则化

## 📋 系统监控

### 训练过程监控
- 观察训练损失下降趋势
- 监控GPU/CPU使用率
- 检查内存使用情况

### 模型质量评估
- 查看R²分数：> 0.8为良好
- 观察预测曲线的拟合程度
- 检查残差分布的随机性

## 🔄 持续优化

### 模型改进建议
1. **特征工程**: 添加时间特征（小时、星期、月份）
2. **数据增强**: 添加噪声、时间偏移
3. **集成学习**: 组合多个模型的预测
4. **超参数搜索**: 使用Grid Search或Bayesian优化

### 生产部署
1. **模型版本管理**: 使用MLflow或类似工具
2. **API服务**: 将训练好的模型封装为REST API
3. **监控系统**: 监控模型性能和数据漂移
4. **自动重训练**: 定期使用新数据重新训练模型

---

**联系方式**: 如有问题，请查看项目README或提交Issue
**更新日期**: 2025年6月16日
