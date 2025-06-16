import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '仪表板', icon: 'Monitor' }
        },
        {
          path: 'data',
          name: 'DataManagement',
          component: () => import('@/views/DataManagement.vue'),
          meta: { title: '数据管理', icon: 'DataBoard' }
        },
        {
          path: 'training',
          name: 'ModelTraining',
          component: () => import('@/views/ModelTraining.vue'),
          meta: { title: '模型训练', icon: 'Setting' }
        },
        {
          path: 'prediction',
          name: 'PredictionAnalysis',
          component: () => import('@/views/PredictionAnalysis.vue'),
          meta: { title: '预测分析', icon: 'TrendCharts' }
        },
        {
          path: 'tasks',
          name: 'TaskMonitoring',
          component: () => import('@/views/TaskMonitoring.vue'),
          meta: { title: '任务监控', icon: 'Monitor' }
        },
        {
          path: 'comparison',
          name: 'ModelComparison',
          component: () => import('@/views/ModelComparison.vue'),
          meta: { title: '模型比较', icon: 'DataAnalysis' }
        }
      ]
    }
  ]
})

export default router
