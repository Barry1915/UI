<template>
  <div class="grid">
    <div class="card kpi">
      <div>
        <div class="label">馆藏总量</div>
        <div class="value">12,380</div>
      </div>
    </div>
    <div class="card kpi">
      <div>
        <div class="label">本月借阅</div>
        <div class="value">1,026</div>
      </div>
    </div>
    <div class="card chart" ref="chartRef" style="height:320px"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref<HTMLDivElement | null>(null)

onMounted(() => {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: {},
    xAxis: { type: 'category', data: ['一','二','三','四','五','六','日'] },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: [120, 200, 150, 80, 70, 110, 130], itemStyle: { color: '#2f6f4e' } }]
  })
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.kpi { display:flex; align-items:center; justify-content: center; min-height: 120px; }
.label { color: #6b665f; }
.value { font-size: 36px; font-weight: 600; }
</style>
