<template>
  <div class="packet-table">
    <!-- 过滤器 -->
    <div class="filter-form">
      <el-form :inline="true">
        <el-form-item label="协议">
          <el-select v-model="filters.protocol" clearable placeholder="全部协议" style="width: 130px;">
            <el-option v-for="p in protocols" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="源IP">
          <el-input v-model="filters.src_ip" clearable placeholder="输入源IP" style="width: 150px;" />
        </el-form-item>
        <el-form-item label="目的IP">
          <el-input v-model="filters.dst_ip" clearable placeholder="输入目的IP" style="width: 150px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPackets" :icon="Search">
            查询
          </el-button>
          <el-button @click="resetFilters" :icon="RefreshLeft">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格 -->
    <el-table
      :data="packets"
      v-loading="loading"
      stripe
      highlight-current-row
      @row-click="handleRowClick"
      style="width: 100%"
    >
      <el-table-column prop="packet_no" label="序号" width="80" align="center" />
      <el-table-column prop="protocol" label="协议" width="100" align="center">
        <template #default="{ row }">
          <el-tag :class="['protocol-tag', row.protocol]" size="small">
            {{ row.protocol }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="src_ip" label="源IP" min-width="140">
        <template #default="{ row }">
          <span class="ip-text">{{ row.src_ip || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="src_port" label="源端口" width="90" align="center">
        <template #default="{ row }">
          <span class="port-text">{{ row.src_port || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="dst_ip" label="目的IP" min-width="140">
        <template #default="{ row }">
          <span class="ip-text">{{ row.dst_ip || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="dst_port" label="目的端口" width="90" align="center">
        <template #default="{ row }">
          <span class="port-text">{{ row.dst_port || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="length" label="长度" width="90" align="right">
        <template #default="{ row }">
          <span class="length-text">{{ row.length }} B</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-wrapper">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :current-page="page"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 报文详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="报文详情"
      size="520px"
      :destroy-on-close="true"
    >
      <PacketDetail v-if="selectedPacket" :packet="selectedPacket" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import { packetApi } from '@/api'
import PacketDetail from './PacketDetail.vue'

const props = defineProps({
  fileId: { type: Number, required: true }
})

const loading = ref(false)
const packets = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)

const filters = reactive({
  protocol: '',
  src_ip: '',
  dst_ip: ''
})

const protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS', 'ICMP', 'ARP', 'SSH']

const drawerVisible = ref(false)
const selectedPacket = ref(null)

onMounted(() => {
  fetchPackets()
})

watch(() => props.fileId, () => {
  page.value = 1
  fetchPackets()
})

async function fetchPackets() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      ...Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v)
      )
    }
    const result = await packetApi.getList(props.fileId, params)
    packets.value = result.items
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.protocol = ''
  filters.src_ip = ''
  filters.dst_ip = ''
  page.value = 1
  fetchPackets()
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchPackets()
}

function handleSizeChange(newSize) {
  pageSize.value = newSize
  page.value = 1
  fetchPackets()
}

async function handleRowClick(row) {
  try {
    selectedPacket.value = await packetApi.getDetail(props.fileId, row.packet_no)
    drawerVisible.value = true
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
.ip-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #1E293B;
}

.port-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #64748B;
}

.length-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #94A3B8;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
