<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

const handleSubmit = async (e: Event) => {
  e.preventDefault()
  error.value = ''
  isLoading.value = true
  
  try {
    const fullUsername = username.value.includes('@') ? username.value : `${username.value}@pve`
    
    const formData = new URLSearchParams()
    formData.append('username', fullUsername)
    formData.append('password', password.value)
    
    console.log('Sending login request...')
    
    const response = await api.post('/token', formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    console.log('Response received:', response.status)

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
      router.push('/')
    } else {
      throw new Error('Invalid response from server')
    }
    
  } catch (e: any) {
    console.error('Login error:', {
      message: e.message,
      response: e.response?.data,
      status: e.response?.status
    })
    
    if (e.response?.status === 401) {
      error.value = 'Invalid username or password'
    } else if (e.code === 'ECONNABORTED') {
      error.value = 'Connection timeout. Please try again.'
    } else if (e.response) {
      error.value = e.response.data.detail || 'Server error'
    } else if (e.request) {
      error.value = 'No response from server. Is it running?'
    } else {
      error.value = 'Login failed: ' + e.message
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
          Sign in to your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-400">
          Use your Proxmox credentials
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              :disabled="isLoading"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Username (e.g., username@pve)"
            >
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              :disabled="isLoading"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            >
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>
        
        <div v-if="error" class="text-red-500 text-center mt-2 p-2 bg-red-100 rounded">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template> 