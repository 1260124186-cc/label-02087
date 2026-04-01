<template>
  <div class="packet-detail">
    <!-- 基本信息 -->
    <section class="detail-section">
      <h4 class="section-title">基本信息</h4>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="序号">{{ packet.packet_no }}</el-descriptions-item>
        <el-descriptions-item label="协议">
          <el-tag :class="['protocol-tag', packet.protocol]" size="small">
            {{ packet.protocol }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="源IP">
          <span class="mono-text">{{ packet.src_ip || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="目的IP">
          <span class="mono-text">{{ packet.dst_ip || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="源端口">
          <span class="mono-text">{{ packet.src_port || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="目的端口">
          <span class="mono-text">{{ packet.dst_port || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="长度">{{ packet.length }} bytes</el-descriptions-item>
        <el-descriptions-item label="时间戳">
          <span class="mono-text">{{ formatTimestamp(packet.timestamp) }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </section>

    <!-- 协议层级 -->
    <section class="detail-section" v-if="packet.layers && Object.keys(packet.layers).length">
      <h4 class="section-title">协议层级</h4>
      <div class="layer-panel">
        <el-collapse v-model="activeLayers">
          <el-collapse-item
            v-for="(fields, layerName) in packet.layers"
            :key="layerName"
            :title="layerName"
            :name="layerName"
          >
            <div class="layer-content">
              <div
                v-for="(value, key) in fields"
                :key="key"
                class="field-row"
              >
                <span class="field-name">{{ key }}</span>
                <span class="field-value">{{ formatValue(value) }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </section>

    <!-- Hex 视图 -->
    <section class="detail-section" v-if="packet.raw_hex">
      <h4 class="section-title">
        <span>原始数据</span>
        <el-button size="small" text type="primary" @click="copyHex">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
      </h4>
      <div class="hex-view">
        <div v-for="(line, index) in hexLines" :key="index" class="hex-line">
          <span class="hex-offset">{{ line.offset }}</span>
          <span class="hex-bytes">
            <span v-for="(byte, i) in line.bytes" :key="i">{{ byte }}</span>
          </span>
          <span class="hex-ascii">{{ line.ascii }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument } from '@element-plus/icons-vue'

const props = defineProps({
  packet: { type: Object, required: true }
})

const activeLayers = ref([])

// 监听 packet 变化，自动展开所有层级
watch(() => props.packet, (newPacket) => {
  if (newPacket?.layers) {
    activeLayers.value = Object.keys(newPacket.layers)
  }
}, { immediate: true })

const hexLines = computed(() => {
  if (!props.packet.raw_hex) return []

  const hex = props.packet.raw_hex
  const lines = []
  const bytesPerLine = 16

  for (let i = 0; i < hex.length; i += bytesPerLine * 2) {
    const lineHex = hex.slice(i, i + bytesPerLine * 2)
    const bytes = []
    let ascii = ''

    for (let j = 0; j < lineHex.length; j += 2) {
      const byte = lineHex.slice(j, j + 2)
      bytes.push(byte)

      const charCode = parseInt(byte, 16)
      ascii += (charCode >= 32 && charCode <= 126) ? String.fromCharCode(charCode) : '.'
    }

    lines.push({
      offset: (i / 2).toString(16).padStart(8, '0'),
      bytes,
      ascii
    })
  }

  return lines
})

function formatTimestamp(ts) {
  if (!ts) return '-'
  return new Date(ts * 1000).toISOString().replace('T', ' ').slice(0, 23)
}

function formatValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

function copyHex() {
  navigator.clipboard.writeText(props.packet.raw_hex)
    .then(() => {
      ElMessage.success('已复制到剪贴板')
    })
    .catch(() => {
      ElMessage.error('复制失败')
    })
}
</script>

<style scoped>
.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.mono-text {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}
</style>
