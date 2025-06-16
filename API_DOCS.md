# TimeVis API 接口文档

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **响应格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "message": "操作成功",
  "data": {},
  "timestamp": "2025-06-16T10:00:00Z"
}
```

### 错误响应
```json
{
  "error": "错误描述",
  "code": 400,
  "timestamp": "2025-06-16T10:00:00Z"
}
```

## 接口列表

### 1. 系统管理

#### 1.1 健康检查
- **接口**: `GET /health`
- **描述**: 检查系统健康状态
- **参数**: 无

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-16T10:00:00Z",
  "version": "1.0.0"
}
```

#### 1.2 系统统计
- **接口**: `GET /stats`
- **描述**: 获取系统统计信息
- **参数**: 无

**响应示例**:
```json
{
  "total_tasks": 15,
  "completed_tasks": 12,
  "running_tasks": 2,
  "failed_tasks": 1,
  "total_models": 8,
  "total_datasets": 5,
  "qwen_models": 4,
  "lstm_models": 4,
  "recent_tasks": [
    {
      "id": 1,
      "task_type": "training",
      "status": "completed",
      "created_at": "2025-06-16T09:00:00Z"
    }
  ]
}
```

### 2. 数据管理

#### 2.1 上传数据文件
- **接口**: `POST /upload`
- **描述**: 上传CSV、Excel或JSON格式的数据文件
- **Content-Type**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| file | File | 是 | 数据文件 |
| data_type | String | 是 | 数据类型: weather/electricity/traffic |
| dataset_name | String | 否 | 数据集名称 |

**响应示例**:
```json
{
  "message": "文件上传成功",
  "dataset_id": 1,
  "file_path": "/uploads/20250616_100000_weather.csv",
  "analysis": {
    "shape": [1000, 4],
    "columns": ["datetime", "temperature", "humidity", "pressure"],
    "numeric_columns": ["temperature", "humidity", "pressure"],
    "missing_values": {
      "temperature": 0,
      "humidity": 2,
      "pressure": 1
    }
  },
  "validation": {
    "target_column_exists": true,
    "has_numeric_data": true,
    "low_missing_ratio": true,
    "sufficient_length": true,
    "reasonable_outliers": true
  },
  "target_column": "temperature"
}
```

#### 2.2 获取数据集列表
- **接口**: `GET /datasets`
- **描述**: 获取所有数据集列表
- **参数**: 无

**响应示例**:
```json
{
  "datasets": [
    {
      "id": 1,
      "name": "天气数据",
      "data_type": "weather",
      "file_path": "/uploads/weather.csv",
      "file_size": 102400,
      "num_samples": 1000,
      "num_features": 4,
      "time_range_start": "2020-01-01T00:00:00Z",
      "time_range_end": "2020-12-31T23:00:00Z",
      "uploaded_at": "2025-06-16T09:00:00Z"
    }
  ]
}
```

#### 2.3 获取数据集详情
- **接口**: `GET /datasets/{dataset_id}`
- **描述**: 获取指定数据集的详细信息
- **参数**: 
  - `dataset_id`: 数据集ID

**响应示例**:
```json
{
  "dataset": {
    "id": 1,
    "name": "天气数据",
    "data_type": "weather",
    "file_path": "/uploads/weather.csv",
    "num_samples": 1000,
    "num_features": 4,
    "uploaded_at": "2025-06-16T09:00:00Z"
  },
  "preview": [
    {
      "datetime": "2020-01-01T00:00:00Z",
      "temperature": 20.5,
      "humidity": 65.2,
      "pressure": 1013.2
    }
  ],
  "columns": ["datetime", "temperature", "humidity", "pressure"],
  "shape": [1000, 4]
}
```

#### 2.4 生成示例数据
- **接口**: `POST /sample-data`
- **描述**: 生成指定类型的示例数据
- **Content-Type**: `application/json`

**请求参数**:
```json
{
  "data_type": "weather",  // weather/electricity/traffic
  "num_samples": 1000      // 样本数量
}
```

**响应示例**:
```json
{
  "message": "示例数据生成成功",
  "dataset_id": 2,
  "file_path": "/uploads/samples/sample_weather_20250616.csv",
  "preview": [
    {
      "datetime": "2020-01-01T00:00:00Z",
      "temperature": 20.5,
      "humidity": 65.2,
      "pressure": 1013.2
    }
  ]
}
```

### 3. 模型训练

#### 3.1 启动训练任务
- **接口**: `POST /train`
- **描述**: 启动模型训练任务
- **Content-Type**: `application/json`

**请求参数**:
```json
{
  "dataset_id": 1,           // 数据集ID
  "model_type": "qwen",      // 模型类型: qwen/lstm
  "data_type": "weather",    // 数据类型: weather/electricity/traffic
  "model_config": {          // 模型配置
    // Qwen模型配置
    "model_name": "Qwen/Qwen2.5-7B-Instruct",
    "max_length": 512,
    "num_epochs": 3,
    "learning_rate": 5e-5,
    "batch_size": 4,
    "sequence_length": 10,
    "lora_r": 8,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    
    // LSTM模型配置
    "hidden_size": 64,
    "num_layers": 2,
    "dropout": 0.2,
    "patience": 10
  }
}
```

**响应示例**:
```json
{
  "message": "训练任务已启动",
  "task_id": 1,
  "status": "pending"
}
```

#### 3.2 获取模型列表
- **接口**: `GET /models`
- **描述**: 获取所有可用模型列表
- **参数**: 无

**响应示例**:
```json
{
  "models": [
    {
      "id": 1,
      "name": "qwen_weather_1",
      "model_type": "qwen",
      "data_type": "weather",
      "model_path": "/models/qwen_weather_1",
      "validation_mse": 0.001234,
      "validation_mae": 0.023456,
      "validation_rmse": 0.035123,
      "created_at": "2025-06-16T09:00:00Z",
      "is_active": true
    }
  ]
}
```

#### 3.3 获取模型详情
- **接口**: `GET /models/{model_id}`
- **描述**: 获取指定模型的详细信息
- **参数**: 
  - `model_id`: 模型ID

**响应示例**:
```json
{
  "id": 1,
  "name": "qwen_weather_1",
  "model_type": "qwen",
  "data_type": "weather",
  "model_path": "/models/qwen_weather_1",
  "training_task_id": 1,
  "training_parameters": {
    "num_epochs": 3,
    "learning_rate": 5e-5,
    "sequence_length": 10
  },
  "validation_mse": 0.001234,
  "validation_mae": 0.023456,
  "validation_rmse": 0.035123,
  "created_at": "2025-06-16T09:00:00Z",
  "updated_at": "2025-06-16T09:30:00Z",
  "is_active": true
}
```

#### 3.4 删除模型
- **接口**: `DELETE /models/{model_id}`
- **描述**: 删除指定模型（软删除）
- **参数**: 
  - `model_id`: 模型ID

**响应示例**:
```json
{
  "message": "模型已删除"
}
```

### 4. 任务管理

#### 4.1 获取任务列表
- **接口**: `GET /tasks`
- **描述**: 获取任务列表，支持分页和筛选
- **参数**: 
  - `page`: 页码（默认1）
  - `per_page`: 每页数量（默认20）
  - `task_type`: 任务类型筛选（training/prediction/comparison）
  - `status`: 状态筛选（pending/running/completed/failed）

**请求示例**:
```
GET /tasks?page=1&per_page=10&task_type=training&status=completed
```

**响应示例**:
```json
{
  "tasks": [
    {
      "id": 1,
      "task_type": "training",
      "data_type": "weather",
      "model_type": "qwen",
      "status": "completed",
      "progress": 1.0,
      "parameters": {
        "dataset_id": 1,
        "model_config": {}
      },
      "mse": 0.001234,
      "mae": 0.023456,
      "rmse": 0.035123,
      "created_at": "2025-06-16T09:00:00Z",
      "started_at": "2025-06-16T09:01:00Z",
      "completed_at": "2025-06-16T09:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 4.2 获取任务详情
- **接口**: `GET /tasks/{task_id}`
- **描述**: 获取指定任务的详细信息
- **参数**: 
  - `task_id`: 任务ID

**响应示例**:
```json
{
  "id": 1,
  "task_type": "training",
  "data_type": "weather",
  "model_type": "qwen",
  "status": "completed",
  "progress": 1.0,
  "parameters": {
    "dataset_id": 1,
    "model_config": {
      "num_epochs": 3,
      "learning_rate": 5e-5
    }
  },
  "data_file_path": "/uploads/weather.csv",
  "model_file_path": "/models/qwen_weather_1",
  "result_file_path": "/results/task_1_results.json",
  "mse": 0.001234,
  "mae": 0.023456,
  "rmse": 0.035123,
  "created_at": "2025-06-16T09:00:00Z",
  "started_at": "2025-06-16T09:01:00Z",
  "completed_at": "2025-06-16T09:30:00Z",
  "error_message": null,
  "task_results": {
    // 如果任务完成且有结果文件，包含详细结果
    "model_type": "qwen",
    "metrics": {
      "mse": 0.001234,
      "mae": 0.023456,
      "rmse": 0.035123
    },
    "predictions": [0.123, 0.456, 0.789],
    "actuals": [0.120, 0.450, 0.785]
  }
}
```

#### 4.3 取消任务
- **接口**: `POST /tasks/{task_id}/cancel`
- **描述**: 取消正在执行或等待中的任务
- **参数**: 
  - `task_id`: 任务ID

**响应示例**:
```json
{
  "message": "任务已取消"
}
```

### 5. 预测分析

#### 5.1 启动预测任务
- **接口**: `POST /predict`
- **描述**: 使用训练好的模型进行预测
- **Content-Type**: `application/json`

**请求参数**:
```json
{
  "model_id": 1,                                    // 模型ID
  "input_sequence": [20.1, 19.8, 21.2, 22.5, 23.1] // 输入序列
}
```

**响应示例**:
```json
{
  "message": "预测任务已启动",
  "task_id": 2,
  "status": "pending"
}
```

#### 5.2 模型比较
- **接口**: `POST /compare`
- **描述**: 比较两个模型的性能
- **Content-Type**: `application/json`

**请求参数**:
```json
{
  "qwen_model_id": 1,      // Qwen模型ID
  "lstm_model_id": 2,      // LSTM模型ID
  "test_dataset_id": 3     // 测试数据集ID
}
```

**响应示例**:
```json
{
  "message": "模型比较任务已启动",
  "task_id": 3,
  "status": "pending"
}
```

### 6. 文件下载

#### 6.1 下载任务结果
- **接口**: `GET /download/{task_id}/results`
- **描述**: 下载任务结果文件
- **参数**: 
  - `task_id`: 任务ID

**响应**: 文件下载（JSON格式）

## 状态码说明

| 状态码 | 描述 |
|-------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 任务状态说明

| 状态 | 描述 |
|-----|------|
| pending | 等待执行 |
| running | 正在执行 |
| completed | 执行完成 |
| failed | 执行失败 |
| cancelled | 已取消 |

## 支持的数据类型

| 类型 | 描述 | 主要字段 |
|-----|------|---------|
| weather | 天气数据 | temperature, humidity, pressure |
| electricity | 电力数据 | load, voltage, frequency |
| traffic | 交通数据 | flow, speed, occupancy |

## 支持的模型类型

| 类型 | 描述 | 特点 |
|-----|------|------|
| qwen | Qwen大模型 | 基于Transformer，使用GPT回归方法 |
| lstm | LSTM模型 | 传统深度学习模型，训练快速 |

## 错误处理

所有API接口都遵循统一的错误处理格式：

```json
{
  "error": "具体错误描述",
  "code": 400,
  "timestamp": "2025-06-16T10:00:00Z"
}
```

常见错误：
- 文件格式不支持
- 数据集不存在
- 模型不存在
- 任务执行失败
- 参数验证错误

## 实时状态监控

对于长时间运行的任务（如训练），建议前端实现轮询机制：

```javascript
// 轮询任务状态示例
async function pollTaskStatus(taskId) {
  const response = await fetch(`/api/tasks/${taskId}`);
  const task = await response.json();
  
  if (task.status === 'completed') {
    // 任务完成处理
    return task;
  } else if (task.status === 'failed') {
    // 任务失败处理
    throw new Error(task.error_message);
  } else {
    // 继续轮询
    setTimeout(() => pollTaskStatus(taskId), 2000);
  }
}
```

## WebSocket 支持（待实现）

未来版本计划支持WebSocket实时推送任务状态更新：

```javascript
// WebSocket连接示例（规划中）
const ws = new WebSocket('ws://localhost:5000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'task_update') {
    updateTaskStatus(data.task_id, data.status, data.progress);
  }
};
```
