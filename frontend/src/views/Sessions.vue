<template>
  <div class="sessions-page">
    <div class="page-header">
      <h1>会话列表</h1>
      <p class="subtitle">浏览和查看所有会话记录</p>
    </div>

    <div class="toolbar">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索会话标题..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-btn">🔍</button>
      </div>

      <div class="filter-group">
        <select v-model="selectedModel" class="filter-select" @change="loadSessions">
          <option value="">全部模型</option>
          <option v-for="model in models" :key="model" :value="model">
            {{ model }}
          </option>
        </select>

        <select v-model="sortBy" class="filter-select" @change="loadSessions">
          <option value="updated_at">按更新时间</option>
          <option value="created_at">按创建时间</option>
          <option value="title">按标题</option>
          <option value="total_tokens">按 Token 数</option>
          <option value="message_count">按消息数</option>
        </select>

        <select v-model="sortOrder" class="filter-select" @change="loadSessions">
          <option value="desc">降序</option>
          <option value="asc">升序</option>
        </select>
      </div>
    </div>

    <div class="sessions-list">
      <div
        v-for="session in sessions"
        :key="session.id"
        class="session-item card"
        @click="goToDetail(session.id)"
      >
        <div class="session-header">
          <h3 class="session-title">{{ session.title || 'Untitled' }}</h3>
          <span v-if="session.model" class="model-tag">{{ session.model }}</span>
        </div>

        <div class="session-meta">
          <div class="meta-item">
            <span class="meta-icon">💬</span>
            <span>{{ session.message_count }} 条消息</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">🔢</span>
            <span>{{ formatTokens(session.total_tokens) }} Tokens</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">🕐</span>
            <span>{{ session.updated_at_str }}</span>
          </div>
        </div>

        <div class="session-footer">
          <span class="view-detail">查看详情 →</span>
        </div>
      </div>
    </div>

    <div v-if="sessions.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📭</div>
      <p>暂无会话数据</p>
      <p class="empty-hint">点击左侧"扫描会话"按钮导入会话数据</p>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div class="pagination" v-if="totalPages > 1">
      <button
        @click="changePage(page - 1)"
        :disabled="page <= 1"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ page }} / {{ totalPages }} 页，共 {{ total }} 条
      </span>
      <button
        @click="changePage(page + 1)"
        :disabled="page >= totalPages"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSessionList, getModels } from '@/api/session'

const router = useRouter()

const sessions = ref([])
const models = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const totalPages = ref(0)
const searchQuery = ref('')
const selectedModel = ref('')
const sortBy = ref('updated_at')
const sortOrder = ref('desc')

const formatTokens = (tokens) => {
  if (!tokens) return '0'
  if (tokens >= 1000000) return (tokens / 1000000).toFixed(2) + 'M'
  if (tokens >= 1000) return (tokens / 1000).toFixed(1) + 'K'
  return tokens.toString()
}

const loadSessions = async () => {
  loading.value = true
  try {
    const res = await getSessionList({
      page: page.value,
      page_size: pageSize,
      search: searchQuery.value,
      model: selectedModel.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
    })
    sessions.value = res.items
    total.value = res.total
    totalPages.value = res.total_pages
  } catch (err) {
    console.error('Failed to load sessions:', err)
  } finally {
    loading.value = false
  }
}

const loadModels = async () => {
  try {
    models.value = await getModels()
  } catch (err) {
    console.error('Failed to load models:', err)
  }
}

const handleSearch = () => {
  page.value = 1
  loadSessions()
}

const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    loadSessions()
  }
}

const goToDetail = (id) => {
  router.push(`/sessions/${id}`)
}

onMounted(() => {
  loadModels()
  loadSessions()
})
</script>

<style scoped>
.sessions-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 4px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-input {
  width: 280px;
  padding: 8px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #89b4fa;
}

.search-btn {
  padding: 8px 16px;
  background: #89b4fa;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.search-btn:hover {
  background: #74c7ec;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: #89b4fa;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-item {
  cursor: pointer;
  transition: all 0.2s;
}

.session-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.session-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model-tag {
  padding: 4px 10px;
  background: #e0e7ff;
  color: #4f46e5;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  margin-left: 12px;
  flex-shrink: 0;
}

.session-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-icon {
  font-size: 14px;
}

.session-footer {
  display: flex;
  justify-content: flex-end;
}

.view-detail {
  color: #89b4fa;
  font-size: 13px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 4px 0;
}

.empty-hint {
  font-size: 13px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #89b4fa;
  color: #89b4fa;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style>
