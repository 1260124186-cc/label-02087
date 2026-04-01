import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analysisApi } from '@/api'

export const useAnalysisStore = defineStore('analysis', () => {
  const protocolStats = ref([])
  const trafficTimeline = ref([])
  const topTalkers = ref([])
  const diagnosis = ref([])
  const loading = ref(false)

  async function fetchAll(fileId, options = {}) {
    loading.value = true
    try {
      const [stats, timeline, talkers, diag] = await Promise.all([
        analysisApi.getProtocolStats(fileId, options),
        analysisApi.getTrafficTimeline(fileId, 1, options),
        analysisApi.getTopTalkers(fileId, 10, options),
        analysisApi.getDiagnosis(fileId, options)
      ])
      protocolStats.value = stats
      trafficTimeline.value = timeline
      topTalkers.value = talkers
      diagnosis.value = diag
    } catch (error) {
      reset()
      throw error
    } finally {
      loading.value = false
    }
  }

  function reset() {
    protocolStats.value = []
    trafficTimeline.value = []
    topTalkers.value = []
    diagnosis.value = []
  }

  return {
    protocolStats,
    trafficTimeline,
    topTalkers,
    diagnosis,
    loading,
    fetchAll,
    reset
  }
})
