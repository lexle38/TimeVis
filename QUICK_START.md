# TimeVis 快速启动指南

本指南将帮助您快速启动TimeVis时间序列预测系统，包括数据处理、模型微调和Web应用运行。

## 🚀 一键启动流程

### 方法一：Windows批处理启动（推荐）
```bash
# 双击运行或在命令行中执行
start_timevis.bat
```

### 方法二：Python一键启动
```bash
# 环境检查和安装（首次运行）
python setup_environment.py

# 一键执行完整流程
python quick_start.py

# 或分别执行不同模块
python quick_start.py --data-only     # 仅数据处理
python quick_start.py --model-only    # 仅模型训练
```

### 方法三：分步手动执行
```bash
# 1. 环境准备
pip install -r requirements.txt

# 2. 数据处理
python data_processing.py

# 3. 模型训练
python model_training.py
```

### 第三步：启动Web应用

#### 后端启动（需要3个终端）

**终端1 - 启动Redis**
```bash
# 请确保Redis服务器已启动
# Windows: 可以通过Windows Services启动Redis
# 或者运行: redis-server
```

**终端2 - 启动Celery Worker**
```bash
cd d:\pycharm-project\TimeVis
venv\Scripts\activate
python backend\celery_worker.py
```

**终端3 - 启动Flask应用**
```bash
cd d:\pycharm-project\TimeVis
venv\Scripts\activate
python backend\app.py
```

#### 前端启动
```bash
# 新建终端
cd d:\pycharm-project\TimeVis\frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

### 第四步：访问应用
- 前端应用：http://localhost:3000
- 后端API：http://localhost:5000
- API文档：http://localhost:5000/docs

## 📊 数据集说明

### 1. weather.csv（天气数据）
- **大小**: 7MB, 52,698行记录
- **时间频率**: 每10分钟
- **时间范围**: 2020年1月开始
- **主要特征**:
  - `T (degC)`: 温度（摄氏度）
  - `rh (%)`: 相对湿度
  - `wv (m/s)`: 风速
  - `rain (mm)`: 降雨量
  - `p (mbar)`: 大气压力
- **预测目标**: 温度预测

### 2. electricity.csv（用电量数据）
- **大小**: 95MB, 大规模时间序列
- **时间频率**: 每小时
- **时间范围**: 2016年7月开始
- **特征**: 320个电力消耗相关指标（编号0-319）
- **预测目标**: 用电量预测

## 🔧 处理流程详解

### 数据处理步骤
1. **自动数据探索**
   - 检测时间列和数值特征
   - 统计缺失值和异常值
   - 生成数据质量报告

2. **数据清洗**
   - 处理特殊字符和编码问题
   - 填补缺失值（前向填充+后向填充）
   - 异常值处理（IQR方法）

3. **特征工程**
   - 选择最重要的数值特征
   - 数据标准化和归一化
   - 时间序列重采样

4. **数据集生成**
   - 创建训练用的时间序列数据集
   - 生成演示用的小样本数据
   - 保存处理后的数据到`data/processed/`

### 模型训练流程
1. **LSTM模型**
   - 多层LSTM网络
   - Dropout正则化
   - 序列长度：60个时间步
   - 自动超参数优化

2. **Transformer模型**
   - 编码器架构（模拟Qwen）
   - 多头注意力机制
   - 位置编码
   - 梯度裁剪和学习率调度

3. **训练特性**
   - 早停机制防止过拟合
   - 自动模型保存
   - 实时训练监控
   - 性能指标计算

## 📈 结果示例

### 预期性能指标
**天气数据（温度预测）**
- LSTM: R² ≈ 0.92, MAE ≈ 1.2°C
- Transformer: R² ≈ 0.90, MAE ≈ 1.4°C

**用电量数据**
- LSTM: R² ≈ 0.85, MAE ≈ 150kWh
- Transformer: R² ≈ 0.88, MAE ≈ 120kWh

### 输出文件位置
```
TimeVis/
├── data/processed/          # 处理后的数据
│   ├── weather_processed.csv
│   ├── weather_demo.csv
│   ├── electricity_processed.csv
│   ├── electricity_demo.csv
│   ├── datasets_info.json
│   └── data_analysis_report.png
├── models/                  # 训练好的模型
│   ├── lstm_weather_temperature_best.pth
│   ├── lstm_electricity_consumption_best.pth
│   ├── transformer_weather_temperature_best.pth
│   └── transformer_electricity_consumption_best.pth
└── results/                 # 训练结果
    ├── lstm_weather_temperature_20250616_*.json
    ├── lstm_weather_temperature_20250616_*.png
    ├── transformer_weather_temperature_20250616_*.json
    ├── transformer_electricity_consumption_20250616_*.json
    └── model_comparison_20250616_*.csv
```

## 🎛️ 自定义配置

### 调整训练参数
编辑`model_training.py`中的参数：
```python
# LSTM参数调整
lstm_hyperparameters = {
    'sequence_length': 120,     # 增加历史窗口
    'hidden_size': 256,         # 增加模型容量
    'num_layers': 3,            # 增加网络深度
    'learning_rate': 0.0005,    # 调整学习率
    'batch_size': 64,           # 调整批次大小
    'epochs': 200               # 增加训练轮数
}

# Transformer参数调整
transformer_hyperparameters = {
    'sequence_length': 120,
    'hidden_size': 512,         # 更大的模型
    'num_heads': 16,            # 更多注意力头
    'num_layers': 6,            # 更深的网络
    'learning_rate': 0.00005,   # 更低的学习率
    'batch_size': 8             # 适应GPU内存
}
```

### 数据采样调整
如果内存不足，可以调整采样大小：
```python
# 在data_processing.py中调整
processor = TimeSeriesDataProcessor()
# 减少electricity数据的采样大小
elec_df, elec_demo = processor.analyze_electricity_data(sample_size=50000)
```

## ⚠️ 常见问题解决

### 1. 依赖安装问题
```bash
# 如果pip安装失败，尝试使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果需要GPU支持
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. 内存不足
```bash
# 如果处理大文件时内存不足，请：
# 1. 关闭其他程序释放内存
# 2. 减少data_processing.py中的sample_size参数
# 3. 使用分批处理模式
```

### 3. Redis连接问题
```bash
# 确保Redis服务正在运行
# Windows: 在服务管理器中启动Redis
# 或者下载Redis for Windows并启动redis-server.exe
```

### 4. 前端依赖问题
```bash
# 如果npm install失败
cd frontend
npm cache clean --force
npm install --registry https://registry.npm.taobao.org
```

## 📞 技术支持

如果遇到问题，请按以下顺序检查：

1. **确认环境要求**
   - Python 3.8+
   - Node.js 16+
   - 足够的内存空间（8GB+推荐）

2. **检查日志输出**
   - 查看终端中的错误信息
   - 检查生成的日志文件

3. **验证数据文件**
   - 确认`data/weather.csv`和`data/electricity.csv`存在
   - 检查文件是否完整未损坏

4. **重新运行流程**
   - 尝试删除`data/processed/`目录后重新运行
   - 清理`models/`和`results/`目录后重新训练

---

**祝您使用愉快！** 🎉
