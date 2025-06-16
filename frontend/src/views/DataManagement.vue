<template>
  <div class="data-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>数据管理</h2>
        <p>管理和预览时间序列数据集</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          @click="showUploadDialog = true"
          :icon="Plus"
        >
          上传数据集
        </el-button>
      </div>
    </div>

    <!-- 数据集列表 -->
    <el-card class="data-list-card">
      <template #header>
        <div class="card-header">
          <span>数据集列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索数据集..."
              style="width: 200px; margin-right: 10px;"
              :prefix-icon="Search"
              clearable
            />
            <el-button 
              @click="refreshData"
              :loading="loading"
              :icon="Refresh"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="filteredDatasets" 
        v-loading="loading"
        stripe
        @row-click="viewDataset"
        style="cursor: pointer;"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="数据集名称" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="rows" label="行数" width="100" />
        <el-table-column prop="columns" label="列数" width="100">
          <template #default="{ row }">
            {{ row.columns?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="previewDataset(row)"
            >
              预览
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click.stop="downloadDataset(row)"
            >
              下载
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click.stop="deleteDataset(row)"
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

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传数据集"
      width="500px"
      @close="resetUploadForm"
    >
      <el-form 
        ref="uploadFormRef" 
        :model="uploadForm" 
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="数据集名称" prop="name">
          <el-input 
            v-model="uploadForm.name" 
            placeholder="请输入数据集名称"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="uploadForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入数据集描述（可选）"
          />
        </el-form-item>
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".csv,.xlsx,.xls"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 CSV、Excel 格式文件，文件大小不超过 100MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleUpload"
          :loading="uploading"
        >
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 数据预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="`数据预览 - ${currentDataset?.name}`"
      width="80%"
      top="5vh"
    >
      <div v-if="previewData">
        <!-- 数据统计信息 -->
        <el-descriptions :column="4" border class="preview-stats">
          <el-descriptions-item label="总行数">{{ previewData.total_rows }}</el-descriptions-item>
          <el-descriptions-item label="总列数">{{ previewData.total_columns }}</el-descriptions-item>
          <el-descriptions-item label="预览行数">{{ previewData.preview_rows }}</el-descriptions-item>
          <el-descriptions-item label="数据类型">{{ previewData.file_type }}</el-descriptions-item>
        </el-descriptions>

        <!-- 数据表格 -->
        <el-table 
          :data="previewData.data" 
          stripe 
          border
          style="margin-top: 20px;"
          max-height="400"
        >
          <el-table-column 
            v-for="column in previewData.columns" 
            :key="column"
            :prop="column"
            :label="column"
            min-width="120"
          />
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, UploadFilled } from '@element-plus/icons-vue'
import { useDataStore } from '@/stores/data'
import type { Dataset } from '@/types/api'

const dataStore = useDataStore()

// 响应式数据
const searchKeyword = ref('')
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const uploading = ref(false)
const uploadFormRef = ref()
const uploadRef = ref()
const currentDataset = ref<Dataset | null>(null)
const previewData = ref<any>(null)

// 上传表单
const uploadForm = reactive({
  name: '',
  description: '',
  file: null as File | null
})

// 表单验证规则
const uploadRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' }
  ],
  file: [
    { required: true, message: '请选择文件', trigger: 'change' }
  ]
}

// 计算属性
const datasets = computed(() => dataStore.datasets)
const loading = computed(() => dataStore.loading)
const total = computed(() => dataStore.total)
const currentPage = computed({
  get: () => dataStore.currentPage,
  set: (value) => dataStore.currentPage = value
})
const pageSize = computed({
  get: () => dataStore.pageSize,
  set: (value) => dataStore.pageSize = value
})

// 过滤后的数据集
const filteredDatasets = computed(() => {
  if (!searchKeyword.value) return datasets.value
  return datasets.value.filter(dataset => 
    dataset.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    dataset.filename.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 文件上传处理
const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  if (!uploadForm.name && file.name) {
    // 自动填充数据集名称
    uploadForm.name = file.name.replace(/\.[^/.]+$/, '')
  }
}

const handleFileRemove = () => {
  uploadForm.file = null
}

// 上传数据集
const handleUpload = async () => {
  if (!uploadFormRef.value) return
  
  try {
    await uploadFormRef.value.validate()
    
    const formData = new FormData()
    formData.append('file', uploadForm.file!)
    formData.append('name', uploadForm.name)
    if (uploadForm.description) {
      formData.append('description', uploadForm.description)
    }
    
    uploading.value = true
    await dataStore.uploadDataset(formData)
    
    ElMessage.success('数据集上传成功')
    showUploadDialog.value = false
    resetUploadForm()
  } catch (error) {
    ElMessage.error('数据集上传失败')
  } finally {
    uploading.value = false
  }
}

// 重置上传表单
const resetUploadForm = () => {
  uploadForm.name = ''
  uploadForm.description = ''
  uploadForm.file = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  if (uploadFormRef.value) {
    uploadFormRef.value.clearValidate()
  }
}

// 预览数据集
const previewDataset = async (dataset: Dataset) => {
  try {
    currentDataset.value = dataset
    previewData.value = await dataStore.previewDataset(dataset.id)
    showPreviewDialog.value = true
  } catch (error) {
    ElMessage.error('数据预览失败')
  }
}

// 查看数据集详情
const viewDataset = (dataset: Dataset) => {
  // 可以跳转到详情页面或显示详情对话框
  previewDataset(dataset)
}

// 下载数据集
const downloadDataset = (dataset: Dataset) => {
  // 这里可以实现下载功能
  ElMessage.info('下载功能待实现')
}

// 删除数据集
const deleteDataset = async (dataset: Dataset) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据集 "${dataset.name}" 吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await dataStore.deleteDataset(dataset.id)
    ElMessage.success('数据集删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('数据集删除失败')
    }
  }
}

// 刷新数据
const refreshData = () => {
  dataStore.fetchDatasets()
}

// 分页处理
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  dataStore.fetchDatasets()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  dataStore.fetchDatasets()
}

// 工具函数
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  dataStore.fetchDatasets()
})
</script>

<style scoped>
.data-management {
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

.data-list-card {
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

.preview-stats {
  margin-bottom: 20px;
}

.el-upload__tip {
  margin-top: 5px;
  color: #606266;
  font-size: 12px;
}
</style>
