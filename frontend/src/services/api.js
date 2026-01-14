import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 通过vite代理到后端
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    if (error.response) {
      // 服务器返回错误状态码
      const message = error.response.data.detail || '请求失败'
      throw new Error(message)
    } else if (error.request) {
      // 网络错误
      throw new Error('网络连接失败，请检查后端服务是否运行')
    } else {
      // 其他错误
      throw new Error(error.message)
    }
  }
)

// API方法
export const pokemonAPI = {
  // 获取宝可梦列表
  getPokemon(params = {}) {
    return api.get('/pokemon', { params })
  },

  // 获取单个宝可梦详情
  getPokemonById(id) {
    return api.get(`/pokemon/${id}`)
  },

  // 搜索宝可梦
  searchPokemon(name) {
    return api.get(`/pokemon/search/${name}`)
  },

  // 获取统计信息
  getStats() {
    return api.get('/stats')
  }
}

export default api
