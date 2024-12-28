<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const vms = ref([])
const error = ref('')
const loading = ref(false)

const fetchVMs = async () => {
  loading.value = true
  try {
    const response = await api.get('/vms')
    vms.value = response.data
  } catch (e: any) {
    console.error('Error fetching VMs:', e)
    error.value = e.response?.data?.detail || 'Failed to load VMs'
  } finally {
    loading.value = false
  }
}

onMounted(fetchVMs)
</script>

<template>
  <main>
    <TheWelcome />
  </main>
</template>
