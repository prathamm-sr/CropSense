import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export const predictCrop = (features, top_k = 5) =>
  client.post('/predict', { features, top_k }).then(r => r.data)

export const getHistory = (page = 1, page_size = 20, crop = null) => {
  const params = { page, page_size }
  if (crop) params.crop = crop
  return client.get('/history', { params }).then(r => r.data)
}

export const getStats = () =>
  client.get('/history/stats').then(r => r.data)

export const deletePrediction = (id) =>
  client.delete(`/history/${id}`).then(r => r.data)

export const getCrops = () =>
  client.get('/predict/crops').then(r => r.data)
  // Note: this hits the ML service directly via backend proxy — 
  // if you want this, add a passthrough in backend or call port 8000 directly