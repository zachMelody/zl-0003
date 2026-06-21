import request from './request'

export function getSessionList(params = {}) {
  return request.get('/sessions', { params })
}

export function getSessionDetail(id) {
  return request.get(`/sessions/${id}`)
}

export function getSessionMessages(id) {
  return request.get(`/sessions/${id}/messages`)
}

export function getModels() {
  return request.get('/sessions/models')
}

export function scanSessions() {
  return request.post('/sessions/scan')
}

export function deleteSession(id) {
  return request.delete(`/sessions/${id}`)
}
