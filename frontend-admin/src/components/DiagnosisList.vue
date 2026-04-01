<template>
  <div class="diagnosis-list">
    <div
      v-for="(item, index) in items"
      :key="index"
      :class="['diagnosis-item', item.level]"
    >
      <el-icon class="diagnosis-icon">
        <WarningFilled v-if="item.level === 'warning'" />
        <CircleCloseFilled v-else-if="item.level === 'error'" />
        <InfoFilled v-else />
      </el-icon>
      <div class="diagnosis-content">
        <div class="diagnosis-title">{{ item.title }}</div>
        <div class="diagnosis-desc">{{ item.description }}</div>
        <div v-if="item.suggestion" class="diagnosis-suggestion">
          <el-icon><Promotion /></el-icon>
          {{ item.suggestion }}
        </div>
      </div>
    </div>

    <div v-if="!items.length" class="empty-state">
      <el-icon><Warning /></el-icon>
      <p>暂无诊断信息</p>
    </div>
  </div>
</template>

<script setup>
import { WarningFilled, CircleCloseFilled, InfoFilled, Warning, Promotion } from '@element-plus/icons-vue'

defineProps({
  items: { type: Array, default: () => [] }
})
</script>

<style scoped>
.diagnosis-list {
  max-height: 320px;
  overflow-y: auto;
  padding-right: 4px;
}

/* 自定义滚动条 */
.diagnosis-list::-webkit-scrollbar {
  width: 6px;
}

.diagnosis-list::-webkit-scrollbar-track {
  background: #F1F5F9;
  border-radius: 3px;
}

.diagnosis-list::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 3px;
}

.diagnosis-list::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}

.diagnosis-suggestion {
  display: flex;
  align-items: flex-start;
  gap: 4px;
}

.diagnosis-suggestion .el-icon {
  font-size: 12px;
  margin-top: 2px;
  flex-shrink: 0;
}
</style>
