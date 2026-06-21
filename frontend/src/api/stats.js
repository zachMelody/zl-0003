import request from './request'

export function getStatsSummary() {
  return request.get('/stats/summary')
}

export function getDailySessions(days = 30) {
  return request.get('/stats/daily-sessions', { params: { days } })
}

export function getDailyTokens(days = 30) {
  return request.get('/stats/daily-tokens', { params: { days } })
}

export function getModelDistribution(days = null) {
  const params = days ? { days } : {}
  return request.get('/stats/model-distribution', { params })
}

export function getHourlyDistribution(days = null) {
  const params = days ? { days } : {}
  return request.get('/stats/hourly-distribution', { params })
}
