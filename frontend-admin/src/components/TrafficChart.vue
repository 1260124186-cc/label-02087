<template>
  <div class="traffic-chart">
    <v-chart v-if="data.length" :option="chartOption" autoresize style="height: 280px;" />
    <div v-else class="empty-state">
      <el-icon><TrendCharts /></el-icon>
      <p>暂无流量数据</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { TrendCharts } from '@element-plus/icons-vue'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const props = defineProps({
  data: { type: Array, default: () => [] }
})

const chartOption = computed(() => {
  const times = props.data.map((_, i) => `${i}s`)
  const packets = props.data.map(item => item.packet_count)
  const bytes = props.data.map(item => item.bytes_count)

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E2E8F0',
      borderWidth: 1,
      textStyle: {
        color: '#1E293B'
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#94A3B8'
        }
      }
    },
    legend: {
      data: ['报文数', '字节数'],
      top: 0,
      textStyle: {
        color: '#475569',
        fontSize: 12
      }
    },
    grid: {
      left: 60,
      right: 60,
      top: 40,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: '#E2E8F0' }
      },
      axisLabel: {
        color: '#64748B'
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '报文数',
        position: 'left',
        nameTextStyle: {
          color: '#64748B',
          fontSize: 12
        },
        axisLine: {
          show: true,
          lineStyle: { color: '#2563EB' }
        },
        axisLabel: {
          color: '#64748B'
        },
        splitLine: {
          lineStyle: { color: '#F1F5F9' }
        }
      },
      {
        type: 'value',
        name: '字节数',
        position: 'right',
        nameTextStyle: {
          color: '#64748B',
          fontSize: 12
        },
        axisLine: {
          show: true,
          lineStyle: { color: '#10B981' }
        },
        axisLabel: {
          color: '#64748B'
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '报文数',
        type: 'line',
        data: packets,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(37, 99, 235, 0.3)' },
              { offset: 1, color: 'rgba(37, 99, 235, 0.05)' }
            ]
          }
        },
        lineStyle: { color: '#2563EB', width: 2 },
        itemStyle: { color: '#2563EB' }
      },
      {
        name: '字节数',
        type: 'line',
        yAxisIndex: 1,
        data: bytes,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
            ]
          }
        },
        lineStyle: { color: '#10B981', width: 2 },
        itemStyle: { color: '#10B981' }
      }
    ]
  }
})
</script>
