import axios from 'axios'
import { ElMessage } from 'element-plus'

// 生产模式（Electron 打包后 file:// 协议）需要绝对 URL
const isElectronProd = typeof window !== 'undefined' && window.location.protocol === 'file:'

const api = axios.create({
  baseURL: isElectronProd ? 'http://127.0.0.1:8765/api/v1' : '/api/v1',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截：FormData 时移除 Content-Type，让浏览器自动设置 multipart boundary
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

// 响应拦截
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default api
