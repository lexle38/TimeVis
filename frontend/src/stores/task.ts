import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { taskAPI } from '@/api'
import type { Task, PaginationParams } from '@/types/api'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)

  // 计算属性
  const hasTasks = computed(() => tasks.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const runningTasks = computed(() => 
    tasks.value.filter(task => task.status === 'running')
  )
  const pendingTasks = computed(() => 
    tasks.value.filter(task => task.status === 'pending')
  )
  const completedTasks = computed(() => 
    tasks.value.filter(task => task.status === 'completed')
  )
  const failedTasks = computed(() => 
    tasks.value.filter(task => task.status === 'failed')
  )

  // 获取任务列表
  const fetchTasks = async (params?: PaginationParams) => {
    loading.value = true
    try {
      const response = await taskAPI.getTasks({
        page: currentPage.value,
        per_page: pageSize.value,
        ...params
      })
      tasks.value = response.data.items
      total.value = response.data.total
      currentPage.value = response.data.page
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取任务详情
  const fetchTask = async (id: string) => {
    loading.value = true
    try {
      const response = await taskAPI.getTask(id)
      currentTask.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch task:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 取消任务
  const cancelTask = async (id: string) => {
    try {
      await taskAPI.cancelTask(id)
      await fetchTasks() // 重新获取列表
    } catch (error) {
      console.error('Failed to cancel task:', error)
      throw error
    }
  }

  // 获取任务日志
  const getTaskLogs = async (id: string) => {
    try {
      const response = await taskAPI.getTaskLogs(id)
      return response.data
    } catch (error) {
      console.error('Failed to get task logs:', error)
      throw error
    }
  }

  // 更新单个任务状态
  const updateTask = (updatedTask: Task) => {
    const index = tasks.value.findIndex(task => task.id === updatedTask.id)
    if (index !== -1) {
      tasks.value[index] = updatedTask
    }
    if (currentTask.value && currentTask.value.id === updatedTask.id) {
      currentTask.value = updatedTask
    }
  }

  // 轮询运行中的任务状态
  const pollRunningTasks = async () => {
    const runningTaskIds = runningTasks.value.map(task => task.id)
    if (runningTaskIds.length === 0) return

    try {
      for (const taskId of runningTaskIds) {
        const task = await fetchTask(taskId)
        updateTask(task)
      }
    } catch (error) {
      console.error('Failed to poll task status:', error)
    }
  }

  // 重置状态
  const reset = () => {
    tasks.value = []
    currentTask.value = null
    loading.value = false
    total.value = 0
    currentPage.value = 1
  }

  return {
    // 状态
    tasks,
    currentTask,
    loading,
    total,
    currentPage,
    pageSize,
    
    // 计算属性
    hasTasks,
    totalPages,
    runningTasks,
    pendingTasks,
    completedTasks,
    failedTasks,
    
    // 方法
    fetchTasks,
    fetchTask,
    cancelTask,
    getTaskLogs,
    updateTask,
    pollRunningTasks,
    reset
  }
})
