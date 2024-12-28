<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { vmService } from '@/services/vmService'
import { ServerIcon } from '@heroicons/vue/24/solid'
import HeaderNav from '@/components/HeaderNav.vue'

const router = useRouter()
const vms = ref<any[]>([])
const vmStatuses = ref<{[key: string]: any}>({})
const loading = ref(true)
const error = ref('')

const fetchVMStatuses = async () => {
  try {
    for (const vmId of vms.value) {
      const status = await vmService.getVMStatus(vmId)
      vmStatuses.value[vmId] = status
    }
  } catch (e: any) {
    console.error('Error fetching VM statuses:', e)
  }
}

const fetchVMs = async () => {
  try {
    const response = await vmService.getVMList()
    vms.value = response
    loading.value = false
    await fetchVMStatuses()
  } catch (e: any) {
    error.value = e.message
    loading.value = false
  }
}

const selectVM = (vmid: string) => {
  router.push(`/dashboard/${vmid}`)
}

onMounted(() => {
  fetchVMs()
})
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <HeaderNav />
    <div class="p-6">
      <div class="max-w-4xl mx-auto">
        <h1 class="text-2xl font-bold text-white mb-6">Virtual Machines</h1>

        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin h-8 w-8 text-blue-400">⟳</div>
        </div>

        <div v-else-if="error" class="text-center py-12">
          <div class="text-red-400">{{ error }}</div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            v-for="vm in vms" 
            :key="vm"
            @click="selectVM(vm)"
            class="bg-gray-800 rounded-lg p-6 cursor-pointer hover:bg-gray-700 transition-colors duration-200"
          >
            <div class="flex items-center space-x-4">
              <ServerIcon class="h-8 w-8 text-blue-400" />
              <div>
                <h2 class="text-lg font-medium text-white">VM {{ vm }}</h2>
                <div class="flex items-center mt-2 space-x-2">
                  <div :class="[
                    'h-2 w-2 rounded-full',
                    vmStatuses[vm]?.status === 'running' ? 'bg-green-400' : 
                    vmStatuses[vm]?.status === 'stopped' ? 'bg-red-400' : 'bg-gray-400'
                  ]"></div>
                  <span class="text-sm text-gray-400">
                    {{ vmStatuses[vm]?.status || 'Loading...' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 