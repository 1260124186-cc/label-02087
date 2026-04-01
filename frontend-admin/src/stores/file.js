import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fileApi } from '@/api'

export const useFileStore = defineStore('file', () => {
  const files = ref([])
  const currentFile = ref(null)
  const loading = ref(false)

  async function fetchFiles() {
    loading.value = true
    try {
      files.value = await fileApi.getList()
    } finally {
      loading.value = false
    }
  }

  async function fetchFile(id, options = {}) {
    loading.value = true
    try {
      currentFile.value = await fileApi.getDetail(id, options)
    } catch (error) {
      currentFile.value = null
      throw error
    } finally {
      loading.value = false
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
