import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelAPI } from '@/api'
import type { Model, TrainingRequest, PaginationParams } from '@/types/api'

export const useModelStore = defineStore('model', () => {
  const models = ref<Model[]>([])
  const currentModel = ref<Model | null>(null)
  const loading = ref(false)
  const training = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)

  // 计算属性
  const hasModels = computed(() => models.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const trainingModels = computed(() => 
    models.value.filter(model => model.status === 'training')
  )
  const completedModels = computed(() => 
    models.value.filter(model => model.status === 'completed')
  )

  // 获取模型列表
  const fetchModels = async (params?: PaginationParams) => {
    loading.value = true
    try {
      const response = await modelAPI.getModels({
        page: currentPage.value,
        per_page: pageSize.value,
        ...params
      })
      models.value = response.data.items
      total.value = response.data.total
      currentPage.value = response.data.page
    } catch (error) {
      console.error('Failed to fetch models:', error)
    } finally {
      loading.value = false
    }
  }

  // 训练模型
  const trainModel = async (data: TrainingRequest) => {
    training.value = true
    try {
      const response = await modelAPI.trainModel(data)
      await fetchModels() // 重新获取列表
      return response.data
    } catch (error) {
      console.error('Failed to train model:', error)
      throw error
    } finally {
      training.value = false
    }
  }

  // 获取模型详情
  const fetchModel = async (id: number) => {
    loading.value = true
    try {
      const response = await modelAPI.getModel(id)
      currentModel.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch model:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除模型
  const deleteModel = async (id: number) => {
    loading.value = true
    try {
      await modelAPI.deleteModel(id)
      await fetchModels() // 重新获取列表
    } catch (error) {
      console.error('Failed to delete model:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取模型训练日志
  const getModelLogs = async (id: number) => {
    try {
      const response = await modelAPI.getModelLogs(id)
      return response.data
    } catch (error) {
      console.error('Failed to get model logs:', error)
      throw error
    }
  }

  // 下载模型
  const downloadModel = async (id: number) => {
    try {
      const response = await modelAPI.downloadModel(id)
      return response.data
    } catch (error) {
      console.error('Failed to download model:', error)
      throw error
    }
  }

  // 重置状态
  const reset = () => {
    models.value = []
    currentModel.value = null
    loading.value = false
    training.value = false
    total.value = 0
    currentPage.value = 1
  }

  return {
    // 状态
    models,
    currentModel,
    loading,
    training,
    total,
    currentPage,
    pageSize,
    
    // 计算属性
    hasModels,
    totalPages,
    trainingModels,
    completedModels,
    
    // 方法
    fetchModels,
    trainModel,
    fetchModel,
    deleteModel,
    getModelLogs,
    downloadModel,
    reset
  }
})
