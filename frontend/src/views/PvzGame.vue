<template>
  <div class="pvz-page">
    <header class="pvz-top card">
      <div class="left">
        <div class="title">植物大战僵尸 · 迷你版</div>
        <div class="subtitle">Python(FastAPI) 作为游戏引擎，Vue 负责渲染与交互</div>
      </div>
      <div class="right">
        <div class="sun-badge" title="阳光">
          <span class="sun-dot" />
          <span class="sun-num">{{ game?.sun ?? 0 }}</span>
        </div>

        <label class="difficulty">
          <span>难度</span>
          <select v-model.number="difficulty" @change="sendDifficulty">
            <option :value="1">轻松</option>
            <option :value="2">普通</option>
            <option :value="3">困难</option>
          </select>
        </label>

        <button class="button-primary" @click="toggleRun">
          {{ game?.running ? '暂停' : '开始' }}
        </button>
        <button class="btn-ghost" @click="resetGame">重置</button>
        <RouterLink class="btn-link" to="/">返回门户</RouterLink>
      </div>
    </header>

    <section class="pvz-body">
      <aside class="panel card">
        <div class="panel-title">植物卡片</div>
        <div class="cards">
          <button class="card-btn" :class="{ active: selected === 'sunflower' }" @click="selected = 'sunflower'">
            <div class="plant-icon sunflower" />
            <div class="txt">
              <div class="name">向日葵</div>
              <div class="desc">产出阳光</div>
            </div>
            <div class="cost">50</div>
          </button>
          <button class="card-btn" :class="{ active: selected === 'peashooter' }" @click="selected = 'peashooter'">
            <div class="plant-icon peashooter" />
            <div class="txt">
              <div class="name">豌豆射手</div>
              <div class="desc">自动射击</div>
            </div>
            <div class="cost">100</div>
          </button>
          <button class="card-btn" :class="{ active: selected === 'wallnut' }" @click="selected = 'wallnut'">
            <div class="plant-icon wallnut" />
            <div class="txt">
              <div class="name">坚果墙</div>
              <div class="desc">高生命值</div>
            </div>
            <div class="cost">50</div>
          </button>
        </div>

        <div class="tips">
          <div><b>左键</b>：在格子里放置选中植物</div>
          <div><b>右键</b>：移除该格子植物</div>
          <div><b>点击阳光</b>：拾取并增加阳光</div>
        </div>

        <div class="panel-kpis">
          <div class="kpi">
            <div class="k">连接</div>
            <div class="v" :class="{ ok: wsStatus === 'connected' }">{{ wsStatus }}</div>
          </div>
          <div class="kpi">
            <div class="k">Tick</div>
            <div class="v">{{ game?.tick ?? '-' }}</div>
          </div>
        </div>
      </aside>

      <main class="lawn card" @contextmenu.prevent>
        <div class="lawn-header">
          <div class="legend">
            <span class="chip plant">植物</span>
            <span class="chip zombie">僵尸</span>
            <span class="chip pea">豌豆</span>
            <span class="chip sun">阳光</span>
          </div>
          <div class="right">
            <span class="muted">提示：开局默认 150 阳光</span>
          </div>
        </div>

        <div class="lawn-stage">
          <div class="lanes">
            <div v-for="r in rows" :key="r" class="lane" :class="{ alt: (r - 1) % 2 === 1 }" />
          </div>

          <div class="grid">
            <div v-for="r in rows" :key="`row-${r}`" class="grid-row">
              <button
                v-for="c in cols"
                :key="`cell-${r}-${c}`"
                class="cell"
                @click="placePlant(r - 1, c - 1)"
                @contextmenu.prevent="removePlant(r - 1, c - 1)"
              >
                <div class="cell-inner">
                  <template v-if="plantAt(r - 1, c - 1)">
                    <div class="plant" :class="plantAt(r - 1, c - 1)!.type">
                      <div class="hp">
                        <div class="hp-fill" :style="{ width: hpWidth(plantAt(r - 1, c - 1)!.hp, plantAt(r - 1, c - 1)!.type) }" />
                      </div>
                    </div>
                  </template>
                </div>
              </button>
            </div>
          </div>

          <div class="entities">
            <button
              v-for="s in game?.sunTokens ?? []"
              :key="`sun-${s.id}`"
              class="sun-token"
              :style="entityStyle(s.col + 0.12, s.row + 0.12)"
              @click="collectSun(s.id)"
              title="点击拾取阳光"
            >
              <span class="sun-glow" />
              <span class="sun-core">☀</span>
              <span class="sun-value">+{{ s.value }}</span>
            </button>

            <div
              v-for="p in game?.projectiles ?? []"
              :key="`pea-${p.id}`"
              class="pea"
              :style="entityStyle(p.x, p.row + 0.42)"
            />

            <div
              v-for="z in game?.zombies ?? []"
              :key="`z-${z.id}`"
              class="zombie"
              :style="entityStyle(z.x, z.row + 0.14)"
            >
              <div class="z-head" />
              <div class="z-body" />
              <div class="z-hp">
                <div class="z-hp-fill" :style="{ width: zombieHpWidth(z.hp) }" />
              </div>
            </div>
          </div>

          <div class="house-line" />
        </div>

        <div v-if="notice" class="toast">{{ notice }}</div>

        <div v-if="game?.gameOver" class="overlay">
          <div class="overlay-card card">
            <div class="big">游戏结束</div>
            <div class="reason">{{ game?.gameOverReason ?? 'unknown' }}</div>
            <div class="overlay-actions">
              <button class="button-primary" @click="resetGame">再来一局</button>
              <button class="btn-ghost" @click="toggleRun(false)">保持暂停</button>
            </div>
          </div>
        </div>
      </main>

      <aside class="panel card">
        <div class="panel-title">战况面板</div>
        <div class="battle-kpis">
          <div class="battle-kpi">
            <div class="k">僵尸数</div>
            <div class="v">{{ (game?.zombies ?? []).length }}</div>
          </div>
          <div class="battle-kpi">
            <div class="k">植物数</div>
            <div class="v">{{ (game?.plants ?? []).length }}</div>
          </div>
          <div class="battle-kpi">
            <div class="k">豌豆</div>
            <div class="v">{{ (game?.projectiles ?? []).length }}</div>
          </div>
        </div>

        <div class="log">
          <div class="log-title">事件日志</div>
          <div class="log-list">
            <div v-for="(l, idx) in logs" :key="`log-${idx}`" class="log-item">{{ l }}</div>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type PlantType = 'peashooter' | 'sunflower' | 'wallnut'

type GameState = {
  tick: number
  running: boolean
  gameOver: boolean
  gameOverReason?: string | null
  sun: number
  difficulty: number
  config: { rows: number; cols: number; tickMs: number }
  plants: Array<{ id: number; type: PlantType; row: number; col: number; hp: number }>
  zombies: Array<{ id: number; row: number; x: number; hp: number }>
  projectiles: Array<{ id: number; row: number; x: number }>
  sunTokens: Array<{ id: number; row: number; col: number; value: number; expiresAtTick: number }>
}

const wsStatus = ref<'disconnected' | 'connecting' | 'connected'>('disconnected')
const wsRef = ref<WebSocket | null>(null)
const game = ref<GameState | null>(null)

const rows = computed(() => game.value?.config.rows ?? 5)
const cols = computed(() => game.value?.config.cols ?? 9)

const selected = ref<PlantType>('peashooter')
const difficulty = ref<number>(1)
const notice = ref<string>('')
const logs = ref<string[]>([])

const plantMap = computed(() => {
  const m = new Map<string, GameState['plants'][number]>()
  for (const p of game.value?.plants ?? []) m.set(`${p.row},${p.col}`, p)
  return m
})

function plantAt(row: number, col: number) {
  return plantMap.value.get(`${row},${col}`)
}

function pushLog(line: string) {
  logs.value.unshift(`[${new Date().toLocaleTimeString()}] ${line}`)
  logs.value = logs.value.slice(0, 80)
}

function showNotice(msg: string) {
  notice.value = msg
  window.setTimeout(() => {
    if (notice.value === msg) notice.value = ''
  }, 1800)
}

function wsUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/pvz/ws`
}

let reconnectTimer: number | null = null

function connect() {
  wsStatus.value = 'connecting'
  const ws = new WebSocket(wsUrl())
  wsRef.value = ws

  ws.onopen = () => {
    wsStatus.value = 'connected'
    pushLog('WebSocket 已连接')
  }
  ws.onclose = () => {
    wsStatus.value = 'disconnected'
    pushLog('WebSocket 已断开，准备重连…')
    scheduleReconnect()
  }
  ws.onerror = () => {
    wsStatus.value = 'disconnected'
  }
  ws.onmessage = (evt) => {
    try {
      const msg = JSON.parse(String(evt.data))
      if (msg.type === 'hello') {
        game.value = msg.state
        difficulty.value = msg.state.difficulty ?? 1
        pushLog('收到初始状态')
        return
      }
      if (msg.type === 'state') {
        const prev = game.value
        game.value = msg.state
        if (prev && !prev.gameOver && msg.state.gameOver) pushLog(`游戏结束：${msg.state.gameOverReason ?? 'unknown'}`)
        return
      }
      if (msg.type === 'ack') {
        if (msg.action === 'place' && msg.ok === false) {
          const err = msg.error ?? 'place_failed'
          if (err === 'not_enough_sun') showNotice(`阳光不足（需要 ${msg.need}，当前 ${msg.have}）`)
          else if (err === 'cell_occupied') showNotice('该格子已有植物')
          else showNotice(`放置失败：${err}`)
        }
        if (msg.action === 'collectSun' && msg.ok === true) pushLog(`拾取阳光 +${msg.value}`)
        return
      }
    } catch {
      // ignore
    }
  }
}

function scheduleReconnect() {
  if (reconnectTimer != null) return
  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null
    connect()
  }, 900)
}

function send(payload: Record<string, unknown>) {
  const ws = wsRef.value
  if (!ws || ws.readyState !== WebSocket.OPEN) return
  ws.send(JSON.stringify(payload))
}

function toggleRun(force?: boolean) {
  send({ type: 'toggle', running: force })
}

function resetGame() {
  logs.value = []
  send({ type: 'reset' })
  showNotice('已重置')
}

function sendDifficulty() {
  send({ type: 'difficulty', value: difficulty.value })
  pushLog(`难度设置为 ${difficulty.value}`)
}

function placePlant(row: number, col: number) {
  send({ type: 'place', row, col, plantType: selected.value })
}

function removePlant(row: number, col: number) {
  send({ type: 'remove', row, col })
}

function collectSun(id: number) {
  send({ type: 'collectSun', id })
}

const CELL_W = 86
const CELL_H = 84

function entityStyle(x: number, y: number) {
  return {
    left: `${x * CELL_W}px`,
    top: `${y * CELL_H}px`,
  }
}

function hpWidth(hp: number, type: PlantType) {
  const max = type === 'wallnut' ? 18 : type === 'peashooter' ? 5 : 4
  const pct = Math.max(0, Math.min(1, hp / max))
  return `${Math.round(pct * 100)}%`
}

function zombieHpWidth(hp: number) {
  const max = difficulty.value === 3 ? 14 : difficulty.value === 2 ? 11 : 8
  const pct = Math.max(0, Math.min(1, hp / max))
  return `${Math.round(pct * 100)}%`
}

onMounted(() => connect())
onBeforeUnmount(() => {
  if (reconnectTimer != null) window.clearTimeout(reconnectTimer)
  reconnectTimer = null
  wsRef.value?.close()
})
</script>

<style scoped lang="scss">
.pvz-page {
  padding: 16px;
  display: grid;
  gap: 16px;
}

.pvz-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.78));
  backdrop-filter: blur(10px);
}
.title { font-size: 18px; font-weight: 700; letter-spacing: 2px; }
.subtitle { font-size: 12px; color: #6b665f; margin-top: 4px; }
.right { display: flex; align-items: center; gap: 10px; }

.sun-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255, 223, 87, 0.35), rgba(255, 200, 80, 0.15));
  border: 1px solid rgba(199, 164, 91, 0.35);
}
.sun-dot {
  width: 14px; height: 14px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff7c2, #ffd34d 45%, #f5a623 78%);
  box-shadow: 0 0 16px rgba(255, 205, 65, 0.55);
}
.sun-num { font-weight: 700; min-width: 32px; text-align: right; }

.difficulty { display: inline-flex; align-items: center; gap: 8px; color: #6b665f; font-size: 12px; }
.difficulty select { padding: 6px 8px; border-radius: 8px; border: 1px solid #ece7da; background: white; }

.btn-ghost {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #ece7da;
  background: rgba(255,255,255,0.7);
  cursor: pointer;
}
.btn-link { text-decoration: none; color: #2f6f4e; padding: 8px 10px; border-radius: 8px; }
.btn-link:hover { background: rgba(47,111,78,0.08); }

.pvz-body {
  display: grid;
  grid-template-columns: 260px 1fr 260px;
  gap: 16px;
  align-items: start;
}

.panel { padding: 14px; }
.panel-title { font-weight: 700; letter-spacing: 1px; margin-bottom: 10px; }
.cards { display: grid; gap: 10px; }
.card-btn {
  display: grid;
  grid-template-columns: 42px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #ece7da;
  background: rgba(255,255,255,0.75);
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.card-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 26px rgba(0,0,0,0.08); }
.card-btn.active { border-color: rgba(47,111,78,0.55); box-shadow: 0 0 0 2px rgba(47,111,78,0.12) inset; }
.txt .name { font-weight: 700; }
.txt .desc { color: #6b665f; font-size: 12px; margin-top: 2px; }
.cost { font-weight: 700; color: #6b665f; }

.plant-icon {
  width: 42px; height: 42px; border-radius: 12px;
  border: 1px solid #ece7da;
  background: radial-gradient(circle at 35% 35%, #fff, #f5f2ea);
  position: relative;
  overflow: hidden;
}
.plant-icon.sunflower::after {
  content: "";
  position: absolute; inset: 6px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 50%, #7a4b00 0 28%, transparent 29%),
    radial-gradient(circle at 35% 35%, #fff4b3, #ffd34d 45%, #f5a623 80%);
  box-shadow: 0 0 14px rgba(255, 210, 90, 0.45);
}
.plant-icon.peashooter::after {
  content: "";
  position: absolute; inset: 6px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #d4ffda, #32c36a 55%, #1f8a70 92%);
  box-shadow: inset 0 -6px 10px rgba(0,0,0,0.12);
}
.plant-icon.wallnut::after {
  content: "";
  position: absolute; inset: 7px;
  border-radius: 14px;
  background: linear-gradient(180deg, #d4a774, #a8723c);
  box-shadow: inset 0 -10px 16px rgba(0,0,0,0.18);
}

.tips { margin-top: 12px; color: #6b665f; font-size: 12px; display: grid; gap: 6px; }
.panel-kpis { margin-top: 12px; display: grid; gap: 8px; }
.kpi { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-radius: 10px; background: rgba(243,239,227,0.55); border: 1px solid #ece7da; }
.kpi .k { color: #6b665f; font-size: 12px; }
.kpi .v { font-weight: 700; }
.kpi .v.ok { color: #2f6f4e; }

.lawn { padding: 12px; position: relative; overflow: hidden; }
.lawn-header { display: flex; align-items: center; justify-content: space-between; padding: 0 4px 10px; }
.legend { display: flex; gap: 8px; align-items: center; }
.chip { font-size: 12px; padding: 6px 8px; border-radius: 999px; border: 1px solid #ece7da; background: rgba(255,255,255,0.7); }
.chip.plant { border-color: rgba(47,111,78,0.35); }
.chip.zombie { border-color: rgba(192,57,43,0.35); }
.chip.pea { border-color: rgba(31,138,112,0.35); }
.chip.sun { border-color: rgba(199,164,91,0.45); }
.muted { color: #6b665f; font-size: 12px; }

.lawn-stage {
  position: relative;
  border-radius: 14px;
  border: 1px solid #ece7da;
  background:
    radial-gradient(circle at 20% 0%, rgba(31,138,112,0.12), transparent 55%),
    radial-gradient(circle at 80% 100%, rgba(199,164,91,0.12), transparent 55%),
    linear-gradient(180deg, #f6fbf6, #eef7ee);
  overflow: hidden;
}

.lanes { position: absolute; inset: 0; display: grid; grid-template-rows: repeat(5, 84px); }
.lane { border-bottom: 1px dashed rgba(47,111,78,0.12); }
.lane.alt { background: rgba(47,111,78,0.05); }

.grid { position: relative; padding: 8px; display: grid; gap: 6px; }
.grid-row { display: grid; grid-template-columns: repeat(9, 86px); gap: 6px; }
.cell {
  height: 84px;
  border-radius: 12px;
  border: 1px solid rgba(47,111,78,0.18);
  background: rgba(255,255,255,0.55);
  cursor: pointer;
  transition: transform 0.08s ease, box-shadow 0.08s ease;
}
.cell:hover { transform: translateY(-1px); box-shadow: 0 10px 20px rgba(0,0,0,0.07); }
.cell-inner { width: 100%; height: 100%; position: relative; display: grid; place-items: center; }

.plant {
  width: 56px; height: 56px; border-radius: 16px;
  position: relative;
  filter: drop-shadow(0 10px 18px rgba(0,0,0,0.12));
}
.plant::after { content: ""; position: absolute; inset: 8px; border-radius: 14px; }
.plant.sunflower::after {
  background:
    radial-gradient(circle at 50% 50%, #7a4b00 0 24%, transparent 25%),
    radial-gradient(circle at 35% 35%, #fff4b3, #ffd34d 45%, #f5a623 80%);
}
.plant.peashooter::after {
  background: radial-gradient(circle at 35% 35%, #d4ffda, #32c36a 55%, #1f8a70 92%);
}
.plant.wallnut::after {
  background: linear-gradient(180deg, #d4a774, #a8723c);
}
.hp {
  position: absolute; left: 6px; right: 6px; bottom: -8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(0,0,0,0.15);
  overflow: hidden;
}
.hp-fill { height: 100%; background: linear-gradient(90deg, #2f6f4e, #1f8a70); }

.entities { position: absolute; inset: 8px; pointer-events: none; }
.pea {
  width: 10px; height: 10px; border-radius: 999px;
  background: radial-gradient(circle at 35% 35%, #e6ffe8, #32c36a 55%, #1f8a70 92%);
  box-shadow: 0 0 14px rgba(31,138,112,0.35);
  position: absolute;
  pointer-events: none;
}

.zombie {
  width: 62px; height: 62px;
  position: absolute;
  pointer-events: none;
  filter: drop-shadow(0 12px 18px rgba(0,0,0,0.16));
  animation: bob 0.9s ease-in-out infinite;
}
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-2px); } }
.z-head {
  width: 22px; height: 22px; border-radius: 8px;
  background: linear-gradient(180deg, #a5d6a7, #6aa26d);
  position: absolute; left: 6px; top: 8px;
}
.z-body {
  width: 44px; height: 40px; border-radius: 14px;
  background: linear-gradient(180deg, #7e8f98, #5f6e76);
  position: absolute; left: 12px; top: 16px;
  box-shadow: inset 0 -10px 16px rgba(0,0,0,0.18);
}
.z-hp {
  position: absolute; left: 6px; right: 6px; bottom: 2px;
  height: 7px; border-radius: 999px;
  background: rgba(0,0,0,0.18);
  overflow: hidden;
}
.z-hp-fill { height: 100%; background: linear-gradient(90deg, #c0392b, #ff6b5b); }

.sun-token {
  position: absolute;
  width: 54px; height: 54px;
  border: 0;
  border-radius: 16px;
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(199,164,91,0.35);
  cursor: pointer;
  pointer-events: auto;
  display: grid;
  place-items: center;
  box-shadow: 0 14px 28px rgba(0,0,0,0.12);
  animation: floaty 1.4s ease-in-out infinite;
}
@keyframes floaty { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
.sun-glow {
  position: absolute; inset: -6px;
  border-radius: 18px;
  background: radial-gradient(circle at 35% 35%, rgba(255,244,179,0.7), rgba(255,211,77,0.35), transparent 70%);
  filter: blur(2px);
}
.sun-core { position: relative; font-size: 22px; }
.sun-value { position: absolute; bottom: 6px; right: 8px; font-size: 11px; color: #7a4b00; font-weight: 700; }

.house-line {
  position: absolute;
  left: 10px;
  top: 8px;
  bottom: 8px;
  width: 6px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(192,57,43,0.25), rgba(192,57,43,0.08));
}

.toast {
  position: absolute;
  left: 50%;
  bottom: 16px;
  transform: translateX(-50%);
  padding: 10px 12px;
  border-radius: 999px;
  border: 1px solid #ece7da;
  background: rgba(255,255,255,0.92);
  box-shadow: 0 14px 34px rgba(0,0,0,0.12);
  font-size: 12px;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(29, 27, 22, 0.35);
  display: grid;
  place-items: center;
}
.overlay-card { padding: 18px; width: min(420px, 92%); text-align: center; }
.big { font-size: 22px; font-weight: 800; letter-spacing: 4px; }
.reason { margin-top: 8px; color: #6b665f; }
.overlay-actions { margin-top: 14px; display: flex; gap: 10px; justify-content: center; }

.battle-kpis { display: grid; gap: 10px; }
.battle-kpi { padding: 10px; border-radius: 12px; border: 1px solid #ece7da; background: rgba(243,239,227,0.55); display: flex; justify-content: space-between; align-items: center; }
.battle-kpi .k { color: #6b665f; font-size: 12px; }
.battle-kpi .v { font-weight: 800; font-size: 18px; }

.log { margin-top: 14px; }
.log-title { font-weight: 700; margin-bottom: 10px; }
.log-list { max-height: 360px; overflow: auto; padding-right: 4px; }
.log-item { font-size: 12px; color: #4b4741; padding: 8px 10px; border-radius: 10px; border: 1px solid #ece7da; background: rgba(255,255,255,0.75); margin-bottom: 8px; }
</style>

