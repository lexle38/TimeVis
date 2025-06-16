<template>
  <div class="task-monitor-drawer">
    <div class="task-summary">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-statistic title="运行中" :value="runningTasks.length" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="等待中" :value="pendingTasks.length" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="已完成" :value="completedTasks.length" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="失败" :value="failedTasks.length" />
        </el-col>
      </el-row>
    </div>

    <el-divider />

    <div class="task-list">
      <div class="section-header">
        <h4>运行中的任务</h4>
        <el-button 
          type="primary" 
          size="small" 
          @click="refreshTasks"
          :loading="loading"
        >
          刷新
        </el-button>
      </div>

      <div v-if="runningTasks.length === 0" class="empty-state">
        <el-empty description="暂无运行中的任务" />
      </div>

      <el-card 
        v-for="task in runningTasks" 
        :key="task.id" 
        class="task-card"
        shadow="hover"
      >
        <div class="task-header">
          <div class="task-title">
            <el-tag :type="getTaskTypeColor(task.type)" size="small">
              {{ getTaskTypeName(task.type) }}
            </el-tag>
            <span class="task-name">{{ task.name }}</span>
          </div>
          <el-button 
            type="danger" 
            size="small" 
            plain
            @click="cancelTask(task.id)"
          >
            取消
          </el-button>
        </div>

        <div class="task-progress">
          <el-progress 
            :percentage="task.progress" 
            :status="task.status === 'failed' ? 'exception' : undefined"
            :stroke-width="8"
          />
          <span class="progress-text">{{ task.progress }}%</span>
        </div>

        <div class="task-info">
          <div class="info-item">
            <span class="label">创建时间:</span>
            <span class="value">{{ formatTime(task.created_time) }}</span>
          </div>
          <div class="info-item" v-if="task.started_time">
            <span class="label">开始时间:</span>
            <span class="value">{{ formatTime(task.started_time) }}</span>
          </div>
        </div>
      </el-card>

      <!-- 最近完成的任务 -->
      <div class="section-header" style="margin-top: 20px;">
        <h4>最近完成</h4>
      </div>

      <el-card 
        v-for="task in recentCompletedTasks" 
        :key="task.id" 
        class="task-card completed"
        shadow="hover"
      >
        <div class="task-header">
          <div class="task-title">
            <el-tag :type="getTaskTypeColor(task.type)" size="small">
              {{ getTaskTypeName(task.type) }}
            </el-tag>
            <span class="task-name">{{ task.name }}</span>
          </div>
          <el-tag 
            :type="task.status === 'completed' ? 'success' : 'danger'" 
            size="small"
          >
            {{ task.status === 'completed' ? '已完成' : '失败' }}
          </el-tag>
        </div>

        <div class="task-info">
          <div class="info-item">
            <span class="label">完成时间:</span>
            <span class="value">{{ formatTime(task.completed_time) }}</span>
          </div>
          <div class="info-item" v-if="task.error_message">
            <span class="label">错误信息:</span>
            <span class="value error">{{ task.error_message }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTaskStore } from '@/stores/task'
import { ElMessage } from 'element-plus'

const taskStore = useTaskStore()

// 计算属性
const loading = computed(() => taskStore.loading)
const runningTasks = computed(() => taskStore.runningTasks)
const pendingTasks = computed(() => taskStore.pendingTasks)
const completedTasks = computed(() => taskStore.completedTasks)
const failedTasks = computed(() => taskStore.failedTasks)

// 最近完成的任务（最多显示5个）
const recentCompletedTasks = computed(() => {
  const completed = [...taskStore.completedTasks, ...taskStore.failedTasks]
  return completed
    .sort((a, b) => new Date(b.completed_time || '').getTime() - new Date(a.completed_time || '').getTime())
    .slice(0, 5)
})

// 刷新任务列表
const refreshTasks = () => {
  taskStore.fetchTasks()
}

// 取消任务
const cancelTask = async (taskId: string) => {
  try {
    await taskStore.cancelTask(taskId)
    ElMessage.success('任务已取消')
  } catch (error) {
    ElMessage.error('取消任务失败')
  }
}

// 获取任务类型颜色
const getTaskTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    training: 'primary',
    prediction: 'success',
    comparison: 'warning'
  }
  return colors[type] || 'info'
}

// 获取任务类型名称
const getTaskTypeName = (type: string) => {
  const names: Record<string, string> = {
    training: '模型训练',
    prediction: '预测分析',
    comparison: '模型比较'
  }
  return names[type] || type
}

// 格式化时间
const formatTime = (timeStr: string | undefined) => {
  if (!timeStr) return '--'
  return new Date(timeStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.task-monitor-drawer {
  padding: 0;
}

.task-summary {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.task-list {
  max-height: 600px;
  overflow-y: auto;
}

.task-card {
  margin-bottom: 12px;
}

.task-card.completed {
  opacity: 0.8;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-name {
  font-weight: 500;
  color: #303133;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.task-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item {
  display: flex;
  font-size: 12px;
}

.info-item .label {
  color: #909399;
  min-width: 60px;
}

.info-item .value {
  color: #606266;
  flex: 1;
}

.info-item .value.error {
  color: #f56c6c;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}
</style>
