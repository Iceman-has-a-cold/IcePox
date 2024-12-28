<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeftIcon } from '@heroicons/vue/24/solid'

const router = useRouter()
const route = useRoute()

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const goToOverview = () => {
  router.push('/')
}
</script>

<template>
  <header class="bg-gray-800 shadow-lg">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <button 
          v-if="route.name === 'dashboard'"
          @click="goToOverview"
          class="text-gray-300 hover:text-white flex items-center space-x-2"
        >
          <ArrowLeftIcon class="h-5 w-5" />
          <span>Back to Overview</span>
        </button>
        <h1 v-else class="text-white font-semibold">VM Overview</h1>
      </div>
      
      <button 
        @click="logout"
        class="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-md transition-colors duration-200"
      >
        Logout
      </button>
    </div>
  </header>
</template> 