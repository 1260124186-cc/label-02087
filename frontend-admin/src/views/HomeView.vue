<template>
  <div class="home-view">
    <!-- 上传区域 -->
    <section class="card">
      <div class="card-header">
        <span class="title">
          <el-icon><Upload /></el-icon>
          上传抓包文件
        </span>
      </div>
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :show-file-list="false"
        accept=".pcap,.pcapng,.cap"
        @change="handleFileChange"
      >
        <el-icon><UploadFilled /></el-icon>
        <div class="upload-text">
          拖拽文件到此处，或 <em>点击上传</em>
        </div>
        <div class="upload-tip">支持 .pcap / .pcapng / .cap 格式，最大 100MB</div>
      </el-upload>

      <!-- 上传进度 -->
      <div v-if="uploading" class="upload-progress">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadProgress === 100 ? 'success' : ''"
          :stroke-width="8"
        />
        <p class="progress-text">
          {{ uploadProgress === 100 ? '正在解析报文...' : '上传中...' }}
        </p>
      </div>
    </section>

    <!-- 文件列表 -->
    <section class="card">
      <div class="card-header">
        <span class="title">
          <el-icon><Document /></el-icon>
          已上传文件
        </span>
        <el-button
          size="small"
          @click="fetchFiles"
          :loading="fileStore.loading"
          :icon="Refresh"
        >
          刷新
        </el-button>
      </div>

      <el-table
        :data="fileStore.files"
        v-loading="fileStore.loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon><Document /></el-icon>
              <span>{{ row.original_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="packet_count" label="报文数" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :disabled="row.status !== 'completed'"
              @click="goAnalysis(row.id)"
            >
              分析
            </el-button>
            <el-popconfirm
              title="确定删除此文件？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" size="small" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="fileStore.files.length === 0 && !fileStore.loading" class="empty-state">
        <el-icon><FolderOpened /></el-icon>
        <p>暂无文件，请上传抓包文件开始分析</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, UploadFilled, Document, Refresh, FolderOpened } from '@element-plus/icons-vue'
import { useFileStore } from '@/stores/file'

const router = useRouter()
const fileStore = useFileStore()

const uploading = ref(false)
const uploadProgress = ref(0)

// 使用 shallowRef 避免图标组件被深度响应
const RefreshIcon = shallowRef(Refresh)

onMounted(() => {
  fetchFiles()
})

async function fetchFiles() {
  await fileStore.fetchFiles()
}

async function handleFileChange(uploadFile) {
  const file = uploadFile.raw
  if (!file) return

  uploading.value = true
  uploadProgress.value = 0

  try {
    await fileStore.uploadFile(file, (e) => {
      uploadProgress.value = Math.round((e.loaded / e.total) * 100)
    })
    ElMessage.success('文件上传并解析成功')
  } catch (error) {
    console.error(error)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

async function handleDelete(id) {
  try {
    await fileStore.deleteFile(id)
    ElMessage.success('删除成功')
  } catch (error) {
    console.error(error)
  }
}

function goAnalysis(id) {
  router.push(`/analysis/${id}`)
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

function formatTime(time) {
  return new Date(time).toLocaleString('zh-CN')
}

function getStatusType(status) {
  const map = { completed: 'success', parsing: 'warning', failed: 'danger', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { completed: '完成', parsing: '解析中', failed: '失败', pending: '等待' }
  return map[status] || status
}
</script>

<style scoped>
.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name .el-icon {
  color: #2563EB;
  font-size: 16px;
}

.upload-progress {
  margin-top: 20px;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 8px;
}

.progress-text {
  text-align: center;
  margin-top: 12px;
  color: #64748B;
  font-size: 13px;
}
</style>
