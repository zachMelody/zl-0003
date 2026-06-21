# Claude Session 分析和查看工具

一个本地运行的 Claude 会话数据分析和查看工具，帮助您了解自己的 AI 使用习惯。

## 功能特性

### 分析侧
- **每日会话数量统计** - 查看每日的会话活跃趋势
- **每日 Token 消耗** - 追踪输入/输出 Token 的使用情况
- **模型使用分布** - 了解各模型的使用频率和 Token 消耗
- **使用时间分布** - 分析一天中各时段的使用活跃程度

### 查看侧
- **会话列表** - 浏览所有会话，支持搜索、筛选和排序
- **会话详情** - 查看完整的对话内容和上下文
- **浮标快速跳转** - 侧边导航浮标，快速定位到任意对话

### 技术特性
- **本地 SQLite 存储** - 已扫描的会话自动缓存，避免重复解析
- **多格式支持** - 自动识别多种常见的会话 JSON 格式
- **前后端分离** - Vue 3 前端 + FastAPI 后端
- **ECharts 图表** - 丰富的数据可视化展示

## 技术栈

### 后端
- **Python 3.11+**
- **uv** - Python 包管理器
- **FastAPI** - Web 框架
- **aiosqlite** - 异步 SQLite 数据库
- **Pydantic** - 数据验证

### 前端
- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **Vue Router** - 路由管理
- **ECharts** - 图表库
- **Axios** - HTTP 客户端

## 项目结构

```
3-codex-session-viewer/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/             # API 路由
│   │   │   ├── sessions.py  # 会话相关接口
│   │   │   └── stats.py     # 统计分析接口
│   │   ├── services/        # 业务逻辑
│   │   │   ├── session_parser.py   # 会话解析器
│   │   │   ├── session_service.py  # 会话服务
│   │   │   └── stats_service.py    # 统计服务
│   │   ├── schemas/         # Pydantic 数据模型
│   │   │   └── session.py
│   │   ├── config.py        # 配置管理
│   │   └── database.py      # 数据库操作
│   ├── data/
│   │   ├── sessions/        # 会话 JSON 文件存放目录
│   │   └── sessions.db      # SQLite 数据库文件
│   ├── generate_samples.py  # 生成示例数据脚本
│   ├── main.py              # 应用入口
│   └── pyproject.toml       # Python 项目配置
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── api/             # API 请求封装
│   │   ├── components/      # 公共组件
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 路由配置
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 入口文件
│   ├── index.html
│   ├── vite.config.js       # Vite 配置
│   └── package.json
└── README.md
```

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- uv (Python 包管理器)

### 1. 安装 uv

如果还没有安装 uv，请先安装：

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 后端设置

```bash
cd backend

# 安装依赖
uv sync

# （可选）生成示例数据用于测试
uv run python generate_samples.py data/sessions 20
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install
```

### 4. 启动开发服务器

**启动后端服务：**
```bash
cd backend
uv run python main.py
```
后端服务将在 `http://localhost:8000` 启动。

**启动前端服务（另一个终端）：**
```bash
cd frontend
npm run dev
```
前端服务将在 `http://localhost:5173` 启动。

### 5. 访问应用

在浏览器中打开 `http://localhost:5173`

点击左侧的 **「🔍 扫描会话」** 按钮，导入会话数据。

## 使用说明

### 导入会话数据

1. 将您的 Claude 会话 JSON 文件放入 `backend/data/sessions/` 目录
2. 点击侧边栏的「扫描会话」按钮
3. 系统会自动解析并存储到本地数据库中
4. 重复扫描时，已存在且未修改的文件会自动跳过

### 支持的会话格式

工具会自动识别以下格式的 JSON 会话文件：

**格式 1 - 标准格式：**
```json
{
  "id": "session-id",
  "title": "会话标题",
  "model": "claude-3-sonnet",
  "created_at": 1234567890,
  "messages": [
    {
      "role": "user",
      "content": "你好"
    }
  ]
}
```

**格式 2 - Claude Desktop 格式：**
```json
{
  "uuid": "...",
  "name": "会话名称",
  "chat_messages": [...],
  "created_at": "2024-01-01T00:00:00Z"
}
```

**格式 3 - 嵌套 conversation 格式：**
```json
{
  "conversation": {
    "messages": [...]
  }
}
```

### 分析仪表盘

- 顶部 4 个统计卡片展示整体使用情况
- 可选择时间范围：7 天 / 30 天 / 90 天 / 一年
- 四个图表：
  - **每日会话数量** - 柱状图展示每日活跃度
  - **每日 Token 消耗** - 面积图展示输入/输出 Token 趋势
  - **模型使用分布** - 环形饼图展示各模型占比
  - **使用时间分布** - 柱状图展示 24 小时分布

### 会话列表

- 支持按标题搜索
- 支持按模型筛选
- 支持多种排序方式（更新时间、创建时间、标题、Token 数、消息数）
- 分页浏览

### 会话详情

- 完整展示所有对话内容
- 用户消息和助手消息样式区分
- 每条消息显示 Token 使用情况
- **右侧浮标导航**：
  - 显示所有消息的预览
  - 点击快速跳转到对应消息
  - 鼠标悬停显示消息详情
  - 自动高亮当前浏览位置

## API 文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的 API 文档（Swagger UI）。

### 主要接口

#### 统计相关
- `GET /api/stats/summary` - 获取统计概览
- `GET /api/stats/daily-sessions` - 每日会话数
- `GET /api/stats/daily-tokens` - 每日 Token 使用
- `GET /api/stats/model-distribution` - 模型分布
- `GET /api/stats/hourly-distribution` - 时段分布

#### 会话相关
- `GET /api/sessions` - 获取会话列表（支持分页、搜索、筛选）
- `GET /api/sessions/{id}` - 获取会话详情
- `GET /api/sessions/{id}/messages` - 获取会话消息
- `GET /api/sessions/{id}/raw` - 获取原始数据
- `GET /api/sessions/models` - 获取可用模型列表
- `POST /api/sessions/scan` - 扫描会话目录
- `DELETE /api/sessions/{id}` - 删除会话

## 配置说明

### 后端配置

可以在 `backend/.env` 文件中配置（可选）：

```env
DEBUG=true
HOST=0.0.0.0
PORT=8000
DB_PATH=data/sessions.db
SESSIONS_DIR=data/sessions
CORS_ORIGINS=["http://localhost:5173"]
```

### 前端配置

在 `frontend/vite.config.js` 中修改代理设置：

```js
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 开发指南

### 添加新的解析格式

在 `backend/app/services/session_parser.py` 中添加新的解析方法：

1. 在 `_detect_parser` 中添加格式检测逻辑
2. 添加对应的解析方法
3. 方法返回统一格式的字典

### 添加新的统计指标

1. 在 `backend/app/services/stats_service.py` 添加统计方法
2. 在 `backend/app/api/stats.py` 添加 API 路由
3. 在 `frontend/src/api/stats.js` 添加前端 API 封装
4. 在前端仪表盘中添加新的图表组件

### 数据库迁移

如需修改数据库表结构：
1. 修改 `database.py` 中的建表 SQL
2. 删除旧的数据库文件 `data/sessions.db`
3. 重新启动服务会自动创建新表

## 常见问题

### Q: 扫描后没有数据？
A: 请确认 `backend/data/sessions/` 目录下有 JSON 文件，并且文件格式是支持的格式之一。

### Q: 如何导出数据库中的数据？
A: 直接备份 `backend/data/sessions.db` 文件即可。这是一个标准的 SQLite 数据库文件，可以用任何 SQLite 工具打开。

### Q: 支持哪些对话格式？
A: 目前支持多种常见的 JSON 会话格式。如果您的格式不被支持，可以参照 `session_parser.py` 添加新的解析器。

### Q: 扫描会重复解析已有文件吗？
A: 不会。系统会计算文件的 MD5 哈希值，只有新文件或内容有变化的文件才会被重新解析。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
