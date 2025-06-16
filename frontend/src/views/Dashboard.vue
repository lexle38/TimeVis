<template>
  <div class="dashboard">
    <!-- 系统概览 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="数据集总数"
            :value="dataStats.totalDatasets"
            :precision="0"
          >
            <template #prefix>
              <el-icon class="stat-icon"><DataBoard /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="训练模型数"
            :value="modelStats.totalModels"
            :precision="0"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Setting /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="预测任务数"
            :value="predictionStats.totalPredictions"
            :precision="0"
          >
            <template #prefix>
              <el-icon class="stat-icon"><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="运行中任务"
            :value="taskStats.runningTasks"
            :precision="0"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Monitor /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-section">
      <!-- 模型性能对比图 -->
      <el-col :span="12">
        <el-card title="模型性能对比" class="chart-card">
          <div ref="modelPerformanceChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 任务状态分布图 -->
      <el-col :span="12">
        <el-card title="任务状态分布" class="chart-card">
          <div ref="taskStatusChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-section">
      <!-- 预测准确度趋势 -->
      <el-col :span="24">
        <el-card title="预测准确度趋势" class="chart-card">
          <div ref="accuracyTrendChart" class="chart-container large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="20" class="recent-activities">
      <el-col :span="12">
        <el-card title="最近训练的模型" class="activity-card">
          <div v-if="recentModels.length === 0" class="empty-state">
            <el-empty description="暂无最近训练的模型" />
          </div>
          <div v-else>
            <div 
              v-for="model in recentModels" 
              :key="model.id" 
              class="activity-item"
            >
              <div class="activity-content">
                <div class="activity-title">
                  <el-tag :type="getModelTypeColor(model.model_type)" size="small">
                    {{ model.model_type.toUpperCase() }}
                  </el-tag>
                  <span class="model-name">{{ model.name }}</span>
                </div>
                <div class="activity-meta">
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ formatTime(model.created_time) }}
                  </span>
                  <span class="meta-item">
                    <el-icon><DataBoard /></el-icon>
                    {{ model.dataset_name }}
                  </span>
                </div>
              </div>
              <div class="activity-status">
                <el-tag 
                  :type="getStatusColor(model.status)" 
                  size="small"
                >
                  {{ getStatusText(model.status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card title="最近的预测结果" class="activity-card">
          <div v-if="recentPredictions.length === 0" class="empty-state">
            <el-empty description="暂无最近的预测结果" />
          </div>
          <div v-else>
            <div 
              v-for="prediction in recentPredictions" 
              :key="prediction.id" 
              class="activity-item"
            >
              <div class="activity-content">
                <div class="activity-title">
                  <span class="prediction-title">{{ prediction.model_name }}</span>
                </div>
                <div class="activity-meta">
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ formatTime(prediction.created_time) }}
                  </span>
                  <span class="meta-item">
                    <el-icon><TrendCharts /></el-icon>
                    {{ prediction.prediction_steps }} 步预测
                  </span>
                </div>
              </div>
              <div class="activity-action">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="viewPrediction(prediction.id)"
                >
                  查看
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { systemAPI, modelAPI, dataAPI, predictionAPI } from '@/api'
import type { Model, PredictionResult } from '@/types/api'

const router = useRouter()

// 图表引用
const modelPerformanceChart = ref<HTMLElement>()
const taskStatusChart = ref<HTMLElement>()
const accuracyTrendChart = ref<HTMLElement>()

// 数据状态
const dataStats = reactive({
  totalDatasets: 0
})

const modelStats = reactive({
  totalModels: 0
})

const predictionStats = reactive({
  totalPredictions: 0
})

const taskStats = reactive({
  runningTasks: 0
})

const recentModels = ref<Model[]>([])
const recentPredictions = ref<PredictionResult[]>([])

// 初始化图表
const initCharts = () => {
  // 模型性能对比图
  if (modelPerformanceChart.value) {
    const chart = echarts.init(modelPerformanceChart.value)
    chart.setOption({
      title: {
        text: '模型性能对比 (MSE)',
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      xAxis: {
        type: 'category',
        data: ['LSTM-1', 'LSTM-2', 'Qwen-1', 'Qwen-2']
      },
      yAxis: {
        type: 'value',
        name: 'MSE'
      },
      series: [{
        data: [0.12, 0.08, 0.15, 0.09],
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }]
    })
  }

  // 任务状态分布图
  if (taskStatusChart.value) {
    const chart = echarts.init(taskStatusChart.value)
    chart.setOption({
      title: {
        text: '任务状态分布',
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'item'
      },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 2, name: '运行中' },
          { value: 1, name: '等待中' },
          { value: 15, name: '已完成' },
          { value: 2, name: '失败' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }

  // 预测准确度趋势图
  if (accuracyTrendChart.value) {
    const chart = echarts.init(accuracyTrendChart.value)
    chart.setOption({
      title: {
        text: '预测准确度趋势',
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['LSTM', 'Qwen'],
        top: 30
      },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: {
        type: 'value',
        name: 'R²分数',
        min: 0,
        max: 1
      },
      series: [
        {
          name: 'LSTM',
          type: 'line',
          data: [0.85, 0.87, 0.89, 0.91, 0.88, 0.92],
          smooth: true
        },
        {
          name: 'Qwen',
          type: 'line',
          data: [0.82, 0.84, 0.86, 0.89, 0.90, 0.91],
          smooth: true
        }
      ]
    })
  }
}

// 获取系统统计数据
const fetchSystemStats = async () => {
  try {
    const response = await systemAPI.getSystemStats()
    const stats = response.data
    
    dataStats.totalDatasets = stats.datasets || 0
    modelStats.totalModels = stats.models || 0
    predictionStats.totalPredictions = stats.predictions || 0
    taskStats.runningTasks = stats.running_tasks || 0
  } catch (error) {
    console.error('Failed to fetch system stats:', error)
  }
}

// 获取最近的模型
const fetchRecentModels = async () => {
  try {
    const response = await modelAPI.getModels({ per_page: 5 })
    recentModels.value = response.data.items
  } catch (error) {
    console.error('Failed to fetch recent models:', error)
  }
}

// 获取最近的预测结果
const fetchRecentPredictions = async () => {
  try {
    const response = await predictionAPI.getPredictions({ per_page: 5 })
    recentPredictions.value = response.data.items
  } catch (error) {
    console.error('Failed to fetch recent predictions:', error)
  }
}

// 工具函数
const getModelTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    lstm: 'primary',
    qwen: 'success'
  }
  return colors[type] || 'info'
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    training: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    training: '训练中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

const viewPrediction = (id: number) => {
  router.push(`/prediction?id=${id}`)
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    fetchSystemStats(),
    fetchRecentModels(),
    fetchRecentPredictions()
  ])
  
  // 图表需要在DOM渲染后初始化
  setTimeout(() => {
    initCharts()
  }, 100)
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.overview-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
}

.stat-icon {
  font-size: 24px;
  color: #409eff;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.chart-container.large {
  height: 350px;
}

.recent-activities {
  margin-bottom: 20px;
}

.activity-card {
  height: 400px;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-content {
  flex: 1;
}

.activity-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.model-name,
.prediction-title {
  font-weight: 500;
  color: #303133;
}

.activity-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.activity-status,
.activity-action {
  flex-shrink: 0;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
</style>
