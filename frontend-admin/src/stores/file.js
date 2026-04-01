import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fileApi } from '@/api'

export const useFileStore = defineStore('file', () => {
  const files = ref([])
  const currentFile = ref(null)
  const loading = ref(false)
  let fetchFileVersion = 0

  async function fetchFiles() {
    loading.value = true
    try {
      files.value = await fileApi.getList()
    } finally {
      loading.value = false
    }
  }

  async function fetchFile(id) {
    fetchFileVersion++
    const currentVersion = fetchFileVersion
    loading.value = true
    currentFile.value = null

    try {
      const result = await fileApi.getDetail(id)
      if (currentVersion === fetchFileVersion) {
        currentFile.value = result
        return result
      }
      return null
    } finally {
      if (currentVersion === fetchFileVersion) {
        loading.value = false
      }
    }
  }

  async function uploadFile(file, onProgress) {
    const result = await fileApi.upload(file, onProgress)
    await fetchFiles()
    return result
  }

  async function deleteFile(id) {
    await fileApi.delete(id)
    await fetchFiles()
    if (currentFile.value?.id === id) {
      currentFile.value = null
    }
  }

  return {
    files,
    currentFile,
    loading,
    fetchFiles,
    fetchFile,
    uploadFile,
    deleteFile
  }
})
