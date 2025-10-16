import axios from 'axios'

const http = axios.create({ baseURL: '/' })

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
  return config
})

http.interceptors.response.use((resp) => resp, (err) => {
  if (err.response?.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/admin/login'
  }
  return Promise.reject(err)
})

export default http
