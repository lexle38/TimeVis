// 数据相关的接口类型定义
export interface Dataset {
  id: number
  name: string
  filename: string
  columns: string[]
  rows: number
  size: number
  upload_time: string
  description?: string
}

export interface DataUploadResponse {
  message: string
  dataset_id: number
  info: {
    columns: string[]
    rows: number
    size: number
  }
}

// 模型相关的接口类型定义
export interface Model {
  id: number
  name: string
  model_type: 'qwen' | 'lstm'
  dataset_id: number
  dataset_name: string
  status: 'training' | 'completed' | 'failed'
  created_time: string
  training_time?: number
  parameters: Record<string, any>
  metrics?: {
    mse?: number
    mae?: number
    rmse?: number
    r2?: number
  }
}

export interface TrainingRequest {
  model_name: string
  model_type: 'qwen' | 'lstm'
  dataset_id: number
  target_column: string
  sequence_length?: number
  test_size?: number
  parameters?: Record<string, any>
}

// 预测相关的接口类型定义
export interface PredictionResult {
  id: number
  model_id: number
  model_name: string
  dataset_id: number
  dataset_name: string
  prediction_steps: number
  created_time: string
  results: {
    predictions: number[]
    timestamps?: string[]
    actual_values?: number[]
    metrics?: {
      mse?: number
      mae?: number
      rmse?: number
    }
  }
}

export interface PredictionRequest {
  model_id: number
  dataset_id?: number
  prediction_steps: number
  input_data?: number[]
}

// 任务相关的接口类型定义
export interface Task {
  id: string
  name: string
  type: 'training' | 'prediction' | 'comparison'
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  created_time: string
  started_time?: string
  completed_time?: string
  error_message?: string
  result?: any
}

// 模型比较相关的接口类型定义
export interface ModelComparison {
  id: number
  name: string
  models: number[]
  dataset_id: number
  created_time: string
  results: {
    model_performances: Array<{
      model_id: number
      model_name: string
      metrics: {
        mse: number
        mae: number
        rmse: number
        r2?: number
      }
    }>
    best_model: {
      model_id: number
      model_name: string
      metric: string
      value: number
    }
  }
}

export interface ComparisonRequest {
  comparison_name: string
  model_ids: number[]
  dataset_id: number
  test_size?: number
}

// API响应的通用格式
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
  error?: string
}

// 分页相关
export interface PaginationParams {
  page?: number
  per_page?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}
