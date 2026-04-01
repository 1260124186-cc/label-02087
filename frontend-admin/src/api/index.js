import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { data } = response
    if (data.success) {
      return data.data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
  },
  error => {
    const message = error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 文件相关 API
export const fileApi = {
  upload: (file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  getList: () => api.get('/files'),

  getDetail: (id) => api.get(`/files/${id}`),

  delete: (id) => api.delete(`/files/${id}`)
}

// 报文相关 API
export const packetApi = {
  getList: (fileId, params = {}) => api.get(`/packets/${fileId}`, { params }),

  getDetail: (fileId, packetNo) => api.get(`/packets/${fileId}/${packetNo}`)
}

// 分析相关 API
export const analysisApi = {
  getProtocolStats: (fileId) => api.get(`/analysis/${fileId}/protocol-stats`),

  getTrafficTimeline: (fileId, interval = 1) =>
    api.get(`/analysis/${fileId}/traffic-timeline`, { params: { interval } }),

  getTopTalkers: (fileId, limit = 10) =>
    api.get(`/analysis/${fileId}/top-talkers`, { params: { limit } }),

  getDiagnosis: (fileId) => api.get(`/analysis/${fileId}/diagnosis`)
}

export default api
