import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dataAPI } from '@/api'
import type { Dataset, PaginationParams } from '@/types/api'

export const useDataStore = defineStore('data', () => {
  const datasets = ref<Dataset[]>([])
  const currentDataset = ref<Dataset | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)

  // 计算属性
  const hasDatasets = computed(() => datasets.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 获取数据集列表
  const fetchDatasets = async (params?: PaginationParams) => {
    loading.value = true
    try {
      const response = await dataAPI.getDatasets({
        page: currentPage.value,
        per_page: pageSize.value,
        ...params
      })
      datasets.value = response.data.items
      total.value = response.data.total
      currentPage.value = response.data.page
    } catch (error) {
      console.error('Failed to fetch datasets:', error)
    } finally {
      loading.value = false
    }
  }

  // 上传数据集
  const uploadDataset = async (formData: FormData) => {
    loading.value = true
    try {
      const response = await dataAPI.uploadDataset(formData)
      await fetchDatasets() // 重新获取列表
      return response.data
    } catch (error) {
      console.error('Failed to upload dataset:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取数据集详情
  const fetchDataset = async (id: number) => {
    loading.value = true
    try {
      const response = await dataAPI.getDataset(id)
      currentDataset.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch dataset:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除数据集
  const deleteDataset = async (id: number) => {
    loading.value = true
    try {
      await dataAPI.deleteDataset(id)
      await fetchDatasets() // 重新获取列表
    } catch (error) {
      console.error('Failed to delete dataset:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 预览数据集
  const previewDataset = async (id: number, limit = 10) => {
    try {
      const response = await dataAPI.previewDataset(id, limit)
      return response.data
    } catch (error) {
      console.error('Failed to preview dataset:', error)
      throw error
    }
  }

  // 获取数据集统计
  const getDatasetStats = async (id: number) => {
    try {
      const response = await dataAPI.getDatasetStats(id)
      return response.data
    } catch (error) {
      console.error('Failed to get dataset stats:', error)
      throw error
    }
  }

  // 重置状态
  const reset = () => {
    datasets.value = []
    currentDataset.value = null
    loading.value = false
    total.value = 0
    currentPage.value = 1
  }

  return {
    // 状态
    datasets,
    currentDataset,
    loading,
    total,
    currentPage,
    pageSize,
    
    // 计算属性
    hasDatasets,
    totalPages,
    
    // 方法
    fetchDatasets,
    uploadDataset,
    fetchDataset,
    deleteDataset,
    previewDataset,
    getDatasetStats,
    reset
  }
})
