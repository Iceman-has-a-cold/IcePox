<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  PlayIcon, 
  StopIcon, 
  PowerIcon, 
  ArrowPathIcon,
  ServerIcon,
  CpuChipIcon,
  ClockIcon,
  CircleStackIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/solid'
import { vmService } from '@/services/vmService'
import HeaderNav from '@/components/HeaderNav.vue'

const props = defineProps<{
  vmId: string
}>()

const vmStatus = ref<any>(null)
const error = ref('')
const loading = ref(true)
const actionInProgress = ref('')
let pollInterval: number | null = null
const successMessage = ref('')
const successProgress = ref(0)

// Format uptime
const formatUptime = (seconds: number): string => {
  if (!seconds) return '0 seconds'
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const parts = []
  if (days > 0) parts.push(`${days}d`)
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  return parts.join(' ') || '< 1m'
}

// Format bytes
const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

// Fetch VM status
const fetchVMStatus = async () => {
  try {
    const status = await vmService.getVMStatus(props.vmId)
    vmStatus.value = status
    loading.value = false
  } catch (e: any) {
    console.error('Error fetching VM status:', e)
    error.value = e.message
    loading.value = false
  }
}

// Start polling
const startPolling = () => {
  fetchVMStatus()
  pollInterval = window.setInterval(fetchVMStatus, 5000)
}

// Add this function
const showSuccess = async (action: string) => {
  successMessage.value = `${action.charAt(0).toUpperCase() + action.slice(1)} successful`
  successProgress.value = 0
  
  // Animate progress bar
  const duration = 2000 // 2 seconds
  const interval = 16 // 60fps
  const steps = duration / interval
  let currentStep = 0
  
  const progressInterval = setInterval(() => {
    currentStep++
    successProgress.value = (currentStep / steps) * 100
    
    if (currentStep >= steps) {
      clearInterval(progressInterval)
      setTimeout(() => {
        successMessage.value = ''
        successProgress.value = 0
      }, 500)
    }
  }, interval)
}

// Perform VM action
const performAction = async (action: 'start' | 'stop' | 'shutdown' | 'reset') => {
  if (actionInProgress.value) return
  
  actionInProgress.value = action
  error.value = ''
  
  try {
    switch (action) {
      case 'start':
        await vmService.startVM(props.vmId)
        break
      case 'stop':
        await vmService.stopVM(props.vmId)
        break
      case 'shutdown':
        await vmService.shutdownVM(props.vmId)
        break
      case 'reset':
        await vmService.resetVM(props.vmId)
        break
    }

    // Show success message
    await showSuccess(action)

    // Poll VM status until it's in the desired state
    let attempts = 0
    const maxAttempts = 30
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000))
      await fetchVMStatus()
      
      if (action === 'stop' && vmStatus.value?.status === 'stopped') break
      if (action === 'reset' && vmStatus.value?.status === 'running') break
      if (action === 'start' && vmStatus.value?.status === 'running') break
      if (action === 'shutdown' && vmStatus.value?.status === 'stopped') break
      
      attempts++
    }

  } catch (e: any) {
    error.value = e.response?.data?.detail || `Failed to ${action} VM`
  } finally {
    actionInProgress.value = ''
  }
}

onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <HeaderNav />
    
    <!-- Success Message Overlay -->
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div 
        v-if="successMessage"
        class="fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-50"
      >
        <div class="bg-gray-800 rounded-lg p-6 max-w-sm w-full mx-4 shadow-2xl transform">
          <div class="flex items-center justify-center mb-4">
            <div class="rounded-full bg-green-500 p-3">
              <CheckCircleIcon class="h-8 w-8 text-white" />
            </div>
          </div>
          <h3 class="text-lg font-medium text-center text-white mb-2">
            {{ successMessage }}
          </h3>
          <div class="mt-4 bg-gray-700 rounded-full h-2">
            <div 
              class="bg-green-500 h-2 rounded-full transition-all duration-200"
              :style="{ width: `${successProgress}%` }"
            ></div>
          </div>
        </div>
      </div>
    </Transition>

    <div class="p-6">
      <div class="max-w-4xl mx-auto">
        <!-- VM Status Card -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6">
          <div class="flex items-center space-x-4 mb-6">
            <ServerIcon class="h-8 w-8 text-blue-400" />
            <h2 class="text-2xl font-bold text-white">Virtual Machine Status</h2>
          </div>

          <div v-if="loading" class="flex justify-center py-12">
            <ArrowPathIcon class="animate-spin h-8 w-8 text-blue-400" />
          </div>

          <div v-else-if="error" class="text-center py-12">
            <div class="text-red-400">{{ error }}</div>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Status -->
            <div class="bg-gray-700 rounded-lg p-4">
              <div class="flex items-center space-x-2">
                <div :class="[
                  'h-3 w-3 rounded-full',
                  vmStatus?.status === 'running' ? 'bg-green-400' : 'bg-red-400'
                ]"></div>
                <span class="text-gray-300">Status: {{ vmStatus?.status }}</span>
              </div>
            </div>

            <!-- CPU Usage -->
            <div class="bg-gray-700 rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <CpuChipIcon class="h-5 w-5 text-blue-400" />
                  <span class="text-gray-300">CPU Usage</span>
                </div>
                <span class="text-gray-400">{{ vmStatus?.cpu?.toFixed(1) }}%</span>
              </div>
              <div class="h-2 bg-gray-600 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-blue-400 transition-all duration-500"
                  :style="{ width: `${Math.min(vmStatus?.cpu || 0, 100)}%` }"
                ></div>
              </div>
            </div>

            <!-- Memory Usage -->
            <div class="bg-gray-700 rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <CircleStackIcon class="h-5 w-5 text-blue-400" />
                  <span class="text-gray-300">Memory Usage</span>
                </div>
                <span class="text-gray-400">
                  {{ ((vmStatus?.memory?.used || 0) / (1024 * 1024 * 1024)).toFixed(1) }}GB / 
                  {{ ((vmStatus?.memory?.total || 0) / (1024 * 1024 * 1024)).toFixed(1) }}GB
                </span>
              </div>
              <div class="h-2 bg-gray-600 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-blue-400 transition-all duration-500"
                  :style="{ width: `${(vmStatus?.memory?.used / vmStatus?.memory?.total * 100) || 0}%` }"
                ></div>
              </div>
            </div>

            <!-- Disk Size -->
            <div class="bg-gray-700 rounded-lg p-4">
              <div class="flex items-center space-x-2">
                <CircleStackIcon class="h-5 w-5 text-blue-400" />
                <span class="text-gray-300">
                  Disk Size: {{ ((vmStatus?.disk?.total || 0) / (1024 * 1024 * 1024)).toFixed(1) }}GB
                </span>
              </div>
            </div>

            <!-- Uptime -->
            <div class="bg-gray-700 rounded-lg p-4">
              <div class="flex items-center space-x-2">
                <ClockIcon class="h-5 w-5 text-blue-400" />
                <span class="text-gray-300">Uptime: {{ formatUptime(vmStatus?.uptime || 0) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Control Buttons -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6">
          <div class="flex space-x-4">
            <button
              @click="() => performAction('start')"
              :disabled="actionInProgress !== ''"
              :class="[
                'flex items-center px-4 py-2 rounded-md text-white transition-all duration-200',
                actionInProgress === 'start' 
                  ? 'bg-green-600 animate-pulse'
                  : 'bg-green-500 hover:bg-green-600',
                actionInProgress && actionInProgress !== 'start' ? 'opacity-50 cursor-not-allowed' : ''
              ]"
            >
              <PlayIcon class="h-5 w-5 mr-2" />
              <span v-if="actionInProgress === 'start'" class="inline-block animate-spin mr-2">⟳</span>
              Start
            </button>

            <button
              @click="() => performAction('stop')"
              :disabled="actionInProgress !== ''"
              :class="[
                'flex items-center px-4 py-2 rounded-md text-white transition-all duration-200',
                actionInProgress === 'stop' 
                  ? 'bg-red-600 animate-pulse'
                  : 'bg-red-500 hover:bg-red-600',
                actionInProgress && actionInProgress !== 'stop' ? 'opacity-50 cursor-not-allowed' : ''
              ]"
            >
              <StopIcon class="h-5 w-5 mr-2" />
              <span v-if="actionInProgress === 'stop'" class="inline-block animate-spin mr-2">⟳</span>
              Stop
            </button>

            <button
              @click="() => performAction('shutdown')"
              :disabled="actionInProgress !== ''"
              :class="[
                'flex items-center px-4 py-2 rounded-md text-white transition-all duration-200',
                actionInProgress === 'shutdown' 
                  ? 'bg-yellow-600 animate-pulse'
                  : 'bg-yellow-500 hover:bg-yellow-600',
                actionInProgress && actionInProgress !== 'shutdown' ? 'opacity-50 cursor-not-allowed' : ''
              ]"
            >
              <PowerIcon class="h-5 w-5 mr-2" />
              <span v-if="actionInProgress === 'shutdown'" class="inline-block animate-spin mr-2">⟳</span>
              Shutdown
            </button>

            <button
              @click="() => performAction('reset')"
              :disabled="actionInProgress !== ''"
              :class="[
                'flex items-center px-4 py-2 rounded-md text-white transition-all duration-200',
                actionInProgress === 'reset' 
                  ? 'bg-blue-600 animate-pulse'
                  : 'bg-blue-500 hover:bg-blue-600',
                actionInProgress && actionInProgress !== 'reset' ? 'opacity-50 cursor-not-allowed' : ''
              ]"
            >
              <ArrowPathIcon class="h-5 w-5 mr-2" />
              <span v-if="actionInProgress === 'reset'" class="inline-block animate-spin mr-2">⟳</span>
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  @apply p-4 bg-gray-50 rounded-lg;
}

.btn-primary {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50;
}

.btn-warning {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50;
}

.btn-danger {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}

.h-64 {
  height: 16rem;
}
</style> 