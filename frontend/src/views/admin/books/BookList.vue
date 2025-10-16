<template>
  <div class="card" style="padding:16px">
    <header style="display:flex; gap:8px; align-items:center; justify-content:space-between; margin-bottom:12px;">
      <div style="display:flex; gap:8px; align-items:center;">
        <input v-model="query" placeholder="检索 书名/作者/ISBN" style="padding:8px 12px; border-radius:8px; border:1px solid #e6e0cf; min-width: 320px;"/>
        <button class="button-primary" @click="fetchList">检索</button>
      </div>
      <button class="button-primary" @click="openCreate">新增图书</button>
    </header>

    <table style="width:100%; border-collapse: collapse;">
      <thead>
        <tr style="text-align:left; border-bottom:1px solid #eee;">
          <th>书名</th>
          <th>作者</th>
          <th>ISBN</th>
          <th>分类</th>
          <th>在馆</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in books" :key="b.id" style="border-bottom:1px solid #f3efe3;">
          <td>{{ b.title }}</td>
          <td>{{ b.author }}</td>
          <td>{{ b.isbn }}</td>
          <td>{{ b.category }}</td>
          <td>{{ b.availableCopies }}</td>
          <td>
            <button class="button-primary" @click="edit(b)">编辑</button>
            <button style="margin-left:8px" @click="remove(b)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { BookService, type Book } from '@/views/admin/books/book.service'

const books = ref<Book[]>([])
const query = ref('')

async function fetchList() {
  books.value = await BookService.list(query.value)
}
function openCreate() {
  alert('TODO: 打开新增弹窗')
}
function edit(b: Book) {
  alert('TODO: 编辑 ' + b.title)
}
async function remove(b: Book) {
  if (confirm('确认删除 "' + b.title + '"?')) {
    await BookService.remove(b.id!)
    await fetchList()
  }
}

onMounted(fetchList)
</script>
