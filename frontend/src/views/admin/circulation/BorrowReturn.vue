<template>
  <div class="card" style="padding:16px">
    <h3>借还办理</h3>
    <div style="display:flex; gap:12px; align-items:center; margin: 12px 0;">
      <input v-model="userNo" placeholder="读者证号" style="padding:8px 12px; border-radius:8px; border:1px solid #e6e0cf;"/>
      <input v-model="isbn" placeholder="ISBN" style="padding:8px 12px; border-radius:8px; border:1px solid #e6e0cf;"/>
      <button class="button-primary" @click="borrow">借出</button>
      <button @click="ret">归还</button>
    </div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CirculationService } from './circulation.service'

const userNo = ref('U20250001')
const isbn = ref('9787300000000')
const message = ref('')

async function borrow() {
  try {
    await CirculationService.borrow(userNo.value, isbn.value)
    message.value = '借阅成功'
  } catch (e) {
    message.value = '借阅失败'
  }
}
async function ret() {
  try {
    await CirculationService.returnBook(userNo.value, isbn.value)
    message.value = '归还成功'
  } catch (e) {
    message.value = '归还失败'
  }
}
</script>
