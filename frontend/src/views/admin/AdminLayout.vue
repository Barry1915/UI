<template>
  <div class="layout">
    <aside class="sider">
      <div class="brand">竹韵书阁</div>
      <nav>
        <RouterLink to="/admin">总览</RouterLink>
        <RouterLink to="/admin/books">图书</RouterLink>
        <RouterLink to="/admin/borrow">借还</RouterLink>
        <RouterLink to="/admin/users">读者</RouterLink>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <RouterLink to="/">返回门户</RouterLink>
      </header>
      <section class="content">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts"></script>

<style lang="scss" scoped>
.layout { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }
.sider { background: linear-gradient(180deg, #203a43, #2c7744); color: white; padding: 24px; }
.brand { font-size: 22px; letter-spacing: 6px; margin-bottom: 24px; }
nav { display: grid; gap: 12px; }
nav a { color: white; text-decoration: none; padding: 8px 12px; border-radius: 8px; }
nav a.router-link-active { background: rgba(255,255,255,0.15); }
.main { display: grid; grid-template-rows: 56px 1fr; }
.topbar { display: flex; align-items: center; justify-content: flex-end; padding: 0 16px; background: #ffffffa6; border-bottom: 1px solid #ece7da; backdrop-filter: blur(8px); }
.content { padding: 16px; }
</style>
