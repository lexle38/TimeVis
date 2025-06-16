/* eslint-env node */
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@/api' {
  export * from '@/api/index'
}

declare module '@/types/api' {
  export * from '@/types/api'
}

declare module '@/stores/*' {
  export * from '@/stores/*'
}

declare module '@/utils/*' {
  export * from '@/utils/*'
}

declare module '@/components/*' {
  export * from '@/components/*'
}

declare module '@/views/*' {
  export * from '@/views/*'
}
