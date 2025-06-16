<template>
  <div class="model-training">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>模型训练</h2>
        <p>训练LSTM和Qwen时间序列预测模型</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          @click="showTrainingDialog = true"
          :icon="Plus"
        >
          新建训练任务
        </el-button>
      </div>
    </div>

    <!-- 模型列表 -->
    <el-card class="model-list-card">
      <template #header>
        <div class="card-header">
          <span>已训练模型</span>
          <div class="header-actions">
            <el-select v-model="filterStatus" placeholder="筛选状态" style="width: 120px; margin-right: 10px;" clearable>
              <el-option label="训练中" value="training" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-select v-model="filterType" placeholder="筛选类型" style="width: 120px; margin-right: 10px;" clearable>
              <el-option label="LSTM" value="lstm" />
              <el-option label="Qwen" value="qwen" />
            </el-select>
            <el-button 
              @click="refreshModels"
              :loading="loading"
              :icon="Refresh"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="filteredModels" 
        v-loading="loading"
        stripe
        @row-click="viewModel"
        style="cursor: pointer;"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模型名称" />
        <el-table-column prop="model_type" label="模型类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getModelTypeColor(row.model_type)" size="small">
              {{ row.model_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataset_name" label="训练数据集" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="training_time" label="训练耗时" width="120">
          <template #default="{ row }">
            {{ row.training_time ? formatDuration(row.training_time) : '--' }}
          </template>
        </el-table-column>
        <el-table-column label="性能指标" width="150">
          <template #default="{ row }">
            <div v-if="row.metrics && row.metrics.mse">
              <div class="metric-item">MSE: {{ row.metrics.mse.toFixed(4) }}</div>
              <div class="metric-item">MAE: {{ row.metrics.mae?.toFixed(4) || '--' }}</div>
            </div>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="viewModelDetails(row)"
            >
              详情
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click.stop="createPrediction(row)"
              :disabled="row.status !== 'completed'"
            >
              预测
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click.stop="deleteModel(row)"
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
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 训练任务对话框 -->
    <el-dialog
      v-model="showTrainingDialog"
      title="新建训练任务"
      width="600px"
      @close="resetTrainingForm"
    >
      <el-form 
        ref="trainingFormRef" 
        :model="trainingForm" 
        :rules="trainingRules"
        label-width="120px"
      >
        <el-form-item label="模型名称" prop="model_name">
          <el-input 
            v-model="trainingForm.model_name" 
            placeholder="请输入模型名称"
          />
        </el-form-item>
        
        <el-form-item label="模型类型" prop="model_type">
          <el-radio-group v-model="trainingForm.model_type">
            <el-radio value="lstm">LSTM</el-radio>
            <el-radio value="qwen">Qwen</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="训练数据集" prop="dataset_id">
          <el-select 
            v-model="trainingForm.dataset_id" 
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
        
        <el-form-item label="目标列" prop="target_column" v-if="selectedDatasetColumns.length > 0">
          <el-select 
            v-model="trainingForm.target_column" 
            placeholder="选择目标列"
            style="width: 100%"
          >
            <el-option 
              v-for="column in selectedDatasetColumns" 
              :key="column"
              :label="column"
              :value="column"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="序列长度" prop="sequence_length">
          <el-input-number 
            v-model="trainingForm.sequence_length" 
            :min="5"
            :max="100"
            placeholder="时间序列长度"
          />
          <span class="form-hint">用于预测的历史数据点数量</span>
        </el-form-item>
        
        <el-form-item label="测试集比例" prop="test_size">
          <el-slider 
            v-model="trainingForm.test_size" 
            :min="0.1"
            :max="0.5"
            :step="0.05"
            show-input
            :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`"
          />
        </el-form-item>
        
        <!-- 高级参数 -->
        <el-collapse v-model="advancedParams">
          <el-collapse-item title="高级参数" name="advanced">
            <el-form-item label="批次大小">
              <el-input-number 
                v-model="trainingForm.parameters.batch_size" 
                :min="8"
                :max="128"
              />
            </el-form-item>
            
            <el-form-item label="训练轮数">
              <el-input-number 
                v-model="trainingForm.parameters.epochs" 
                :min="10"
                :max="500"
              />
            </el-form-item>
            
            <el-form-item label="学习率">
              <el-input-number 
                v-model="trainingForm.parameters.learning_rate" 
                :min="0.0001"
                :max="0.1"
                :step="0.0001"
                :precision="4"
              />
            </el-form-item>
            
            <div v-if="trainingForm.model_type === 'lstm'">
              <el-form-item label="隐藏层大小">
                <el-input-number 
                  v-model="trainingForm.parameters.hidden_size" 
                  :min="32"
                  :max="512"
                />
              </el-form-item>
              
              <el-form-item label="层数">
                <el-input-number 
                  v-model="trainingForm.parameters.num_layers" 
                  :min="1"
                  :max="5"
                />
              </el-form-item>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-form>
      
      <template #footer>
        <el-button @click="showTrainingDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleTraining"
          :loading="training"
        >
          开始训练
        </el-button>
      </template>
    </el-dialog>

    <!-- 模型详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      :title="`模型详情 - ${currentModel?.name}`"
      width="70%"
      top="5vh"
    >
      <div v-if="currentModel">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="模型ID">{{ currentModel.id }}</el-descriptions-item>
          <el-descriptions-item label="模型名称">{{ currentModel.name }}</el-descriptions-item>
          <el-descriptions-item label="模型类型">
            <el-tag :type="getModelTypeColor(currentModel.model_type)">
              {{ currentModel.model_type.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="训练数据集">{{ currentModel.dataset_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(currentModel.status)">
              {{ getStatusText(currentModel.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentModel.created_time) }}</el-descriptions-item>
          <el-descriptions-item label="训练耗时" v-if="currentModel.training_time">
            {{ formatDuration(currentModel.training_time) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 性能指标 -->
        <div v-if="currentModel.metrics" class="metrics-section">
          <h4>性能指标</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="MSE" :value="currentModel.metrics.mse" :precision="6" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="MAE" :value="currentModel.metrics.mae" :precision="6" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="RMSE" :value="currentModel.metrics.rmse" :precision="6" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="R²" :value="currentModel.metrics.r2" :precision="4" />
            </el-col>
          </el-row>
        </div>

        <!-- 训练参数 -->
        <div v-if="currentModel.parameters" class="parameters-section">
          <h4>训练参数</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item 
              v-for="(value, key) in currentModel.parameters" 
              :key="key"
              :label="formatParameterName(key)"
            >
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { useModelStore } from '@/stores/model'
import { useDataStore } from '@/stores/data'
import type { Model, Dataset, TrainingRequest } from '@/types/api'

const router = useRouter()
const modelStore = useModelStore()
const dataStore = useDataStore()

// 响应式数据
const filterStatus = ref('')
const filterType = ref('')
const showTrainingDialog = ref(false)
const showDetailsDialog = ref(false)
const trainingFormRef = ref()
const advancedParams = ref([''])
const currentModel = ref<Model | null>(null)
const selectedDatasetColumns = ref<string[]>([])

// 训练表单
const trainingForm = reactive({
  model_name: '',
  model_type: 'lstm' as 'lstm' | 'qwen',
  dataset_id: null as number | null,
  target_column: '',
  sequence_length: 30,
  test_size: 0.2,
  parameters: {
    batch_size: 32,
    epochs: 100,
    learning_rate: 0.001,
    hidden_size: 128,
    num_layers: 2
  }
})

// 表单验证规则
const trainingRules = {
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  model_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  dataset_id: [
    { required: true, message: '请选择训练数据集', trigger: 'change' }
  ],
  target_column: [
    { required: true, message: '请选择目标列', trigger: 'change' }
  ]
}

// 计算属性
const models = computed(() => modelStore.models)
const loading = computed(() => modelStore.loading)
const training = computed(() => modelStore.training)
const total = computed(() => modelStore.total)
const currentPage = computed({
  get: () => modelStore.currentPage,
  set: (value) => modelStore.currentPage = value
})
const pageSize = computed({
  get: () => modelStore.pageSize,
  set: (value) => modelStore.pageSize = value
})

const availableDatasets = computed(() => dataStore.datasets)

// 过滤后的模型
const filteredModels = computed(() => {
  let result = models.value
  
  if (filterStatus.value) {
    result = result.filter(model => model.status === filterStatus.value)
  }
  
  if (filterType.value) {
    result = result.filter(model => model.model_type === filterType.value)
  }
  
  return result
})

// 数据集选择变化
const onDatasetChange = async (datasetId: number) => {
  try {
    const dataset = await dataStore.fetchDataset(datasetId)
    selectedDatasetColumns.value = dataset.columns || []
  } catch (error) {
    console.error('Failed to fetch dataset columns:', error)
  }
}

// 开始训练
const handleTraining = async () => {
  if (!trainingFormRef.value) return
  
  try {
    await trainingFormRef.value.validate()
    
    const data: TrainingRequest = {
      model_name: trainingForm.model_name,
      model_type: trainingForm.model_type,
      dataset_id: trainingForm.dataset_id!,
      target_column: trainingForm.target_column,
      sequence_length: trainingForm.sequence_length,
      test_size: trainingForm.test_size,
      parameters: trainingForm.parameters
    }
    
    const result = await modelStore.trainModel(data)
    
    ElMessage.success(`训练任务已创建，任务ID: ${result.task_id}`)
    showTrainingDialog.value = false
    resetTrainingForm()
  } catch (error) {
    ElMessage.error('创建训练任务失败')
  }
}

// 重置训练表单
const resetTrainingForm = () => {
  trainingForm.model_name = ''
  trainingForm.model_type = 'lstm'
  trainingForm.dataset_id = null
  trainingForm.target_column = ''
  trainingForm.sequence_length = 30
  trainingForm.test_size = 0.2
  trainingForm.parameters = {
    batch_size: 32,
    epochs: 100,
    learning_rate: 0.001,
    hidden_size: 128,
    num_layers: 2
  }
  selectedDatasetColumns.value = []
  if (trainingFormRef.value) {
    trainingFormRef.value.clearValidate()
  }
}

// 查看模型详情
const viewModel = (model: Model) => {
  currentModel.value = model
  showDetailsDialog.value = true
}

const viewModelDetails = (model: Model) => {
  viewModel(model)
}

// 创建预测任务
const createPrediction = (model: Model) => {
  router.push(`/prediction?model_id=${model.id}`)
}

// 删除模型
const deleteModel = async (model: Model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.name}" 吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await modelStore.deleteModel(model.id)
    ElMessage.success('模型删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('模型删除失败')
    }
  }
}

// 刷新模型列表
const refreshModels = () => {
  modelStore.fetchModels()
}

// 分页处理
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  modelStore.fetchModels()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  modelStore.fetchModels()
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

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}

const formatParameterName = (key: string) => {
  const names: Record<string, string> = {
    batch_size: '批次大小',
    epochs: '训练轮数',
    learning_rate: '学习率',
    hidden_size: '隐藏层大小',
    num_layers: '层数'
  }
  return names[key] || key
}

// 生命周期
onMounted(() => {
  modelStore.fetchModels()
  dataStore.fetchDatasets()
})
</script>

<style scoped>
.model-training {
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

.model-list-card {
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

.metric-item {
  font-size: 12px;
  line-height: 1.5;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.metrics-section,
.parameters-section {
  margin-top: 20px;
}

.metrics-section h4,
.parameters-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}
</style>
