# 前端开发指南

## 项目概述

TimeVis 前端是一个基于 Vue3 + TypeScript 的现代化单页应用，用于时间序列预测和可视化。界面设计参考 LLaMA-Factory 风格，提供直观易用的用户体验。

## 技术栈推荐

### 核心框架
- **Vue 3**: 使用 Composition API
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Vue Router**: 路由管理
- **Pinia**: 状态管理

### UI组件库
- **Element Plus**: 推荐，组件丰富，文档完善
- **Ant Design Vue**: 备选方案
- **Naive UI**: 轻量级选择

### 图表库
- **ECharts**: 主要图表库，功能强大
- **Chart.js**: 轻量级备选
- **D3.js**: 高度定制化需求

### 工具库
- **Axios**: HTTP客户端
- **Day.js**: 日期处理
- **Lodash**: 工具函数
- **VueUse**: Vue 组合式函数

## 项目结构

```
frontend/
├── public/                 # 静态资源
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── api/               # API接口
│   │   ├── types.ts       # 类型定义
│   │   ├── dataset.ts     # 数据集相关接口
│   │   ├── model.ts       # 模型相关接口
│   │   ├── task.ts        # 任务相关接口
│   │   └── index.ts       # 接口汇总
│   ├── components/        # 组件
│   │   ├── common/        # 通用组件
│   │   ├── charts/        # 图表组件
│   │   ├── upload/        # 文件上传组件
│   │   └── forms/         # 表单组件
│   ├── views/             # 页面
│   │   ├── Dashboard.vue  # 仪表板
│   │   ├── DataManagement.vue  # 数据管理
│   │   ├── ModelTraining.vue   # 模型训练
│   │   ├── Prediction.vue      # 预测分析
│   │   ├── TaskMonitor.vue     # 任务监控
│   │   └── ModelComparison.vue # 模型比较
│   ├── stores/            # 状态管理
│   │   ├── user.ts
│   │   ├── dataset.ts
│   │   ├── model.ts
│   │   └── task.ts
│   ├── router/            # 路由配置
│   │   └── index.ts
│   ├── utils/             # 工具函数
│   │   ├── request.ts     # 请求封装
│   │   ├── formatter.ts   # 数据格式化
│   │   └── constants.ts   # 常量定义
│   ├── types/             # 类型定义
│   │   └── index.ts
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── package.json           # 依赖配置
├── tsconfig.json          # TypeScript配置
├── vite.config.ts         # Vite配置
└── README.md              # 前端说明
```

## 核心功能模块

### 1. 仪表板 (Dashboard)
- 系统统计概览
- 最近任务状态
- 快捷操作入口
- 性能指标展示

### 2. 数据管理 (DataManagement)
- 数据文件上传
- 数据集列表展示
- 数据预览和分析
- 示例数据生成

### 3. 模型训练 (ModelTraining)
- 训练配置表单
- 模型参数设置
- 训练过程监控
- 训练结果展示

### 4. 预测分析 (Prediction)
- 模型选择
- 输入序列配置
- 预测结果可视化
- 批量预测支持

### 5. 任务监控 (TaskMonitor)
- 任务列表展示
- 实时状态更新
- 进度条显示
- 任务操作管理

### 6. 模型比较 (ModelComparison)
- 模型性能对比
- 预测结果对比
- 误差分析图表
- 统计指标比较

## 关键组件设计

### 1. 文件上传组件 (UploadComponent)

```vue
<template>
  <el-upload
    class="upload-demo"
    drag
    :action="uploadUrl"
    :data="uploadData"
    :on-success="handleSuccess"
    :on-error="handleError"
    :before-upload="beforeUpload"
    accept=".csv,.xlsx,.json"
  >
    <el-icon class="el-icon--upload">
      <upload-filled />
    </el-icon>
    <div class="el-upload__text">
      拖拽文件到此处或<em>点击上传</em>
    </div>
    <div class="el-upload__tip">
      支持 CSV、Excel、JSON 格式，文件大小不超过100MB
    </div>
  </el-upload>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps } from 'element-plus'

interface Props {
  dataType: 'weather' | 'electricity' | 'traffic'
  datasetName?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  success: [result: any]
  error: [error: string]
}>()

const uploadUrl = ref('/api/upload')
const uploadData = ref({
  data_type: props.dataType,
  dataset_name: props.datasetName || ''
})

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isValidType = ['text/csv', 'application/vnd.ms-excel', 'application/json'].includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 100

  if (!isValidType) {
    ElMessage.error('只支持 CSV、Excel、JSON 格式文件')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过 100MB')
    return false
  }
  return true
}

const handleSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
  emit('success', response)
}

const handleError = (error: any) => {
  ElMessage.error('文件上传失败')
  emit('error', error.message)
}
</script>
```

### 2. 时间序列图表组件 (TimeSeriesChart)

```vue
<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data: {
    actual?: number[]
    predicted?: number[]
    qwen_predicted?: number[]
    lstm_predicted?: number[]
    timestamps?: string[]
  }
  title?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '时间序列预测',
  height: '400px'
})

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chart) return

  const series: any[] = []
  
  // 实际值
  if (props.data.actual) {
    series.push({
      name: '实际值',
      type: 'line',
      data: props.data.actual,
      lineStyle: { color: '#409EFF', width: 2 },
      symbol: 'circle',
      symbolSize: 4
    })
  }
  
  // 预测值
  if (props.data.predicted) {
    series.push({
      name: '预测值',
      type: 'line',
      data: props.data.predicted,
      lineStyle: { color: '#67C23A', width: 2, type: 'dashed' },
      symbol: 'diamond',
      symbolSize: 4
    })
  }
  
  // Qwen预测值
  if (props.data.qwen_predicted) {
    series.push({
      name: 'Qwen预测',
      type: 'line',
      data: props.data.qwen_predicted,
      lineStyle: { color: '#E6A23C', width: 2, type: 'dashed' },
      symbol: 'triangle',
      symbolSize: 4
    })
  }
  
  // LSTM预测值
  if (props.data.lstm_predicted) {
    series.push({
      name: 'LSTM预测',
      type: 'line',
      data: props.data.lstm_predicted,
      lineStyle: { color: '#F56C6C', width: 2, type: 'dashed' },
      symbol: 'rect',
      symbolSize: 4
    })
  }

  const option = {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      top: 30,
      data: series.map(s => s.name)
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.data.timestamps || Array.from({length: series[0]?.data?.length || 0}, (_, i) => i),
      axisLine: {
        lineStyle: { color: '#666' }
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: { color: '#666' }
      },
      splitLine: {
        lineStyle: { color: '#f0f0f0' }
      }
    },
    series
  }

  chart.setOption(option)
}

watch(() => props.data, updateChart, { deep: true })

onMounted(initChart)
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: v-bind(height);
}
</style>
```

### 3. 训练配置表单 (TrainingConfigForm)

```vue
<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
    <el-form-item label="数据集" prop="datasetId">
      <el-select v-model="form.datasetId" placeholder="选择数据集" style="width: 100%">
        <el-option
          v-for="dataset in datasets"
          :key="dataset.id"
          :label="dataset.name"
          :value="dataset.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="模型类型" prop="modelType">
      <el-radio-group v-model="form.modelType">
        <el-radio label="qwen">Qwen大模型</el-radio>
        <el-radio label="lstm">LSTM模型</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="数据类型" prop="dataType">
      <el-select v-model="form.dataType" placeholder="选择数据类型">
        <el-option label="天气数据" value="weather" />
        <el-option label="电力数据" value="electricity" />
        <el-option label="交通数据" value="traffic" />
      </el-select>
    </el-form-item>

    <!-- Qwen模型配置 -->
    <template v-if="form.modelType === 'qwen'">
      <el-form-item label="训练轮数" prop="modelConfig.num_epochs">
        <el-input-number v-model="form.modelConfig.num_epochs" :min="1" :max="20" />
      </el-form-item>
      
      <el-form-item label="学习率" prop="modelConfig.learning_rate">
        <el-input-number 
          v-model="form.modelConfig.learning_rate" 
          :min="1e-6" 
          :max="1e-2" 
          :step="1e-5"
          :precision="6"
        />
      </el-form-item>
      
      <el-form-item label="序列长度" prop="modelConfig.sequence_length">
        <el-input-number v-model="form.modelConfig.sequence_length" :min="5" :max="50" />
      </el-form-item>
    </template>

    <!-- LSTM模型配置 -->
    <template v-if="form.modelType === 'lstm'">
      <el-form-item label="隐藏层大小" prop="modelConfig.hidden_size">
        <el-input-number v-model="form.modelConfig.hidden_size" :min="16" :max="512" :step="16" />
      </el-form-item>
      
      <el-form-item label="LSTM层数" prop="modelConfig.num_layers">
        <el-input-number v-model="form.modelConfig.num_layers" :min="1" :max="5" />
      </el-form-item>
      
      <el-form-item label="训练轮数" prop="modelConfig.num_epochs">
        <el-input-number v-model="form.modelConfig.num_epochs" :min="10" :max="1000" />
      </el-form-item>
    </template>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        开始训练
      </el-button>
      <el-button @click="handleReset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

interface Dataset {
  id: number
  name: string
  data_type: string
}

interface Props {
  datasets: Dataset[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  submit: [config: any]
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  datasetId: null,
  modelType: 'lstm',
  dataType: 'weather',
  modelConfig: {
    num_epochs: 50,
    learning_rate: 0.001,
    sequence_length: 10,
    hidden_size: 64,
    num_layers: 2,
    dropout: 0.2
  }
})

const rules: FormRules = {
  datasetId: [{ required: true, message: '请选择数据集', trigger: 'change' }],
  modelType: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  dataType: [{ required: true, message: '请选择数据类型', trigger: 'change' }]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    emit('submit', { ...form })
  } catch (error) {
    ElMessage.error('请检查表单填写')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
}
</script>
```

## API 接口封装

### 1. HTTP 客户端配置

```typescript
// src/utils/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加认证头等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.error || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
```

### 2. API 接口定义

```typescript
// src/api/types.ts
export interface Dataset {
  id: number
  name: string
  data_type: 'weather' | 'electricity' | 'traffic'
  file_path: string
  file_size: number
  num_samples: number
  num_features: number
  uploaded_at: string
}

export interface Model {
  id: number
  name: string
  model_type: 'qwen' | 'lstm'
  data_type: 'weather' | 'electricity' | 'traffic'
  model_path: string
  validation_mse: number
  validation_mae: number
  validation_rmse: number
  created_at: string
  is_active: boolean
}

export interface Task {
  id: number
  task_type: 'training' | 'prediction' | 'comparison'
  data_type: 'weather' | 'electricity' | 'traffic'
  model_type: 'qwen' | 'lstm' | 'comparison'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  created_at: string
  started_at?: string
  completed_at?: string
  mse?: number
  mae?: number
  rmse?: number
  error_message?: string
}

export interface TrainingConfig {
  dataset_id: number
  model_type: 'qwen' | 'lstm'
  data_type: 'weather' | 'electricity' | 'traffic'
  model_config: Record<string, any>
}

export interface PredictionConfig {
  model_id: number
  input_sequence: number[]
}
```

```typescript
// src/api/dataset.ts
import request from '@/utils/request'
import type { Dataset } from './types'

export const datasetApi = {
  // 获取数据集列表
  getList(): Promise<{ datasets: Dataset[] }> {
    return request.get('/datasets')
  },

  // 获取数据集详情
  getDetail(id: number): Promise<{
    dataset: Dataset
    preview: any[]
    columns: string[]
    shape: number[]
  }> {
    return request.get(`/datasets/${id}`)
  },

  // 上传文件
  upload(formData: FormData): Promise<any> {
    return request.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 生成示例数据
  generateSample(params: {
    data_type: string
    num_samples: number
  }): Promise<any> {
    return request.post('/sample-data', params)
  }
}
```

## 状态管理

```typescript
// src/stores/task.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { taskApi } from '@/api/task'
import type { Task } from '@/api/types'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const loading = ref(false)

  // 获取任务列表
  const fetchTasks = async (params?: any) => {
    loading.value = true
    try {
      const response = await taskApi.getList(params)
      tasks.value = response.tasks
    } finally {
      loading.value = false
    }
  }

  // 获取任务详情
  const fetchTaskDetail = async (id: number) => {
    const task = await taskApi.getDetail(id)
    currentTask.value = task
    
    // 更新列表中的任务
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index] = task
    }
    
    return task
  }

  // 轮询任务状态
  const pollTaskStatus = async (taskId: number, interval = 2000) => {
    const poll = async () => {
      try {
        const task = await fetchTaskDetail(taskId)
        
        if (task.status === 'completed' || task.status === 'failed') {
          return task
        }
        
        setTimeout(poll, interval)
      } catch (error) {
        console.error('轮询任务状态失败:', error)
      }
    }
    
    return poll()
  }

  // 计算属性
  const runningTasks = computed(() => 
    tasks.value.filter(task => task.status === 'running')
  )
  
  const completedTasks = computed(() =>
    tasks.value.filter(task => task.status === 'completed')
  )

  return {
    tasks,
    currentTask,
    loading,
    runningTasks,
    completedTasks,
    fetchTasks,
    fetchTaskDetail,
    pollTaskStatus
  }
})
```

## 页面布局建议

### 1. 主布局

```vue
<!-- src/App.vue -->
<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <h2>TimeVis</h2>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><FolderOpened /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/training">
          <el-icon><Setting /></el-icon>
          <span>模型训练</span>
        </el-menu-item>
        <el-menu-item index="/prediction">
          <el-icon><TrendCharts /></el-icon>
          <span>预测分析</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务监控</span>
        </el-menu-item>
        <el-menu-item index="/comparison">
          <el-icon><DataAnalysis /></el-icon>
          <span>模型比较</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <h3>{{ $route.meta.title || '时间序列预测系统' }}</h3>
        </div>
        <div class="header-right">
          <el-badge :value="runningTasksCount" class="task-badge">
            <el-button :icon="Loading" circle />
          </el-badge>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
```

### 2. 响应式设计

```css
/* 响应式样式 */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .main-content {
    padding: 10px;
  }
}

/* 深色主题支持 */
.dark-theme {
  --el-bg-color: #141414;
  --el-text-color-primary: #ffffff;
  --el-border-color: #303030;
}
```

## 开发建议

### 1. 开发环境配置

```json
// package.json
{
  "name": "timevis-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .vue,.js,.ts,.jsx,.tsx",
    "lint:fix": "eslint src --ext .vue,.js,.ts,.jsx,.tsx --fix"
  },
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.3.0",
    "echarts": "^5.4.0",
    "axios": "^1.4.0",
    "dayjs": "^1.11.0",
    "@element-plus/icons-vue": "^2.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "typescript": "^5.0.0",
    "vue-tsc": "^1.6.0",
    "vite": "^4.3.0",
    "eslint": "^8.42.0",
    "@typescript-eslint/eslint-plugin": "^5.59.0",
    "@typescript-eslint/parser": "^5.59.0"
  }
}
```

### 2. 开发工作流

1. **组件开发**: 先开发通用组件，再组合成页面
2. **API接口**: 先完成接口封装，再开发页面功能
3. **状态管理**: 合理使用Pinia管理全局状态
4. **错误处理**: 统一错误处理和用户提示
5. **性能优化**: 使用懒加载、虚拟滚动等技术

### 3. 代码规范

- 使用TypeScript严格模式
- 遵循Vue3 Composition API最佳实践
- 组件命名使用PascalCase
- 文件命名使用kebab-case
- 提交信息遵循Conventional Commits

### 4. 测试策略

- 单元测试：核心工具函数
- 组件测试：关键业务组件
- 端到端测试：主要用户流程

## 部署建议

### 1. 构建配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          element: ['element-plus'],
          charts: ['echarts']
        }
      }
    }
  }
})
```

### 2. Docker部署

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

这份前端开发指南提供了完整的技术栈选择、项目结构、关键组件实现和开发流程建议。前端开发者可以基于这个指南快速开始开发工作。
