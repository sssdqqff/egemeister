export type DataSourceMode = 'mock' | 'api'

export const DATA_SOURCE: DataSourceMode =
  import.meta.env.VITE_DATA_SOURCE === 'api' ? 'api' : 'mock'

export const IS_DEMO = DATA_SOURCE === 'mock'
