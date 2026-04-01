<template>
  <div class="protocol-chart">
    <v-chart v-if="data.length" :option="chartOption" autoresize :style="{ height: chartHeight }" />
    <div v-else class="empty-state">
      <el-icon><PieChart /></el-icon>
      <p>暂无协议数据</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart as EchartsPie } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { PieChart } from '@element-plus/icons-vue'

use([CanvasRenderer, EchartsPie, TitleComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  data: { type: Array, default: () => [] }
})

// 响应式：检测屏幕宽度
const screenWidth = ref(window.innerWidth)

const handleResize = () => {
  screenWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const isSmallScreen = computed(() => screenWidth.value < 768)
const chartHeight = computed(() => isSmallScreen.value ? '320px' : '300px')

// 协议颜色映射
const colorMap = {
  TCP: '#2563EB',
  UDP: '#10B981',
  HTTP: '#F59E0B',
  HTTPS: '#059669',
  DNS: '#6B7280',
  ICMP: '#EF4444',
  ARP: '#64748B',
  SSH: '#0891B2',
  'HTTP-Alt': '#94A3B8',
  default: '#94A3B8'
}

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} 个 ({d}%)',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#E2E8F0',
    borderWidth: 1,
    textStyle: {
      color: '#1E293B',
      fontSize: 12
    }
  },
  legend: {
    orient: isSmallScreen.value ? 'horizontal' : 'vertical',
    right: isSmallScreen.value ? 'center' : 10,
    top: isSmallScreen.value ? 'bottom' : 'center',
    bottom: isSmallScreen.value ? 10 : 'auto',
    textStyle: {
      color: '#475569',
      fontSize: 12
    },
    itemGap: isSmallScreen.value ? 8 : 12,
    itemWidth: 14,
    itemHeight: 14
  },
  series: [
    {
      type: 'pie',
      radius: isSmallScreen.value ? ['30%', '55%'] : ['45%', '75%'],
      center: isSmallScreen.value ? ['50%', '38%'] : ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 13,
          fontWeight: '600',
          color: '#1E293B'
        },
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        }
      },
      data: props.data.map(item => ({
        name: item.protocol,
        value: item.count,
        itemStyle: {
          color: colorMap[item.protocol] || colorMap.default
        }
      }))
    }
  ]
}))
</script>

<style scoped>
.protocol-chart {
  min-height: 300px;
}

@media (max-width: 768px) {
  .protocol-chart {
    min-height: 320px;
  }
}
</style>
