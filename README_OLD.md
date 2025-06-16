# TimeVis - 时间序列预测与可视化系统

基于Qwen大模型和LSTM的时间序列预测系统，支持天气、电力、交通流量等多类型数据的预测与分析。

## 项目概述

TimeVis是一个完整的时间序列预测解决方案，采用前后端分离架构：

- **后端**: Flask + Celery + Redis，提供API服务和异步任务处理
- **模型**: Qwen大模型（GPT回归）+ LSTM传统深度学习模型
- **前端**: Vue3 + TypeScript（待开发）
- **数据**: 支持天气、电力负荷、交通流量等时间序列数据

## 核心特性

### 🤖 双模型架构
- **Qwen大模型**: 基于Transformer架构，支持自然语言提示的时间序列预测
- **LSTM模型**: 传统深度学习模型，提供基线对比

### 📊 数据处理
- 支持CSV、Excel、JSON格式数据上传
- 自动数据清洗、归一化、序列化
- 数据质量验证和统计分析

### 🔄 异步任务
- 基于Celery的异步训练和预测
- 实时进度监控和状态更新
- 任务队列管理和错误处理

### 📈 可视化分析
- 预测结果可视化
- 模型性能对比分析
- 残差分析和误差统计

### 🚀 易用接口
- RESTful API设计
- 完整的错误处理和日志记录
- 支持批量预测和模型比较

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue3)    │    │   后端 (Flask)   │    │   任务队列       │
│                 │    │                 │    │   (Celery)      │
│ - 数据上传       │◄──►│ - API接口        │◄──►│                 │
│ - 训练配置       │    │ - 数据处理       │    │ - 模型训练       │
│ - 结果可视化     │    │ - 任务调度       │    │ - 预测推理       │
│ - 模型管理       │    │ - 状态管理       │    │ - 模型比较       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   数据库        │    │   模型存储       │
                       │   (SQLite)      │    │   (文件系统)     │
                       │                 │    │                 │
                       │ - 任务记录       │    │ - Qwen模型       │
                       │ - 模型元数据     │    │ - LSTM模型       │
                       │ - 数据集信息     │    │ - 训练结果       │
                       └─────────────────┘    └─────────────────┘
```

## 快速开始

### 环境要求
- Python 3.8+
- Redis
- CUDA (GPU训练可选)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd TimeVis
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动Redis**
```bash
redis-server
```

4. **启动Celery Worker**
```bash
cd backend
python celery_worker.py worker --loglevel=info
```

5. **启动Flask应用**
```bash
cd backend
python run.py
```

6. **访问API**
- 健康检查: http://localhost:5000/api/health
- API文档: http://localhost:5000/api/

### 快速测试

使用提供的脚本生成示例数据并测试系统：

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

## API接口

### 数据管理
- `POST /api/upload` - 上传数据文件
- `GET /api/datasets` - 获取数据集列表
- `GET /api/datasets/<id>` - 获取数据集详情
- `POST /api/sample-data` - 生成示例数据

### 模型训练
- `POST /api/train` - 启动训练任务
- `GET /api/models` - 获取模型列表
- `GET /api/models/<id>` - 获取模型详情

### 任务管理
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/<id>` - 获取任务详情
- `POST /api/tasks/<id>/cancel` - 取消任务

### 预测分析
- `POST /api/predict` - 启动预测任务
- `POST /api/compare` - 模型比较
- `GET /api/stats` - 系统统计

## 技术特点

### Qwen模型的"GPT回归"方法
1. **文本化输入**: 将数值序列转换为自然语言描述
2. **字符级预测**: 将数字按位分解，提高预测精度
3. **LoRA微调**: 使用参数高效的微调方法
4. **提示工程**: 针对不同任务类型设计专门的提示模板

### LSTM模型优化
1. **多层架构**: 支持多层LSTM网络
2. **正则化**: Dropout和梯度裁剪
3. **早停机制**: 防止过拟合
4. **自适应学习率**: 动态调整学习率

### 数据处理流程
1. **数据验证**: 格式检查、缺失值检测
2. **数据清洗**: 异常值处理、重复值去除
3. **特征工程**: 归一化、序列化
4. **数据分割**: 训练/验证/测试集划分

## 目录结构

```
TimeVis/
├── backend/                 # 后端代码
│   ├── app/                # Flask应用
│   │   ├── __init__.py     # 应用工厂
│   │   ├── models.py       # 数据库模型
│   │   ├── routes.py       # API路由
│   │   └── tasks.py        # Celery任务
│   ├── models/             # 机器学习模型
│   │   ├── qwen_model.py   # Qwen模型封装
│   │   └── lstm_model.py   # LSTM模型封装
│   ├── utils/              # 工具模块
│   │   ├── data_processor.py  # 数据处理
│   │   └── model_trainer.py   # 模型训练器
│   ├── config/             # 配置文件
│   │   └── config.py       # 应用配置
│   ├── run.py              # 应用入口
│   ├── celery_worker.py    # Celery启动
│   └── generate_data.py    # 数据生成脚本
├── frontend/               # 前端代码（待开发）
│   └── README.md           # 前端开发说明
├── data/                   # 数据目录
│   ├── samples/            # 示例数据
│   └── test/               # 测试数据
├── models/                 # 模型存储
├── uploads/                # 上传文件
├── logs/                   # 日志文件
├── requirements.txt        # Python依赖
├── start.sh               # 启动脚本(Linux/Mac)
├── start.bat              # 启动脚本(Windows)
└── README.md              # 项目说明
```

## 注意事项

1. **首次运行**: 第一次运行可能需要下载Qwen模型文件，请确保网络连接稳定
2. **GPU支持**: 如果有CUDA环境，系统会自动使用GPU加速训练
3. **前端开发**: 前端部分需要单独开发，已预留接口和设计规范
4. **生产部署**: 生产环境建议使用MySQL/PostgreSQL替换SQLite

## 故障排除

### 常见问题

1. **Redis连接失败**: 确保Redis服务正在运行
2. **Qwen模型下载慢**: 配置Hugging Face镜像
3. **GPU内存不足**: 减小batch_size参数
4. **训练任务卡住**: 检查Celery Worker状态

---

**注意**: 这是一个研究项目，重点在于模型训练部分的实现。前端界面将由专门的前端开发人员完成。
