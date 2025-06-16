<template>
  <div class="prediction-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>预测分析</h2>
        <p>基于训练模型进行时间序列预测</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          @click="showPredictionDialog = true"
        >
          创建预测任务
        </el-button>
      </div>
    </div>

    <!-- 预测结果列表 -->
    <el-card class="prediction-list-card">
      <template #header>
        <div class="card-header">
          <span>预测结果</span>
          <div class="header-actions">
            <el-button 
              @click="refreshPredictions"
              :loading="loading"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="predictions" 
        v-loading="loading"
        stripe
        @row-click="viewPrediction"
        style="cursor: pointer;"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model_name" label="使用模型" />
        <el-table-column prop="dataset_name" label="数据集" />
        <el-table-column prop="prediction_steps" label="预测步数" width="100" />
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
              @click.stop="viewPredictionDetails(row)"
            >
              查看详情
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click.stop="downloadPrediction(row)"
            >
              下载
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click.stop="deletePrediction(row)"
            >
              删除
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

    <!-- 创建预测对话框 -->
    <el-dialog
      v-model="showPredictionDialog"
      title="创建预测任务"
      width="500px"
    >
      <el-form 
        :model="predictionForm" 
        label-width="120px"
      >
        <el-form-item label="选择模型">
          <el-select 
            v-model="predictionForm.model_id" 
            placeholder="选择训练好的模型"
            style="width: 100%"
          >
            <el-option 
              v-for="model in availableModels" 
              :key="model.id"
              :label="`${model.name} (${model.model_type.toUpperCase()})`"
              :value="model.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="预测步数">
          <el-input-number 
            v-model="predictionForm.prediction_steps" 
            :min="1"
            :max="100"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPredictionDialog = false">取消</el-button>
        <el-button type="primary" @click="createPrediction">
          创建预测
        </el-button>
      </template>
    </el-dialog>

    <!-- 预测详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      :title="`预测详情 - ${currentPrediction?.model_name}`"
      width="90%"
      top="5vh"
    >
      <div v-if="currentPrediction">
        <!-- 预测信息 -->
        <el-descriptions :column="4" border class="prediction-info">
          <el-descriptions-item label="预测ID">{{ currentPrediction.id }}</el-descriptions-item>
          <el-descriptions-item label="使用模型">{{ currentPrediction.model_name }}</el-descriptions-item>
          <el-descriptions-item label="数据集">{{ currentPrediction.dataset_name }}</el-descriptions-item>
          <el-descriptions-item label="预测步数">{{ currentPrediction.prediction_steps }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentPrediction.created_time) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 预测结果图表 -->
        <div class="chart-section">
          <h4>预测结果可视化</h4>
          <div ref="predictionChart" class="prediction-chart"></div>
        </div>

        <!-- 性能指标 -->
        <div v-if="currentPrediction.results?.metrics" class="metrics-section">
          <h4>预测性能</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic 
                title="MSE" 
                :value="currentPrediction.results.metrics.mse" 
                :precision="6" 
              />
            </el-col>
            <el-col :span="8">
              <el-statistic 
                title="MAE" 
                :value="currentPrediction.results.metrics.mae" 
                :precision="6" 
              />
            </el-col>
            <el-col :span="8">
              <el-statistic 
                title="RMSE" 
                :value="currentPrediction.results.metrics.rmse" 
                :precision="6" 
              />
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { predictionAPI, modelAPI } from '@/api'
import type { PredictionResult, Model, PredictionRequest } from '@/types/api'

// 响应式数据
const predictions = ref<PredictionResult[]>([])
const availableModels = ref<Model[]>([])
const currentPrediction = ref<PredictionResult | null>(null)
const showPredictionDialog = ref(false)
const showDetailsDialog = ref(false)
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const predictionChart = ref<HTMLElement>()

// 预测表单
const predictionForm = reactive({
  model_id: null as number | null,
  prediction_steps: 10
})

// 获取预测列表
const fetchPredictions = async () => {
  loading.value = true
  try {
    const response = await predictionAPI.getPredictions({
      page: currentPage.value,
      per_page: pageSize.value
    })
    predictions.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to fetch predictions:', error)
  } finally {
    loading.value = false
  }
}

// 获取可用模型
const fetchAvailableModels = async () => {
  try {
    const response = await modelAPI.getModels()
    availableModels.value = response.data.items.filter(model => model.status === 'completed')
  } catch (error) {
    console.error('Failed to fetch models:', error)
  }
}

// 创建预测任务
const createPrediction = async () => {
  if (!predictionForm.model_id) {
    ElMessage.warning('请选择模型')
    return
  }

  try {
    const data: PredictionRequest = {
      model_id: predictionForm.model_id,
      prediction_steps: predictionForm.prediction_steps
    }
    
    const result = await predictionAPI.createPrediction(data)
    ElMessage.success(`预测任务已创建，任务ID: ${result.task_id}`)
    showPredictionDialog.value = false
    fetchPredictions()
  } catch (error) {
    ElMessage.error('创建预测任务失败')
  }
}

// 查看预测详情
const viewPrediction = (prediction: PredictionResult) => {
  currentPrediction.value = prediction
  showDetailsDialog.value = true
  nextTick(() => {
    initPredictionChart()
  })
}

const viewPredictionDetails = (prediction: PredictionResult) => {
  viewPrediction(prediction)
}

// 初始化预测结果图表
const initPredictionChart = () => {
  if (!predictionChart.value || !currentPrediction.value) return

  const chart = echarts.init(predictionChart.value)
  const prediction = currentPrediction.value
  const results = prediction.results

  if (!results || !results.predictions) return

  // 生成时间轴
  const timeLabels = results.timestamps || 
    Array.from({ length: results.predictions.length }, (_, i) => `T${i + 1}`)

  const series: any[] = [
    {
      name: '预测值',
      type: 'line',
      data: results.predictions,
      smooth: true,
      itemStyle: { color: '#409EFF' },
      symbol: 'circle',
      symbolSize: 4
    }
  ]

  // 如果有实际值，添加到图表中
  if (results.actual_values && results.actual_values.length > 0) {
    series.push({
      name: '实际值',
      type: 'line',
      data: results.actual_values,
      smooth: true,
      itemStyle: { color: '#67C23A' },
      symbol: 'circle',
      symbolSize: 4
    })
  }

  chart.setOption({
    title: {
      text: '预测结果对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: { backgroundColor: '#6a7985' }
      }
    },
    legend: {
      data: series.map(s => s.name),
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      boundaryGap: false
    },
    yAxis: {
      type: 'value'
    },
    series: series
  })

  // 响应式调整
  const resizeChart = () => chart.resize()
  window.addEventListener('resize', resizeChart)
}

// 下载预测结果
const downloadPrediction = async (prediction: PredictionResult) => {
  try {
    await predictionAPI.downloadPrediction(prediction.id)
    ElMessage.success('下载已开始')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 删除预测结果
const deletePrediction = async (prediction: PredictionResult) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这个预测结果吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await predictionAPI.deletePrediction(prediction.id)
    ElMessage.success('预测结果删除成功')
    fetchPredictions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 刷新数据
const refreshPredictions = () => {
  fetchPredictions()
}

// 工具函数
const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchPredictions()
  fetchAvailableModels()
})
</script>

<style scoped>
.prediction-analysis {
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

.prediction-list-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.prediction-info {
  margin-bottom: 20px;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.prediction-chart {
  height: 400px;
  width: 100%;
}

.metrics-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}
</style>
