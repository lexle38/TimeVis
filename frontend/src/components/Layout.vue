<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="250px" class="sidebar">
      <div class="logo">
        <h2>TimeVis</h2>
        <p>时间序列预测系统</p>
      </div>
      
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
        >
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <span>{{ route.meta.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主体内容 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute?.meta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 系统状态 -->
          <el-badge :value="runningTasksCount" :hidden="runningTasksCount === 0" class="task-badge">
            <el-button
              type="text"
              @click="showTaskMonitor = true"
              class="header-btn"
            >
              <el-icon><Monitor /></el-icon>
              任务监控
            </el-button>
          </el-badge>
          
          <!-- 系统信息 -->
          <el-dropdown @command="handleCommand">
            <el-button type="text" class="header-btn">
              <el-icon><Setting /></el-icon>
              系统
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="status">系统状态</el-dropdown-item>
                <el-dropdown-item command="help">帮助文档</el-dropdown-item>
                <el-dropdown-item command="about">关于</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主体内容区域 -->
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 任务监控抽屉 -->
    <el-drawer
      v-model="showTaskMonitor"
      title="任务监控"
      direction="rtl"
      size="40%"
    >
      <TaskMonitorDrawer />
    </el-drawer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import TaskMonitorDrawer from './TaskMonitorDrawer.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()

const showTaskMonitor = ref(false)
let taskPollingTimer: number | null = null

// 菜单路由配置
const menuRoutes = [
  { path: '/dashboard', meta: { title: '仪表板', icon: 'Monitor' } },
  { path: '/data', meta: { title: '数据管理', icon: 'DataBoard' } },
  { path: '/training', meta: { title: '模型训练', icon: 'Setting' } },
  { path: '/prediction', meta: { title: '预测分析', icon: 'TrendCharts' } },
  { path: '/tasks', meta: { title: '任务监控', icon: 'Monitor' } },
  { path: '/comparison', meta: { title: '模型比较', icon: 'DataAnalysis' } }
]

// 计算属性
const currentRoute = computed(() => route)
const runningTasksCount = computed(() => taskStore.runningTasks.length)

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'status':
      // 显示系统状态
      break
    case 'help':
      // 打开帮助文档
      break
    case 'about':
      // 显示关于信息
      break
  }
}

// 启动任务轮询
const startTaskPolling = () => {
  // 每5秒检查一次运行中的任务状态
  taskPollingTimer = setInterval(() => {
    if (taskStore.runningTasks.length > 0) {
      taskStore.pollRunningTasks()
    }
  }, 5000)
}

// 停止任务轮询
const stopTaskPolling = () => {
  if (taskPollingTimer) {
    clearInterval(taskPollingTimer)
    taskPollingTimer = null
  }
}

onMounted(() => {
  // 初始化任务列表
  taskStore.fetchTasks()
  // 启动任务轮询
  startTaskPolling()
})

onUnmounted(() => {
  stopTaskPolling()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #404854;
  color: #fff;
}

.logo h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.logo p {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #bfcbd9;
}

.sidebar-menu {
  border: none;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-btn {
  color: #606266;
  font-size: 14px;
}

.task-badge {
  margin-right: 10px;
}

.content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
