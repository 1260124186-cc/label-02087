<template>
  <div class="analysis-view" v-loading="loading">
    <!-- 文件信息头部 -->
    <section class="card" v-if="fileStore.currentFile">
      <div class="card-header">
        <span class="title">
          <el-icon><Document /></el-icon>
          {{ fileStore.currentFile.original_name }}
        </span>
        <el-button size="small" @click="$router.push('/')" :icon="Back">
          返回列表
        </el-button>
      </div>

      <!-- 统计概览 -->
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6">
          <div class="stat-card">
            <div class="stat-value">{{ fileStore.currentFile.packet_count.toLocaleString() }}</div>
            <div class="stat-label">报文总数</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card">
            <div class="stat-value">{{ formatSize(fileStore.currentFile.file_size) }}</div>
            <div class="stat-label">文件大小</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card">
            <div class="stat-value">{{ analysisStore.protocolStats.length }}</div>
            <div class="stat-label">协议类型</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card">
            <div class="stat-value">{{ analysisStore.topTalkers.length }}</div>
            <div class="stat-label">通信节点</div>
          </div>
        </el-col>
      </el-row>
    </section>

    <!-- 分析面板 -->
    <el-row :gutter="20">
      <!-- 协议分布 -->
      <el-col :xs="24" :sm="24" :md="12">
        <section class="card">
          <div class="card-header">
            <span class="title">
              <el-icon><PieChart /></el-icon>
              协议分布
            </span>
          </div>
          <ProtocolChart :data="analysisStore.protocolStats" />
        </section>
      </el-col>

      <!-- 诊断建议 -->
      <el-col :xs="24" :sm="24" :md="12">
        <section class="card">
          <div class="card-header">
            <span class="title">
              <el-icon><Warning /></el-icon>
              智能诊断
            </span>
          </div>
          <DiagnosisList :items="analysisStore.diagnosis" />
        </section>
      </el-col>
    </el-row>

    <!-- 流量时间线 -->
    <section class="card">
      <div class="card-header">
        <span class="title">
          <el-icon><TrendCharts /></el-icon>
          流量时间线
        </span>
      </div>
      <TrafficChart :data="analysisStore.trafficTimeline" />
    </section>

    <!-- 报文列表 -->
    <section class="card">
      <div class="card-header">
        <span class="title">
          <el-icon><List /></el-icon>
          报文列表
        </span>
      </div>
      <PacketTable :file-id="fileId" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Document, Back, PieChart, Warning, TrendCharts, List } from '@element-plus/icons-vue'
import { useFileStore } from '@/stores/file'
import { useAnalysisStore } from '@/stores/analysis'
import ProtocolChart from '@/components/ProtocolChart.vue'
import TrafficChart from '@/components/TrafficChart.vue'
import DiagnosisList from '@/components/DiagnosisList.vue'
import PacketTable from '@/components/PacketTable.vue'

const props = defineProps({
  id: { type: [String, Number], required: true }
})

const fileStore = useFileStore()
const analysisStore = useAnalysisStore()
const loading = ref(false)

const fileId = ref(Number(props.id))

onMounted(() => {
  loadData()
})

watch(() => props.id, (newId) => {
  fileId.value = Number(newId)
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    await Promise.all([
      fileStore.fetchFile(fileId.value),
      analysisStore.fetchAll(fileId.value)
    ])
  } finally {
    loading.value = false
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}
</script>

<style scoped>
@media (max-width: 768px) {
  .stat-card {
    margin-bottom: 12px;
  }
}
</style>
