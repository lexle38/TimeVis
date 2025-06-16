import request from '@/utils/request'
import type {
  Dataset,
  DataUploadResponse,
  Model,
  TrainingRequest,
  PredictionResult,
  PredictionRequest,
  Task,
  ModelComparison,
  ComparisonRequest,
  PaginatedResponse,
  PaginationParams
} from '@/types/api'

// 数据管理相关API
export const dataAPI = {
  // 获取数据集列表
  getDatasets(params?: PaginationParams) {
    return request.get<PaginatedResponse<Dataset>>('/datasets', { params })
  },

  // 上传数据集
  uploadDataset(formData: FormData) {
    return request.post<DataUploadResponse>('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取数据集详情
  getDataset(id: number) {
    return request.get<Dataset>(`/datasets/${id}`)
  },

  // 删除数据集
  deleteDataset(id: number) {
    return request.delete(`/datasets/${id}`)
  },

  // 预览数据集
  previewDataset(id: number, limit?: number) {
    return request.get(`/datasets/${id}/preview`, {
      params: { limit }
    })
  },

  // 数据集统计信息
  getDatasetStats(id: number) {
    return request.get(`/datasets/${id}/stats`)
  }
}

// 模型相关API
export const modelAPI = {
  // 获取模型列表
  getModels(params?: PaginationParams) {
    return request.get<PaginatedResponse<Model>>('/models', { params })
  },

  // 训练模型
  trainModel(data: TrainingRequest) {
    return request.post<{ task_id: string }>('/models/train', data)
  },

  // 获取模型详情
  getModel(id: number) {
    return request.get<Model>(`/models/${id}`)
  },

  // 删除模型
  deleteModel(id: number) {
    return request.delete(`/models/${id}`)
  },

  // 获取模型训练日志
  getModelLogs(id: number) {
    return request.get(`/models/${id}/logs`)
  },

  // 下载模型
  downloadModel(id: number) {
    return request.get(`/models/${id}/download`, {
      responseType: 'blob'
    })
  }
}

// 预测相关API
export const predictionAPI = {
  // 获取预测结果列表
  getPredictions(params?: PaginationParams) {
    return request.get<PaginatedResponse<PredictionResult>>('/predictions', { params })
  },

  // 创建预测
  createPrediction(data: PredictionRequest) {
    return request.post<{ task_id: string }>('/predictions', data)
  },

  // 获取预测详情
  getPrediction(id: number) {
    return request.get<PredictionResult>(`/predictions/${id}`)
  },

  // 删除预测结果
  deletePrediction(id: number) {
    return request.delete(`/predictions/${id}`)
  },

  // 下载预测结果
  downloadPrediction(id: number) {
    return request.get(`/predictions/${id}/download`, {
      responseType: 'blob'
    })
  }
}

// 任务相关API
export const taskAPI = {
  // 获取任务列表
  getTasks(params?: PaginationParams) {
    return request.get<PaginatedResponse<Task>>('/tasks', { params })
  },

  // 获取任务详情
  getTask(id: string) {
    return request.get<Task>(`/tasks/${id}`)
  },

  // 取消任务
  cancelTask(id: string) {
    return request.post(`/tasks/${id}/cancel`)
  },

  // 获取任务日志
  getTaskLogs(id: string) {
    return request.get(`/tasks/${id}/logs`)
  }
}

// 模型比较相关API
export const comparisonAPI = {
  // 获取比较结果列表
  getComparisons(params?: PaginationParams) {
    return request.get<PaginatedResponse<ModelComparison>>('/comparisons', { params })
  },

  // 创建模型比较
  createComparison(data: ComparisonRequest) {
    return request.post<{ task_id: string }>('/comparisons', data)
  },

  // 获取比较详情
  getComparison(id: number) {
    return request.get<ModelComparison>(`/comparisons/${id}`)
  },

  // 删除比较结果
  deleteComparison(id: number) {
    return request.delete(`/comparisons/${id}`)
  }
}

// 系统相关API
export const systemAPI = {
  // 获取系统状态
  getSystemStatus() {
    return request.get('/system/status')
  },

  // 获取系统统计
  getSystemStats() {
    return request.get('/system/stats')
  }
}
