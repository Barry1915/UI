<template>
  <div class="login">
    <div class="panel card">
      <h2>后台登录</h2>
      <input v-model="username" placeholder="用户名"/>
      <input v-model="password" placeholder="密码" type="password"/>
      <button class="button-primary" @click="login">登录</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('admin')
const password = ref('admin123')
const router = useRouter()

async function login() {
  try {
    const { data } = await axios.post('/api/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('token', data.data?.token)
    router.push('/admin')
  } catch (e) {
    alert('登录失败')
  }
}
</script>

<style scoped>
.login { display:grid; place-items:center; min-height:100vh; }
.panel { padding:24px; width:360px; display:grid; gap:12px; }
.panel input { padding:10px 12px; border:1px solid #e6e0cf; border-radius:8px; }
</style>
