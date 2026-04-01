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

  getList: (options = {}) => api.get('/files', options),

  getDetail: (id, options = {}) => api.get(`/files/${id}`, options),

  delete: (id) => api.delete(`/files/${id}`)
}

// 报文相关 API
export const packetApi = {
  getList: (fileId, params = {}, options = {}) => api.get(`/packets/${fileId}`, { params, ...options }),

  getDetail: (fileId, packetNo, options = {}) => api.get(`/packets/${fileId}/${packetNo}`, options)
}

// 分析相关 API
export const analysisApi = {
  getProtocolStats: (fileId, options = {}) => api.get(`/analysis/${fileId}/protocol-stats`, options),

  getTrafficTimeline: (fileId, interval = 1, options = {}) =>
    api.get(`/analysis/${fileId}/traffic-timeline`, { params: { interval }, ...options }),

  getTopTalkers: (fileId, limit = 10, options = {}) =>
    api.get(`/analysis/${fileId}/top-talkers`, { params: { limit }, ...options }),

  getDiagnosis: (fileId, options = {}) => api.get(`/analysis/${fileId}/diagnosis`, options)
}

export default api
