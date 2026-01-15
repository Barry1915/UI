# PVZ（植物大战僵尸）Mini · Python + Vue

本仓库在原有“竹韵书阁”管理系统（Vue + Java）基础上，额外增加了一个**可快速启动的迷你版 PVZ**：

- **后端**：Python `FastAPI`（游戏引擎 + WebSocket 实时推送）
- **前端**：Vue3 + Vite（网格草坪渲染、放置植物、僵尸推进、豌豆与阳光动画）

入口页面：`/pvz`

---

## 快速启动（推荐：Docker）

确保已安装 `docker` 与 `docker compose`，在仓库根目录执行：

```bash
docker compose up --build
```

然后打开：

- PVZ 页面：`http://localhost:8088/pvz`
-（可选）后端健康检查：`http://localhost:8000/pvz/health`

停止：

```bash
docker compose down
```

---

## 本地开发启动（无需 Docker）

### 1) 启动 PVZ Python 后端

```bash
cd pvz_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) 启动 Vue 前端

```bash
cd frontend
npm install
npm run dev
```

打开：

- `http://localhost:5173/pvz`

说明：

- 开发模式下，Vite 已配置 `/pvz` 代理到 `http://localhost:8000`（含 WebSocket），所以前端会自动连到 `ws://localhost:5173/pvz/ws`。

---

## 玩法说明

- **左键点击格子**：放置当前选中的植物
- **右键点击格子**：移除该格子植物
- **点击阳光**：拾取阳光（增加资源）
- **开始/暂停/重置**：顶部工具栏
- **难度**：影响僵尸血量与刷新频率

---

## 目录结构（与 PVZ 相关）

- `pvz_backend/`：Python FastAPI 后端（`/pvz/ws` WebSocket）
- `frontend/src/views/PvzGame.vue`：PVZ 页面（富 UI + 实时渲染）
- `docker-compose.yml`：一键启动 PVZ（`pvz-web` + `pvz-backend`）

---

## 常见问题

- **访问 `/pvz` 白屏/404**：请使用 `http://localhost:8088/pvz`（Docker）或 `http://localhost:5173/pvz`（本地 dev）。Vue Router 使用 history 模式，静态部署需要 fallback（已在 nginx 配置中处理）。
- **WebSocket see disconnected**：确认后端端口 `8000` 可用，且前端访问路径是同域的 `/pvz/ws`（Docker 已通过 Nginx 反代处理）。

