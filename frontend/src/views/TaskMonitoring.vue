<template>
  <div class="task-monitoring">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>任务监控</h2>
        <p>监控和管理系统中的各种任务</p>
      </div>
      <div class="header-right">
        <el-button 
          @click="refreshTasks"
          :loading="loading"
        >
          刷新
        </el-button>
      </div>
    </div>

    <!-- 任务统计 -->
    <el-row :gutter="20" class="task-stats">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="运行中"
            :value="runningTasks.length"
            :precision="0"
          >
            <template #prefix>
              <el-icon style="color: #F56C6C"><Loading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="等待中"
            :value="pendingTasks.length"
            :precision="0"
          >
            <template #prefix>
              <el-icon style="color: #E6A23C"><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="已完成"
            :value="completedTasks.length"
            :precision="0"
          >
            <template #prefix>
              <el-icon style="color: #67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="失败"
            :value="failedTasks.length"
            :precision="0"
          >
            <template #prefix>
              <el-icon style="color: #F56C6C"><CircleClose /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <div class="header-actions">
            <el-select v-model="filterStatus" placeholder="筛选状态" style="width: 120px; margin-right: 10px;" clearable>
              <el-option label="运行中" value="running" />
              <el-option label="等待中" value="pending" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-select v-model="filterType" placeholder="筛选类型" style="width: 120px; margin-right: 10px;" clearable>
              <el-option label="模型训练" value="training" />
              <el-option label="预测分析" value="prediction" />
              <el-option label="模型比较" value="comparison" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table 
        :data="filteredTasks" 
        v-loading="loading"
        stripe
        @row-click="viewTask"
        style="cursor: pointer;"
      >
        <el-table-column prop="id" label="任务ID" width="200" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="type" label="任务类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTaskTypeColor(row.type)" size="small">
              {{ getTaskTypeName(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.progress" 
              :status="row.status === 'failed' ? 'exception' : (row.status === 'completed' ? 'success' : undefined)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="viewTaskDetails(row)"
            >
              详情
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click.stop="cancelTask(row)"
              :disabled="row.status !== 'running' && row.status !== 'pending'"
            >
              取消
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click.stop="viewTaskLogs(row)"
            >
              日志
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      :title="`任务详情 - ${currentTask?.name}`"
      width="70%"
      top="5vh"
    >
      <div v-if="currentTask">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="任务ID">{{ currentTask.id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ currentTask.name }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag :type="getTaskTypeColor(currentTask.type)">
              {{ getTaskTypeName(currentTask.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(currentTask.status)">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">
            <el-progress 
              :percentage="currentTask.progress" 
              :status="currentTask.status === 'failed' ? 'exception' : (currentTask.status === 'completed' ? 'success' : undefined)"
            />
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentTask.created_time) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间" v-if="currentTask.started_time">
            {{ formatTime(currentTask.started_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间" v-if="currentTask.completed_time">
            {{ formatTime(currentTask.completed_time) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 错误信息 -->
        <div v-if="currentTask.error_message" class="error-section">
          <h4>错误信息</h4>
          <el-alert
            :title="currentTask.error_message"
            type="error"
            :closable="false"
            show-icon
          />
        </div>

        <!-- 任务结果 -->
        <div v-if="currentTask.result" class="result-section">
          <h4>任务结果</h4>
          <el-code-viewer :value="JSON.stringify(currentTask.result, null, 2)" />
        </div>
      </div>
    </el-dialog>

    <!-- 任务日志对话框 -->
    <el-dialog
      v-model="showLogsDialog"
      :title="`任务日志 - ${currentTask?.name}`"
      width="80%"
      top="5vh"
    >
      <div class="logs-container">
        <el-input
          v-model="taskLogs"
          type="textarea"
          :rows="20"
          readonly
          placeholder="暂无日志信息"
        />
      </div>
      
      <template #footer>
        <el-button @click="refreshTaskLogs">刷新日志</el-button>
        <el-button @click="showLogsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Clock, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import type { Task } from '@/types/api'

const taskStore = useTaskStore()

// 响应式数据
const filterStatus = ref('')
const filterType = ref('')
const showDetailsDialog = ref(false)
const showLogsDialog = ref(false)
const currentTask = ref<Task | null>(null)
const taskLogs = ref('')
let pollingTimer: number | null = null

// 计算属性
const tasks = computed(() => taskStore.tasks)
const loading = computed(() => taskStore.loading)
const total = computed(() => taskStore.total)
const currentPage = computed({
  get: () => taskStore.currentPage,
  set: (value) => taskStore.currentPage = value
})
const pageSize = computed({
  get: () => taskStore.pageSize,
  set: (value) => taskStore.pageSize = value
})

const runningTasks = computed(() => taskStore.runningTasks)
const pendingTasks = computed(() => taskStore.pendingTasks)
const completedTasks = computed(() => taskStore.completedTasks)
const failedTasks = computed(() => taskStore.failedTasks)

// 过滤后的任务
const filteredTasks = computed(() => {
  let result = tasks.value
  
  if (filterStatus.value) {
    result = result.filter(task => task.status === filterStatus.value)
  }
  
  if (filterType.value) {
    result = result.filter(task => task.type === filterType.value)
  }
  
  return result
})

// 查看任务详情
const viewTask = (task: Task) => {
  currentTask.value = task
  showDetailsDialog.value = true
}

const viewTaskDetails = (task: Task) => {
  viewTask(task)
}

// 取消任务
const cancelTask = async (task: Task) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消任务 "${task.name}" 吗？`,
      '取消确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await taskStore.cancelTask(task.id)
    ElMessage.success('任务已取消')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消任务失败')
    }
  }
}

// 查看任务日志
const viewTaskLogs = async (task: Task) => {
  currentTask.value = task
  showLogsDialog.value = true
  await refreshTaskLogs()
}

// 刷新任务日志
const refreshTaskLogs = async () => {
  if (!currentTask.value) return
  
  try {
    const logs = await taskStore.getTaskLogs(currentTask.value.id)
    taskLogs.value = logs || '暂无日志信息'
  } catch (error) {
    taskLogs.value = '获取日志失败'
  }
}

// 刷新任务列表
const refreshTasks = () => {
  taskStore.fetchTasks()
}

// 启动轮询
const startPolling = () => {
  pollingTimer = setInterval(() => {
    if (runningTasks.value.length > 0 || pendingTasks.value.length > 0) {
      taskStore.pollRunningTasks()
    }
  }, 3000) // 每3秒检查一次
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 工具函数
const getTaskTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    training: 'primary',
    prediction: 'success',
    comparison: 'warning'
  }
  return colors[type] || 'info'
}

const getTaskTypeName = (type: string) => {
  const names: Record<string, string> = {
    training: '模型训练',
    prediction: '预测分析',
    comparison: '模型比较'
  }
  return names[type] || type
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  taskStore.fetchTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.task-monitoring {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 4px 0;
  color: #303133;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.task-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
}

.task-list-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.error-section,
.result-section {
  margin-top: 20px;
}

.error-section h4,
.result-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.logs-container {
  font-family: 'Courier New', monospace;
}
</style>
