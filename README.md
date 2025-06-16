# TimeVis - 时间序列预测与可视化系统

基于Qwen大模型和LSTM的智能时间序列预测与可视化系统。支持多种时间序列预测算法，提供完整的数据管理、模型训练、预测分析和结果可视化功能。

## 🚀 功能特性

### 核心功能
- **多算法支持**: 集成LSTM神经网络和Qwen大语言模型两种预测算法
- **数据管理**: 支持CSV/Excel格式数据上传、预览、统计分析
- **模型训练**: 可视化训练过程，自动超参数调优，训练进度实时监控
- **预测分析**: 灵活的预测步长配置，多种评估指标，预测结果可视化
- **模型比较**: 多模型性能对比分析，自动最优模型推荐
- **任务管理**: 异步任务执行，实时进度跟踪，任务状态监控

### 技术架构
- **前端**: Vue 3 + TypeScript + Element Plus + ECharts
- **后端**: Flask + Celery + Redis + SQLAlchemy
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **模型**: PyTorch (LSTM) + Transformers (Qwen)
- **任务队列**: Celery + Redis
- **API文档**: 完整的RESTful API接口

## 📋 系统要求

### 开发环境
- Python 3.8+
- Node.js 16+
- Redis 6+
- Git

### 推荐配置
- 内存: 8GB+
- 显卡: NVIDIA GPU (支持CUDA，可选)
- 存储: 5GB+ 可用空间

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd TimeVis
```

### 2. 后端环境设置

#### 2.1 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 环境配置
创建 `.env` 文件（可选）：
```bash
# 数据库配置
DATABASE_URL=sqlite:///timevis.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 模型配置
MODEL_PATH=./models
DATA_PATH=./data

# API配置
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 2.4 初始化数据库
```bash
cd backend
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 3. 前端环境设置

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 开发环境启动
```bash
npm run dev
```

### 4. 启动完整系统

#### 4.1 启动Redis (如果未运行)
```bash
# Windows (需要预先安装Redis)
redis-server

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

#### 4.2 方式一：使用启动脚本（推荐）

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

#### 4.3 方式二：手动启动各服务

**终端1 - 启动后端API服务:**
```bash
cd backend
python app/__init__.py
```

**终端2 - 启动Celery任务队列:**
```bash
cd backend
python celery_worker.py
```

**终端3 - 启动前端开发服务器:**
```bash
cd frontend
npm run dev
```

### 5. 访问系统
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000/api
- **API文档**: 查看 `API_DOCS.md`

## 📖 详细使用指南

### 数据管理
1. **上传数据集**
   - 支持CSV、Excel格式文件
   - 自动数据类型检测和统计分析
   - 数据预览和列信息查看

2. **数据预处理**
   - 缺失值处理和异常值检测
   - 数据归一化和标准化
   - 时间序列特征工程

### 模型训练

#### LSTM模型训练
1. **基础参数设置**
   ```
   - 模型名称: 自定义模型名称
   - 目标列: 选择要预测的数值列
   - 序列长度: 用于预测的历史数据点数量 (建议: 30-60)
   - 测试集比例: 用于模型评估的数据比例 (建议: 0.2)
   ```

2. **高级参数调优**
   ```
   - 批次大小 (batch_size): 32-128
   - 训练轮数 (epochs): 50-200
   - 学习率 (learning_rate): 0.001-0.01
   - 隐藏层大小 (hidden_size): 64-256
   - 网络层数 (num_layers): 1-3
   ```

#### Qwen模型训练
1. **模型配置**
   ```
   - 基于预训练Qwen模型微调
   - 自适应序列长度
   - 自动超参数优化
   ```

2. **训练监控**
   - 实时损失函数曲线
   - 验证集性能监控
   - 早停机制防止过拟合

### 预测分析
1. **创建预测任务**
   - 选择已训练的模型
   - 设置预测步数 (1-100步)
   - 可选择输入数据或使用默认数据

2. **结果分析**
   - 预测值与实际值对比图表
   - 性能指标计算 (MSE, MAE, RMSE, R²)
   - 预测置信区间展示

3. **结果导出**
   - CSV格式数据导出
   - 图表图片导出
   - 预测报告生成

### 模型比较
1. **创建比较任务**
   - 选择多个模型 (至少2个)
   - 使用相同数据集进行评估
   - 自动生成性能对比报告

2. **对比分析**
   - 多维度性能指标对比
   - 可视化性能差异
   - 自动推荐最优模型

### 任务监控
1. **任务状态跟踪**
   - 实时任务进度显示
   - 任务执行时间统计
   - 错误信息详细展示

2. **系统监控**
   - 系统资源使用监控
   - 任务队列状态显示
   - 性能指标统计

## 🔧 高级配置

### 模型微调

#### LSTM模型优化
1. **网络架构调整**
   ```python
   # 在 backend/models/lstm_model.py 中修改
   class LSTMModel(nn.Module):
       def __init__(self, input_size, hidden_size, num_layers, output_size):
           # 添加dropout层
           self.dropout = nn.Dropout(0.2)
           # 添加批归一化
           self.batch_norm = nn.BatchNorm1d(hidden_size)
   ```

2. **超参数搜索**
   ```python
   # 使用网格搜索或贝叶斯优化
   param_grid = {
       'hidden_size': [64, 128, 256],
       'num_layers': [1, 2, 3],
       'learning_rate': [0.001, 0.01, 0.1],
       'batch_size': [16, 32, 64]
   }
   ```

#### Qwen模型微调
1. **模型配置调整**
   ```python
   # 在 backend/models/qwen_model.py 中配置
   model_config = {
       'model_name': 'Qwen/Qwen-7B-Chat',
       'max_length': 2048,
       'temperature': 0.7,
       'do_sample': True
   }
   ```

2. **微调参数设置**
   ```python
   training_args = {
       'learning_rate': 2e-5,
       'num_train_epochs': 3,
       'per_device_train_batch_size': 4,
       'gradient_accumulation_steps': 8
   }
   ```

### 性能优化

#### 系统级优化
1. **数据库优化**
   ```bash
   # 使用PostgreSQL替代SQLite
   pip install psycopg2-binary
   # 修改配置文件中的DATABASE_URL
   ```

2. **缓存配置**
   ```bash
   # Redis缓存优化
   redis-cli config set maxmemory 1gb
   redis-cli config set maxmemory-policy allkeys-lru
   ```

3. **异步任务优化**
   ```bash
   # 增加Celery工作进程
   celery -A celery_worker.celery worker --loglevel=info --concurrency=4
   ```

#### 模型推理优化
1. **批量预测**
   ```python
   # 批量处理多个预测请求
   def batch_predict(models, data_batch):
       results = []
       for model in models:
           batch_result = model.predict_batch(data_batch)
           results.append(batch_result)
       return results
   ```

2. **模型缓存**
   ```python
   # 实现模型缓存机制
   from functools import lru_cache
   
   @lru_cache(maxsize=10)
   def load_model(model_path):
       return torch.load(model_path)
   ```

### 部署配置

#### 生产环境部署
1. **Docker部署**
   ```dockerfile
   # Dockerfile示例
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Nginx配置**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

3. **环境变量配置**
   ```bash
   # .env.production
   FLASK_ENV=production
   DATABASE_URL=postgresql://user:password@localhost/timevis
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key
   ```

## 🌩️ 云服务器部署

### 一键部署（推荐）

适用于阿里云、腾讯云、AWS、Google Cloud等云服务器：

```bash
# 1. 上传项目到服务器
git clone <your-repo> TimeVis
cd TimeVis

# 2. 运行一键部署脚本
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

### Docker部署

```bash
# 1. 构建并启动容器
docker-compose up -d

# 2. 查看服务状态
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 环境检查

部署前检查环境：

```bash
# Linux/macOS
chmod +x check_environment.sh
./check_environment.sh

# Windows
check_environment.bat
```

### 服务管理

```bash
# 启动服务
./start_service.sh

# 停止服务
./stop_service.sh

# 查看服务状态
tmux attach -t timevis
```

### 云平台配置建议

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核心 | 4核心+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB SSD | 50GB SSD |
| 网络 | 1Mbps | 5Mbps+ |

详细部署文档请参考：[CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)

---

## 🖥️ 本地开发

# TimeVis - 时间序列预测与可视化系统

基于Qwen大模型和LSTM的智能时间序列预测与可视化系统。支持多种时间序列预测算法，提供完整的数据管理、模型训练、预测分析和结果可视化功能。

## 🚀 功能特性

### 核心功能
- **多算法支持**: 集成LSTM神经网络和Qwen大语言模型两种预测算法
- **数据管理**: 支持CSV/Excel格式数据上传、预览、统计分析
- **模型训练**: 可视化训练过程，自动超参数调优，训练进度实时监控
- **预测分析**: 灵活的预测步长配置，多种评估指标，预测结果可视化
- **模型比较**: 多模型性能对比分析，自动最优模型推荐
- **任务管理**: 异步任务执行，实时进度跟踪，任务状态监控

### 技术架构
- **前端**: Vue 3 + TypeScript + Element Plus + ECharts
- **后端**: Flask + Celery + Redis + SQLAlchemy
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **模型**: PyTorch (LSTM) + Transformers (Qwen)
- **任务队列**: Celery + Redis
- **API文档**: 完整的RESTful API接口

## 📋 系统要求

### 开发环境
- Python 3.8+
- Node.js 16+
- Redis 6+
- Git

### 推荐配置
- 内存: 8GB+
- 显卡: NVIDIA GPU (支持CUDA，可选)
- 存储: 5GB+ 可用空间

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd TimeVis
```

### 2. 后端环境设置

#### 2.1 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 环境配置
创建 `.env` 文件（可选）：
```bash
# 数据库配置
DATABASE_URL=sqlite:///timevis.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 模型配置
MODEL_PATH=./models
DATA_PATH=./data

# API配置
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 2.4 初始化数据库
```bash
cd backend
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 3. 前端环境设置

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 开发环境启动
```bash
npm run dev
```

### 4. 启动完整系统

#### 4.1 启动Redis (如果未运行)
```bash
# Windows (需要预先安装Redis)
redis-server

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

#### 4.2 方式一：使用启动脚本（推荐）

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

#### 4.3 方式二：手动启动各服务

**终端1 - 启动后端API服务:**
```bash
cd backend
python app/__init__.py
```

**终端2 - 启动Celery任务队列:**
```bash
cd backend
python celery_worker.py
```

**终端3 - 启动前端开发服务器:**
```bash
cd frontend
npm run dev
```

### 5. 访问系统
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000/api
- **API文档**: 查看 `API_DOCS.md`

## 📖 详细使用指南

### 数据管理
1. **上传数据集**
   - 支持CSV、Excel格式文件
   - 自动数据类型检测和统计分析
   - 数据预览和列信息查看

2. **数据预处理**
   - 缺失值处理和异常值检测
   - 数据归一化和标准化
   - 时间序列特征工程

### 模型训练

#### LSTM模型训练
1. **基础参数设置**
   ```
   - 模型名称: 自定义模型名称
   - 目标列: 选择要预测的数值列
   - 序列长度: 用于预测的历史数据点数量 (建议: 30-60)
   - 测试集比例: 用于模型评估的数据比例 (建议: 0.2)
   ```

2. **高级参数调优**
   ```
   - 批次大小 (batch_size): 32-128
   - 训练轮数 (epochs): 50-200
   - 学习率 (learning_rate): 0.001-0.01
   - 隐藏层大小 (hidden_size): 64-256
   - 网络层数 (num_layers): 1-3
   ```

#### Qwen模型训练
1. **模型配置**
   ```
   - 基于预训练Qwen模型微调
   - 自适应序列长度
   - 自动超参数优化
   ```

2. **训练监控**
   - 实时损失函数曲线
   - 验证集性能监控
   - 早停机制防止过拟合

### 预测分析
1. **创建预测任务**
   - 选择已训练的模型
   - 设置预测步数 (1-100步)
   - 可选择输入数据或使用默认数据

2. **结果分析**
   - 预测值与实际值对比图表
   - 性能指标计算 (MSE, MAE, RMSE, R²)
   - 预测置信区间展示

3. **结果导出**
   - CSV格式数据导出
   - 图表图片导出
   - 预测报告生成

### 模型比较
1. **创建比较任务**
   - 选择多个模型 (至少2个)
   - 使用相同数据集进行评估
   - 自动生成性能对比报告

2. **对比分析**
   - 多维度性能指标对比
   - 可视化性能差异
   - 自动推荐最优模型

### 任务监控
1. **任务状态跟踪**
   - 实时任务进度显示
   - 任务执行时间统计
   - 错误信息详细展示

2. **系统监控**
   - 系统资源使用监控
   - 任务队列状态显示
   - 性能指标统计

## 🔧 高级配置

### 模型微调

#### LSTM模型优化
1. **网络架构调整**
   ```python
   # 在 backend/models/lstm_model.py 中修改
   class LSTMModel(nn.Module):
       def __init__(self, input_size, hidden_size, num_layers, output_size):
           # 添加dropout层
           self.dropout = nn.Dropout(0.2)
           # 添加批归一化
           self.batch_norm = nn.BatchNorm1d(hidden_size)
   ```

2. **超参数搜索**
   ```python
   # 使用网格搜索或贝叶斯优化
   param_grid = {
       'hidden_size': [64, 128, 256],
       'num_layers': [1, 2, 3],
       'learning_rate': [0.001, 0.01, 0.1],
       'batch_size': [16, 32, 64]
   }
   ```

#### Qwen模型微调
1. **模型配置调整**
   ```python
   # 在 backend/models/qwen_model.py 中配置
   model_config = {
       'model_name': 'Qwen/Qwen-7B-Chat',
       'max_length': 2048,
       'temperature': 0.7,
       'do_sample': True
   }
   ```

2. **微调参数设置**
   ```python
   training_args = {
       'learning_rate': 2e-5,
       'num_train_epochs': 3,
       'per_device_train_batch_size': 4,
       'gradient_accumulation_steps': 8
   }
   ```

### 性能优化

#### 系统级优化
1. **数据库优化**
   ```bash
   # 使用PostgreSQL替代SQLite
   pip install psycopg2-binary
   # 修改配置文件中的DATABASE_URL
   ```

2. **缓存配置**
   ```bash
   # Redis缓存优化
   redis-cli config set maxmemory 1gb
   redis-cli config set maxmemory-policy allkeys-lru
   ```

3. **异步任务优化**
   ```bash
   # 增加Celery工作进程
   celery -A celery_worker.celery worker --loglevel=info --concurrency=4
   ```

#### 模型推理优化
1. **批量预测**
   ```python
   # 批量处理多个预测请求
   def batch_predict(models, data_batch):
       results = []
       for model in models:
           batch_result = model.predict_batch(data_batch)
           results.append(batch_result)
       return results
   ```

2. **模型缓存**
   ```python
   # 实现模型缓存机制
   from functools import lru_cache
   
   @lru_cache(maxsize=10)
   def load_model(model_path):
       return torch.load(model_path)
   ```

### 部署配置

#### 生产环境部署
1. **Docker部署**
   ```dockerfile
   # Dockerfile示例
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Nginx配置**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

3. **环境变量配置**
   ```bash
   # .env.production
   FLASK_ENV=production
   DATABASE_URL=postgresql://user:password@localhost/timevis
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key
   ```

## 🌩️ 云服务器部署

### 一键部署（推荐）

适用于阿里云、腾讯云、AWS、Google Cloud等云服务器：

```bash
# 1. 上传项目到服务器
git clone <your-repo> TimeVis
cd TimeVis

# 2. 运行一键部署脚本
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

### Docker部署

```bash
# 1. 构建并启动容器
docker-compose up -d

# 2. 查看服务状态
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 环境检查

部署前检查环境：

```bash
# Linux/macOS
chmod +x check_environment.sh
./check_environment.sh

# Windows
check_environment.bat
```

### 服务管理

```bash
# 启动服务
./start_service.sh

# 停止服务
./stop_service.sh

# 查看服务状态
tmux attach -t timevis
```

### 云平台配置建议

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核心 | 4核心+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB SSD | 50GB SSD |
| 网络 | 1Mbps | 5Mbps+ |

详细部署文档请参考：[CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)

---

## 🖥️ 本地开发

# TimeVis - 时间序列预测与可视化系统

基于Qwen大模型和LSTM的智能时间序列预测与可视化系统。支持多种时间序列预测算法，提供完整的数据管理、模型训练、预测分析和结果可视化功能。

## 🚀 功能特性

### 核心功能
- **多算法支持**: 集成LSTM神经网络和Qwen大语言模型两种预测算法
- **数据管理**: 支持CSV/Excel格式数据上传、预览、统计分析
- **模型训练**: 可视化训练过程，自动超参数调优，训练进度实时监控
- **预测分析**: 灵活的预测步长配置，多种评估指标，预测结果可视化
- **模型比较**: 多模型性能对比分析，自动最优模型推荐
- **任务管理**: 异步任务执行，实时进度跟踪，任务状态监控

### 技术架构
- **前端**: Vue 3 + TypeScript + Element Plus + ECharts
- **后端**: Flask + Celery + Redis + SQLAlchemy
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **模型**: PyTorch (LSTM) + Transformers (Qwen)
- **任务队列**: Celery + Redis
- **API文档**: 完整的RESTful API接口

## 📋 系统要求

### 开发环境
- Python 3.8+
- Node.js 16+
- Redis 6+
- Git

### 推荐配置
- 内存: 8GB+
- 显卡: NVIDIA GPU (支持CUDA，可选)
- 存储: 5GB+ 可用空间

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd TimeVis
```

### 2. 后端环境设置

#### 2.1 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 环境配置
创建 `.env` 文件（可选）：
```bash
# 数据库配置
DATABASE_URL=sqlite:///timevis.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 模型配置
MODEL_PATH=./models
DATA_PATH=./data

# API配置
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 2.4 初始化数据库
```bash
cd backend
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 3. 前端环境设置

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 开发环境启动
```bash
npm run dev
```

### 4. 启动完整系统

#### 4.1 启动Redis (如果未运行)
```bash
# Windows (需要预先安装Redis)
redis-server

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

#### 4.2 方式一：使用启动脚本（推荐）

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

#### 4.3 方式二：手动启动各服务

**终端1 - 启动后端API服务:**
```bash
cd backend
python app/__init__.py
```

**终端2 - 启动Celery任务队列:**
```bash
cd backend
python celery_worker.py
```

**终端3 - 启动前端开发服务器:**
```bash
cd frontend
npm run dev
```

### 5. 访问系统
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000/api
- **API文档**: 查看 `API_DOCS.md`

## 📖 详细使用指南

### 数据管理
1. **上传数据集**
   - 支持CSV、Excel格式文件
   - 自动数据类型检测和统计分析
   - 数据预览和列信息查看

2. **数据预处理**
   - 缺失值处理和异常值检测
   - 数据归一化和标准化
   - 时间序列特征工程

### 模型训练

#### LSTM模型训练
1. **基础参数设置**
   ```
   - 模型名称: 自定义模型名称
   - 目标列: 选择要预测的数值列
   - 序列长度: 用于预测的历史数据点数量 (建议: 30-60)
   - 测试集比例: 用于模型评估的数据比例 (建议: 0.2)
   ```

2. **高级参数调优**
   ```
   - 批次大小 (batch_size): 32-128
   - 训练轮数 (epochs): 50-200
   - 学习率 (learning_rate): 0.001-0.01
   - 隐藏层大小 (hidden_size): 64-256
   - 网络层数 (num_layers): 1-3
   ```

#### Qwen模型训练
1. **模型配置**
   ```
   - 基于预训练Qwen模型微调
   - 自适应序列长度
   - 自动超参数优化
   ```

2. **训练监控**
   - 实时损失函数曲线
   - 验证集性能监控
   - 早停机制防止过拟合

### 预测分析
1. **创建预测任务**
   - 选择已训练的模型
   - 设置预测步数 (1-100步)
   - 可选择输入数据或使用默认数据

2. **结果分析**
   - 预测值与实际值对比图表
   - 性能指标计算 (MSE, MAE, RMSE, R²)
   - 预测置信区间展示

3. **结果导出**
   - CSV格式数据导出
   - 图表图片导出
   - 预测报告生成

### 模型比较
1. **创建比较任务**
   - 选择多个模型 (至少2个)
   - 使用相同数据集进行评估
   - 自动生成性能对比报告

2. **对比分析**
   - 多维度性能指标对比
   - 可视化性能差异
   - 自动推荐最优模型

### 任务监控
1. **任务状态跟踪**
   - 实时任务进度显示
   - 任务执行时间统计
   - 错误信息详细展示

2. **系统监控**
   - 系统资源使用监控
   - 任务队列状态显示
   - 性能指标统计

## 🔧 高级配置

### 模型微调

#### LSTM模型优化
1. **网络架构调整**
   ```python
   # 在 backend/models/lstm_model.py 中修改
   class LSTMModel(nn.Module):
       def __init__(self, input_size, hidden_size, num_layers, output_size):
           # 添加dropout层
           self.dropout = nn.Dropout(0.2)
           # 添加批归一化
           self.batch_norm = nn.BatchNorm1d(hidden_size)
   ```

2. **超参数搜索**
   ```python
   # 使用网格搜索或贝叶斯优化
   param_grid = {
       'hidden_size': [64, 128, 256],
       'num_layers': [1, 2, 3],
       'learning_rate': [0.001, 0.01, 0.1],
       'batch_size': [16, 32, 64]
   }
   ```

#### Qwen模型微调
1. **模型配置调整**
   ```python
   # 在 backend/models/qwen_model.py 中配置
   model_config = {
       'model_name': 'Qwen/Qwen-7B-Chat',
       'max_length': 2048,
       'temperature': 0.7,
       'do_sample': True
   }
   ```

2. **微调参数设置**
   ```python
   training_args = {
       'learning_rate': 2e-5,
       'num_train_epochs': 3,
       'per_device_train_batch_size': 4,
       'gradient_accumulation_steps': 8
   }
   ```

### 性能优化

#### 系统级优化
1. **数据库优化**
   ```bash
   # 使用PostgreSQL替代SQLite
   pip install psycopg2-binary
   # 修改配置文件中的DATABASE_URL
   ```

2. **缓存配置**
   ```bash
   # Redis缓存优化
   redis-cli config set maxmemory 1gb
   redis-cli config set maxmemory-policy allkeys-lru
   ```

3. **异步任务优化**
   ```bash
   # 增加Celery工作进程
   celery -A celery_worker.celery worker --loglevel=info --concurrency=4
   ```

#### 模型推理优化
1. **批量预测**
   ```python
   # 批量处理多个预测请求
   def batch_predict(models, data_batch):
       results = []
       for model in models:
           batch_result = model.predict_batch(data_batch)
           results.append(batch_result)
       return results
   ```

2. **模型缓存**
   ```python
   # 实现模型缓存机制
   from functools import lru_cache
   
   @lru_cache(maxsize=10)
   def load_model(model_path):
       return torch.load(model_path)
   ```

### 部署配置

#### 生产环境部署
1. **Docker部署**
   ```dockerfile
   # Dockerfile示例
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Nginx配置**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

3. **环境变量配置**
   ```bash
   # .env.production
   FLASK_ENV=production
   DATABASE_URL=postgresql://user:password@localhost/timevis
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key
   ```

## 🌩️ 云服务器部署

### 一键部署（推荐）

适用于阿里云、腾讯云、AWS、Google Cloud等云服务器：

```bash
# 1. 上传项目到服务器
git clone <your-repo> TimeVis
cd TimeVis

# 2. 运行一键部署脚本
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

### Docker部署

```bash
# 1. 构建并启动容器
docker-compose up -d

# 2. 查看服务状态
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 环境检查

部署前检查环境：

```bash
# Linux/macOS
chmod +x check_environment.sh
./check_environment.sh

# Windows
check_environment.bat
```

### 服务管理

```bash
# 启动服务
./start_service.sh

# 停止服务
./stop_service.sh

# 查看服务状态
tmux attach -t timevis
```

### 云平台配置建议

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核心 | 4核心+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB SSD | 50GB SSD |
| 网络 | 1Mbps | 5Mbps+ |

详细部署文档请参考：[CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)

---

## 🖥️ 本地开发

# TimeVis - 时间序列预测与可视化系统

基于Qwen大模型和LSTM的智能时间序列预测与可视化系统。支持多种时间序列预测算法，提供完整的数据管理、模型训练、预测分析和结果可视化功能。

## 🚀 功能特性

### 核心功能
- **多算法支持**: 集成LSTM神经网络和Qwen大语言模型两种预测算法
- **数据管理**: 支持CSV/Excel格式数据上传、预览、统计分析
- **模型训练**: 可视化训练过程，自动超参数调优，训练进度实时监控
- **预测分析**: 灵活的预测步长配置，多种评估指标，预测结果可视化
- **模型比较**: 多模型性能对比分析，自动最优模型推荐
- **任务管理**: 异步任务执行，实时进度跟踪，任务状态监控

### 技术架构
- **前端**: Vue 3 + TypeScript + Element Plus + ECharts
- **后端**: Flask + Celery + Redis + SQLAlchemy
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **模型**: PyTorch (LSTM) + Transformers (Qwen)
- **任务队列**: Celery + Redis
- **API文档**: 完整的RESTful API接口

## 📋 系统要求

### 开发环境
- Python 3.8+
- Node.js 16+
- Redis 6+
- Git

### 推荐配置
- 内存: 8GB+
- 显卡: NVIDIA GPU (支持CUDA，可选)
- 存储: 5GB+ 可用空间

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd TimeVis
```

### 2. 后端环境设置

#### 2.1 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 环境配置
创建 `.env` 文件（可选）：
```bash
# 数据库配置
DATABASE_URL=sqlite:///timevis.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 模型配置
MODEL_PATH=./models
DATA_PATH=./data

# API配置
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 2.4 初始化数据库
```bash
cd backend
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 3. 前端环境设置

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 开发环境启动
```bash
npm run dev
```

### 4. 启动完整系统

#### 4.1 启动Redis (如果未运行)
```bash
# Windows (需要预先安装Redis)
redis-server

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

#### 4.2 方式一：使用启动脚本（推荐）

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

#### 4.3 方式二：手动启动各服务

**终端1 - 启动后端API服务:**
```bash
cd backend
python app/__init__.py
```

**终端2 - 启动Celery任务队列:**
```bash
cd backend
python celery_worker.py
```

**终端3 - 启动前端开发服务器:**
```bash
cd frontend
npm run dev
```

### 5. 访问系统
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000/api
- **API文档**: 查看 `API_DOCS.md`

## 📖 详细使用指南

### 数据管理
1. **上传数据集**
   - 支持CSV、Excel格式文件
   - 自动数据类型检测和统计分析
   - 数据预览和列信息查看

2. **数据预处理**
   - 缺失值处理和异常值检测
   - 数据归一化和标准化
   - 时间序列特征工程

### 模型训练

#### LSTM模型训练
1. **基础参数设置**
   ```
   - 模型名称: 自定义模型名称
   - 目标列: 选择要预测的数值列
   - 序列长度: 用于预测的历史数据点数量 (建议: 30-60)
   - 测试集比例: 用于模型评估的数据比例 (建议: 0.2)
   ```

2. **高级参数调优**
   ```
   - 批次大小 (batch_size): 32-128
   - 训练轮数 (epochs): 50-200
   - 学习率 (learning_rate): 0.001-0.01
   - 隐藏层大小 (hidden_size): 64-256
   - 网络层数 (num_layers): 1-3
   ```

#### Qwen模型训练
1. **模型配置**
   ```
   - 基于预训练Qwen模型微调
   - 自适应序列长度
   - 自动超参数优化
   ```

2. **训练监控**
   - 实时损失函数曲线
   - 验证集性能监控
   - 早停机制防止过拟合

### 预测分析
1. **创建预测任务**
   - 选择已训练的模型
   - 设置预测步数 (1-100步)
   - 可选择输入数据或使用默认数据

2. **结果分析**
   - 预测值与实际值对比图表
   - 性能指标计算 (MSE, MAE, RMSE, R²)
   - 预测置信区间展示

3. **结果导出**
   - CSV格式数据导出
   - 图表图片导出
   - 预测报告生成

### 模型比较
1. **创建比较任务**
   - 选择多个模型 (至少2个)
   - 使用相同数据集进行评估
   - 自动生成性能对比报告

2. **对比分析**
   - 多维度性能指标对比
   - 可视化性能差异
   - 自动推荐最优模型

### 任务监控
1. **任务状态跟踪**
   - 实时任务进度显示
   - 任务执行时间统计
   - 错误信息详细展示

2. **系统监控**
   - 系统资源使用监控
   - 任务队列状态显示
   - 性能指标统计

## 🔧 高级配置

### 模型微调

#### LSTM模型优化
1. **网络架构调整**
   ```python
   # 在 backend/models/lstm_model.py 中修改
   class LSTMModel(nn.Module):
       def __init__(self, input_size, hidden_size, num_layers, output_size):
           # 添加dropout层
           self.dropout = nn.Dropout(0.2)
           # 添加批归一化
           self.batch_norm = nn.BatchNorm1d(hidden_size)
   ```

2. **超参数搜索**
   ```python
   # 使用网格搜索或贝叶斯优化
   param_grid = {
       'hidden_size': [64, 128, 256],
       'num_layers': [1, 2, 3],
       'learning_rate': [0.001, 0.01, 0.1],
       'batch_size': [16, 32, 64]
   }
   ```

#### Qwen模型微调
1. **模型配置调整**
   ```python
   # 在 backend/models/qwen_model.py 中配置
   model_config = {
       'model_name': 'Qwen/Qwen-7B-Chat',
       'max_length': 2048,
       'temperature': 0.7,
       'do_sample': True
   }
   ```

2. **微调参数设置**
   ```python
   training_args = {
       'learning_rate': 2e-5,
       'num_train_epochs': 3,
       'per_device_train_batch_size': 4,
       'gradient_accumulation_steps': 8
   }
   ```

### 性能优化

#### 系统级优化
1. **数据库优化**
   ```bash
   # 使用PostgreSQL替代SQLite
   pip install psycopg2-binary
   # 修改配置文件中的DATABASE_URL
   ```

2. **缓存配置**
   ```bash
   # Redis缓存优化
   redis-cli config set maxmemory 1gb
   redis-cli config set maxmemory-policy allkeys-lru
   ```

3. **异步任务优化**
   ```bash
   # 增加Celery工作进程
   celery -A celery_worker.celery worker --loglevel=info --concurrency=4
   ```

#### 模型推理优化
1. **批量预测**
   ```python
   # 批量处理多个预测请求
   def batch_predict(models, data_batch):
       results = []
       for model in models:
           batch_result = model.predict_batch(data_batch)
           results.append(batch_result)
       return results
   ```

2. **模型缓存**
   ```python
   # 实现模型缓存机制
   from functools import lru_cache
   
   @lru_cache(maxsize=10)
   def load_model(model_path):
       return torch.load(model_path)
   ```

### 部署配置

#### 生产环境部署
1. **Docker部署**
   ```dockerfile
   # Dockerfile示例
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Nginx配置**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

3. **环境变量配置**
   ```bash
   # .env.production
   FLASK_ENV=production
   DATABASE_URL=postgresql://user:password@localhost/timevis
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key
   ```

## 🌩️ 云服务器部署

### 一键部署（推荐）

适用于阿里云、腾讯云、AWS、Google Cloud等云服务器：

```bash
# 1. 上传项目到服务器
git clone <your-repo> TimeVis
cd TimeVis

# 2. 运行一键部署脚本
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

### Docker部署

```bash
# 1. 构建并启动容器
docker-compose up -d

# 2. 查看服务状态
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 环境检查

部署前检查环境：

```bash
# Linux/macOS
chmod +x check_environment.sh
./check_environment.sh

# Windows
check_environment.bat
```

### 服务管理

```bash
# 启动服务
./start_service.sh

# 停止服务
./stop_service.sh

# 查看服务状态
tmux attach -t timevis
```

### 云平台配置建议

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核心 | 4核心+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB SSD | 50GB SSD |
| 网络 | 1Mbps | 5Mbps+ |

详细部署文档请参考：[CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)

---

## 🖥️ 本地开发
