import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analysisApi } from '@/api'

export const useAnalysisStore = defineStore('analysis', () => {
  const protocolStats = ref([])
  const trafficTimeline = ref([])
  const topTalkers = ref([])
  const diagnosis = ref([])
  const loading = ref(false)
  let fetchAllVersion = 0

  async function fetchAll(fileId) {
    fetchAllVersion++
    const currentVersion = fetchAllVersion
    loading.value = true
    reset()

    try {
      const [stats, timeline, talkers, diag] = await Promise.all([
        analysisApi.getProtocolStats(fileId),
        analysisApi.getTrafficTimeline(fileId),
        analysisApi.getTopTalkers(fileId),
        analysisApi.getDiagnosis(fileId)
      ])

      if (currentVersion === fetchAllVersion) {
        protocolStats.value = stats
        trafficTimeline.value = timeline
        topTalkers.value = talkers
        diagnosis.value = diag
      }
    } catch (error) {
      if (currentVersion === fetchAllVersion) {
        reset()
      }
      throw error
    } finally {
      if (currentVersion === fetchAllVersion) {
        loading.value = false
      }
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
