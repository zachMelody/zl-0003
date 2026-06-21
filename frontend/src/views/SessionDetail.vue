<template>
  <div class="session-detail" ref="containerRef">
    <div class="detail-header">
      <button @click="goBack" class="back-btn">← 返回列表</button>
      <div class="header-info">
        <h1 class="session-title">{{ session?.title || 'Untitled' }}</h1>
        <div class="header-meta">
          <span v-if="session?.model" class="model-tag">{{ session.model }}</span>
          <span class="meta-text">💬 {{ session?.message_count }} 条消息</span>
          <span class="meta-text">🔢 {{ formatTokens(session?.total_tokens || 0) }} Tokens</span>
          <span class="meta-text">🕐 {{ session?.updated_at_str }}</span>
        </div>
      </div>
    </div>

    <div class="detail-content">
      <div class="messages-container" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="msg.id"
          :ref="el => setMessageRef(el, index)"
          :id="'msg-' + index"
          class="message-item"
          :class="{ user: msg.role === 'user', assistant: msg.role === 'assistant' }"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">{{ getRoleLabel(msg.role) }}</span>
              <span v-if="msg.model" class="message-model">{{ msg.model }}</span>
              <span class="message-time">{{ msg.created_at_str }}</span>
            </div>
            <div class="message-body">
              <pre><code>{{ msg.content }}</code></pre>
            </div>
            <div v-if="msg.tokens > 0" class="message-tokens">
              {{ msg.tokens }} tokens
              <span v-if="msg.input_tokens > 0">(输入: {{ msg.input_tokens }})</span>
              <span v-if="msg.output_tokens > 0">(输出: {{ msg.output_tokens }})</span>
            </div>
          </div>
        </div>
      </div>

      <div class="floating-nav">
        <div class="nav-header">
          <span>快速跳转</span>
          <span class="msg-count">{{ messages.length }} 条</span>
        </div>
        <div class="nav-list" ref="navList">
          <div
            v-for="(msg, index) in navItems"
            :key="index"
            class="nav-item"
            :class="{ 
              active: activeMessageIndex === index,
              user: msg.role === 'user',
              assistant: msg.role === 'assistant'
            }"
            @click="jumpToMessage(index)"
            @mouseenter="hoveredIndex = index"
            @mouseleave="hoveredIndex = -1"
          >
            <div class="nav-dot"></div>
            <div class="nav-label" :title="msg.preview">
              <span class="nav-role">{{ getRoleLabel(msg.role) }}</span>
              <span class="nav-preview">{{ msg.preview }}</span>
            </div>

            <div
              v-if="hoveredIndex === index"
              class="nav-tooltip"
            >
              <div class="tooltip-header">
                <span>{{ getRoleLabel(msg.role) }}</span>
                <span class="tooltip-time">{{ msg.time }}</span>
              </div>
              <div class="tooltip-content">{{ msg.preview }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSessionDetail } from '@/api/session'

const route = useRoute()
const router = useRouter()

const session = ref(null)
const messages = ref([])
const containerRef = ref(null)
const messagesContainer = ref(null)
const navList = ref(null)
const activeMessageIndex = ref(0)
const hoveredIndex = ref(-1)
const messageRefs = ref([])

const setMessageRef = (el, index) => {
  if (el) {
    messageRefs.value[index] = el
  }
}

const navItems = computed(() => {
  return messages.value.map((msg) => {
    const preview = msg.content
      .replace(/\n/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 60)
    return {
      role: msg.role,
      preview: preview || '(空消息)',
      time: msg.created_at_str || '',
    }
  })
})

const formatTokens = (tokens) => {
  if (!tokens) return '0'
  if (tokens >= 1000000) return (tokens / 1000000).toFixed(2) + 'M'
  if (tokens >= 1000) return (tokens / 1000).toFixed(1) + 'K'
  return tokens.toString()
}

const getRoleLabel = (role) => {
  const labels = {
    user: '用户',
    assistant: '助手',
    system: '系统',
  }
  return labels[role] || role
}

const goBack = () => {
  router.push('/sessions')
}

const jumpToMessage = (index) => {
  const msgEl = messageRefs.value[index]
  if (msgEl && messagesContainer.value) {
    const container = messagesContainer.value
    const msgRect = msgEl.getBoundingClientRect()
    const containerRect = container.getBoundingClientRect()
    const scrollTop = msgEl.offsetTop - container.offsetTop - 20
    container.scrollTo({
      top: scrollTop,
      behavior: 'smooth',
    })
    activeMessageIndex.value = index
  }
}

const handleScroll = () => {
  if (!messagesContainer.value || messages.value.length === 0) return

  const container = messagesContainer.value
  const containerTop = container.getBoundingClientRect().top
  const scrollTop = container.scrollTop
  const containerHeight = container.clientHeight

  let closestIndex = 0
  let closestDistance = Infinity

  messageRefs.value.forEach((el, index) => {
    if (el) {
      const elTop = el.offsetTop - container.offsetTop
      const distance = Math.abs(elTop - scrollTop - 20)
      if (distance < closestDistance) {
        closestDistance = distance
        closestIndex = index
      }
    }
  })

  activeMessageIndex.value = closestIndex

  const navListEl = navList.value
  if (navListEl) {
    const activeEl = navListEl.querySelector('.nav-item.active')
    if (activeEl) {
      const navListRect = navListEl.getBoundingClientRect()
      const activeRect = activeEl.getBoundingClientRect()
      if (
        activeRect.top < navListRect.top ||
        activeRect.bottom > navListRect.bottom
      ) {
        activeEl.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth',
        })
      }
    }
  }
}

const loadSession = async () => {
  const id = route.params.id
  if (!id) return

  try {
    const data = await getSessionDetail(id)
    session.value = data
    messages.value = data.messages || []
  } catch (err) {
    console.error('Failed to load session:', err)
    alert('加载会话失败')
  }
}

watch(
  () => route.params.id,
  () => {
    loadSession()
  }
)

onMounted(() => {
  loadSession()
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.addEventListener('scroll', handleScroll)
    }
  })
})

onUnmounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.removeEventListener('scroll', handleScroll)
  }
})
</script>

<style scoped>
.session-detail {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.detail-header {
  background: #fff;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.back-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 0;
  margin-bottom: 8px;
}

.back-btn:hover {
  color: #89b4fa;
}

.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.session-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.model-tag {
  padding: 4px 10px;
  background: #e0e7ff;
  color: #4f46e5;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.meta-text {
  font-size: 13px;
  color: #666;
}

.detail-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  padding-right: 260px;
}

.message-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: #dbeafe;
}

.message-item.assistant .message-avatar {
  background: #dcfce7;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-role {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.message-model {
  font-size: 12px;
  color: #888;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-body {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.message-body pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.message-body code {
  font-family: inherit;
}

.message-tokens {
  margin-top: 6px;
  font-size: 11px;
  color: #aaa;
}

.floating-nav {
  position: fixed;
  right: 20px;
  top: 100px;
  width: 220px;
  max-height: calc(100vh - 140px);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 100;
}

.nav-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
  font-size: 14px;
  color: #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.msg-count {
  font-size: 12px;
  color: #999;
  font-weight: normal;
}

.nav-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.nav-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.nav-item:hover {
  background: #f5f5f5;
}

.nav-item.active {
  background: #eff6ff;
}

.nav-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.nav-item.user .nav-dot {
  background: #3b82f6;
}

.nav-item.assistant .nav-dot {
  background: #22c55e;
}

.nav-label {
  flex: 1;
  min-width: 0;
}

.nav-role {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: #666;
  margin-bottom: 2px;
}

.nav-preview {
  display: block;
  font-size: 12px;
  color: #888;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-item.active .nav-preview {
  color: #333;
}

.nav-tooltip {
  position: absolute;
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  width: 240px;
  background: #1e1e2e;
  color: #fff;
  padding: 10px 12px;
  border-radius: 8px;
  margin-right: 8px;
  z-index: 200;
  pointer-events: none;
  opacity: 0;
  animation: fadeIn 0.15s ease-out forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 500;
}

.tooltip-time {
  color: #999;
  font-size: 11px;
  font-weight: normal;
}

.tooltip-content {
  font-size: 12px;
  line-height: 1.4;
  color: #ddd;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}

.nav-tooltip::after {
  content: '';
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  border: 6px solid transparent;
  border-left-color: #1e1e2e;
}
</style>
