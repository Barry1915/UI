<template>
  <div class="card" style="padding:16px">
    <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
      <h3>读者管理</h3>
      <button class="button-primary">新增读者</button>
    </header>
    <table style="width:100%; border-collapse: collapse;">
      <thead>
        <tr style="text-align:left; border-bottom:1px solid #eee;">
          <th>姓名</th>
          <th>证号</th>
          <th>手机号</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>张三</td>
          <td>U20250001</td>
          <td>138****0001</td>
          <td>正常</td>
          <td>
            <button class="button-primary">编辑</button>
            <button style="margin-left:8px">禁用</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts"></script>
