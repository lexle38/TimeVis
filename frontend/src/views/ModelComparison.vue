<template>
  <div class="model-comparison">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>模型比较</h2>
        <p>比较不同模型在同一数据集上的性能表现</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          @click="showComparisonDialog = true"
        >
          创建比较任务
        </el-button>
      </div>
    </div>

    <!-- 比较结果列表 -->
    <el-card class="comparison-list-card">
      <template #header>
        <div class="card-header">
          <span>比较结果</span>
          <div class="header-actions">
            <el-button 
              @click="refreshComparisons"
              :loading="loading"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="comparisons" 
        v-loading="loading"
        stripe
        @row-click="viewComparison"
        style="cursor: pointer;"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="比较名称" />
        <el-table-column label="参与模型" width="200">
          <template #default="{ row }">
            {{ row.models?.length || 0 }} 个模型
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column label="最佳模型" width="200">
          <template #default="{ row }">
            <div v-if="row.results?.best_model">
              {{ row.results.best_model.model_name }}
              <el-tag type="success" size="small" style="margin-left: 8px;">
                {{ row.results.best_model.metric }}: {{ row.results.best_model.value.toFixed(4) }}
              </el-tag>
            </div>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="viewComparisonDetails(row)"
            >
              查看详情
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click.stop="deleteComparison(row)"
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

    <!-- 创建比较对话框 -->
    <el-dialog
      v-model="showComparisonDialog"
      title="创建模型比较"
      width="600px"
    >
      <el-form 
        :model="comparisonForm" 
        label-width="120px"
      >
        <el-form-item label="比较名称">
          <el-input 
            v-model="comparisonForm.comparison_name" 
            placeholder="请输入比较名称"
          />
        </el-form-item>
        
        <el-form-item label="选择数据集">
          <el-select 
            v-model="comparisonForm.dataset_id" 
            placeholder="选择数据集"
            style="width: 100%"
            @change="onDatasetChange"
          >
            <el-option 
              v-for="dataset in availableDatasets" 
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择模型">
          <el-transfer
            v-model="comparisonForm.model_ids"
            :data="availableModelsForTransfer"
            :titles="['可选模型', '参与比较']"
            :button-texts="['移除', '添加']"
            :format="{
              noChecked: '${total}',
              hasChecked: '${checked}/${total}'
            }"
            style="text-align: left; display: inline-block"
          />
        </el-form-item>
        
        <el-form-item label="测试集比例">
          <el-slider 
            v-model="comparisonForm.test_size" 
            :min="0.1"
            :max="0.5"
            :step="0.05"
            show-input
            :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showComparisonDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="createComparison"
          :disabled="comparisonForm.model_ids.length < 2"
        >
          创建比较
        </el-button>
      </template>
    </el-dialog>

    <!-- 比较详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      :title="`比较详情 - ${currentComparison?.name}`"
      width="90%"
      top="5vh"
    >
      <div v-if="currentComparison">
        <!-- 比较信息 -->
        <el-descriptions :column="3" border class="comparison-info">
          <el-descriptions-item label="比较ID">{{ currentComparison.id }}</el-descriptions-item>
          <el-descriptions-item label="比较名称">{{ currentComparison.name }}</el-descriptions-item>
          <el-descriptions-item label="参与模型数">{{ currentComparison.models?.length || 0 }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentComparison.created_time) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 性能对比图表 -->
        <div class="chart-section">
          <h4>性能对比</h4>
          <div ref="comparisonChart" class="comparison-chart"></div>
        </div>

        <!-- 详细性能指标表格 -->
        <div v-if="currentComparison.results?.model_performances" class="performance-table">
          <h4>详细性能指标</h4>
          <el-table 
            :data="currentComparison.results.model_performances" 
            border
            stripe
          >
            <el-table-column prop="model_name" label="模型名称" />
            <el-table-column prop="metrics.mse" label="MSE" width="120">
              <template #default="{ row }">
                {{ row.metrics.mse.toFixed(6) }}
              </template>
            </el-table-column>
            <el-table-column prop="metrics.mae" label="MAE" width="120">
              <template #default="{ row }">
                {{ row.metrics.mae.toFixed(6) }}
              </template>
            </el-table-column>
            <el-table-column prop="metrics.rmse" label="RMSE" width="120">
              <template #default="{ row }">
                {{ row.metrics.rmse.toFixed(6) }}
              </template>
            </el-table-column>
            <el-table-column prop="metrics.r2" label="R²" width="120">
              <template #default="{ row }">
                {{ row.metrics.r2?.toFixed(4) || '--' }}
              </template>
            </el-table-column>
            <el-table-column label="是否最佳" width="100">
              <template #default="{ row }">
                <el-tag 
                  v-if="row.model_id === currentComparison?.results?.best_model?.model_id"
                  type="success"
                  size="small"
                >
                  最佳
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 最佳模型信息 -->
        <div v-if="currentComparison.results?.best_model" class="best-model-section">
          <h4>最佳模型</h4>
          <el-alert
            :title="`${currentComparison.results.best_model.model_name} - ${currentComparison.results.best_model.metric}: ${currentComparison.results.best_model.value.toFixed(6)}`"
            type="success"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { comparisonAPI, modelAPI, dataAPI } from '@/api'
import type { ModelComparison, Model, Dataset, ComparisonRequest } from '@/types/api'

// 响应式数据
const comparisons = ref<ModelComparison[]>([])
const availableModels = ref<Model[]>([])
const availableDatasets = ref<Dataset[]>([])
const currentComparison = ref<ModelComparison | null>(null)
const showComparisonDialog = ref(false)
const showDetailsDialog = ref(false)
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const comparisonChart = ref<HTMLElement>()

// 比较表单
const comparisonForm = reactive({
  comparison_name: '',
  model_ids: [] as number[],
  dataset_id: null as number | null,
  test_size: 0.2
})

// 计算属性
const availableModelsForTransfer = computed(() => {
  return availableModels.value
    .filter(model => model.status === 'completed')
    .map(model => ({
      key: model.id,
      label: `${model.name} (${model.model_type.toUpperCase()})`,
      disabled: false
    }))
})

// 获取比较结果列表
const fetchComparisons = async () => {
  loading.value = true
  try {
    const response = await comparisonAPI.getComparisons({
      page: currentPage.value,
      per_page: pageSize.value
    })
    comparisons.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to fetch comparisons:', error)
  } finally {
    loading.value = false
  }
}

// 获取可用模型和数据集
const fetchAvailableData = async () => {
  try {
    const [modelsResponse, datasetsResponse] = await Promise.all([
      modelAPI.getModels(),
      dataAPI.getDatasets()
    ])
    availableModels.value = modelsResponse.data.items
    availableDatasets.value = datasetsResponse.data.items
  } catch (error) {
    console.error('Failed to fetch available data:', error)
  }
}

// 数据集变化处理
const onDatasetChange = (datasetId: number) => {
  // 可以根据数据集筛选相关模型
  // 这里暂时不做处理
}

// 创建比较任务
const createComparison = async () => {
  if (!comparisonForm.comparison_name) {
    ElMessage.warning('请输入比较名称')
    return
  }
  
  if (!comparisonForm.dataset_id) {
    ElMessage.warning('请选择数据集')
    return
  }
  
  if (comparisonForm.model_ids.length < 2) {
    ElMessage.warning('至少选择2个模型进行比较')
    return
  }

  try {
    const data: ComparisonRequest = {
      comparison_name: comparisonForm.comparison_name,
      model_ids: comparisonForm.model_ids,
      dataset_id: comparisonForm.dataset_id,
      test_size: comparisonForm.test_size
    }
    
    const result = await comparisonAPI.createComparison(data)
    ElMessage.success(`比较任务已创建，任务ID: ${result.task_id}`)
    showComparisonDialog.value = false
    resetComparisonForm()
    fetchComparisons()
  } catch (error) {
    ElMessage.error('创建比较任务失败')
  }
}

// 重置比较表单
const resetComparisonForm = () => {
  comparisonForm.comparison_name = ''
  comparisonForm.model_ids = []
  comparisonForm.dataset_id = null
  comparisonForm.test_size = 0.2
}

// 查看比较详情
const viewComparison = (comparison: ModelComparison) => {
  currentComparison.value = comparison
  showDetailsDialog.value = true
  nextTick(() => {
    initComparisonChart()
  })
}

const viewComparisonDetails = (comparison: ModelComparison) => {
  viewComparison(comparison)
}

// 初始化比较图表
const initComparisonChart = () => {
  if (!comparisonChart.value || !currentComparison.value?.results?.model_performances) return

  const chart = echarts.init(comparisonChart.value)
  const performances = currentComparison.value.results.model_performances

  const modelNames = performances.map(p => p.model_name)
  const mseData = performances.map(p => p.metrics.mse)
  const maeData = performances.map(p => p.metrics.mae)
  const rmseData = performances.map(p => p.metrics.rmse)

  chart.setOption({
    title: {
      text: '模型性能对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['MSE', 'MAE', 'RMSE'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: modelNames,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'MSE',
        type: 'bar',
        data: mseData,
        itemStyle: { color: '#FF6B6B' }
      },
      {
        name: 'MAE',
        type: 'bar',
        data: maeData,
        itemStyle: { color: '#4ECDC4' }
      },
      {
        name: 'RMSE',
        type: 'bar',
        data: rmseData,
        itemStyle: { color: '#45B7D1' }
      }
    ]
  })

  // 响应式调整
  const resizeChart = () => chart.resize()
  window.addEventListener('resize', resizeChart)
}

// 删除比较结果
const deleteComparison = async (comparison: ModelComparison) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除比较结果 "${comparison.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await comparisonAPI.deleteComparison(comparison.id)
    ElMessage.success('比较结果删除成功')
    fetchComparisons()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 刷新数据
const refreshComparisons = () => {
  fetchComparisons()
}

// 工具函数
const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchComparisons()
  fetchAvailableData()
})
</script>

<style scoped>
.model-comparison {
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

.comparison-list-card {
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

.comparison-info {
  margin-bottom: 20px;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.comparison-chart {
  height: 400px;
  width: 100%;
}

.performance-table h4,
.best-model-section h4 {
  margin: 20px 0 15px 0;
  color: #303133;
}
</style>
