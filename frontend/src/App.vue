<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="logo">
        <h2>Session Analyzer</h2>
      </div>
      <nav class="nav-menu">
        <router-link to="/" class="nav-item">
          <span class="nav-icon">📊</span>
          <span>分析仪表盘</span>
        </router-link>
        <router-link to="/sessions" class="nav-item">
          <span class="nav-icon">💬</span>
          <span>会话列表</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="handleScan" class="scan-btn" :disabled="scanning">
          {{ scanning ? '扫描中...' : '🔍 扫描会话' }}
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { scanSessions } from '@/api/session'

const router = useRouter()
const scanning = ref(false)

const handleScan = async () => {
  scanning.value = true
  try {
    await scanSessions()
    alert('扫描完成！')
    router.go(0)
  } catch (err) {
    alert('扫描失败: ' + err.message)
  } finally {
    scanning.value = false
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: #1e1e2e;
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  padding: 20px;
  border-bottom: 1px solid #313244;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  padding: 12px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #bac2de;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #313244;
  color: #fff;
}

.nav-item.router-link-active {
  background: #45475a;
  color: #89b4fa;
  border-left: 3px solid #89b4fa;
  padding-left: 17px;
}

.nav-icon {
  font-size: 18px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #313244;
}

.scan-btn {
  width: 100%;
  padding: 10px 16px;
  background: #89b4fa;
  color: #1e1e2e;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.scan-btn:hover:not(:disabled) {
  background: #b4befe;
}

.scan-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.main-content {
  flex: 1;
  overflow: auto;
  background: #f5f5f7;
}
</style>
