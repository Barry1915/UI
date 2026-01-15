<template>
  <div class="hero">
    <div class="hero-inner card">
      <h1>竹韵书阁</h1>
      <p>集借阅、预约、荐购、盘点、统计于一体的图书馆管理平台</p>
      <div class="actions">
        <RouterLink class="button-primary" to="/admin">进入管理后台</RouterLink>
        <RouterLink class="button-primary" to="/pvz">玩一局 PVZ</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style lang="scss" scoped>
.hero {
  display: grid; place-items: center; min-height: 80vh;
  background-image: url('https://images.unsplash.com/photo-1524213452769-9bcd8ae44f83?q=80&w=1200&auto=format&fit=crop');
  background-size: cover; background-position: center; position: relative;
}
.hero::after { content: ''; position: absolute; inset: 0; background: rgba(251,250,245,0.8); }
.hero-inner { position: relative; padding: 48px; max-width: 720px; text-align: center; }
.hero h1 { margin: 0 0 12px; font-size: 48px; letter-spacing: 8px; }
.hero p { margin: 0 0 24px; color: #6b665f; }
.actions { display: flex; gap: 12px; justify-content: center; }
</style>
