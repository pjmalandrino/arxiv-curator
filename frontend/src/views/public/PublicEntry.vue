<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        ArXiv Research Papers
      </h1>
      <p class="text-gray-600 mb-8">
        Public Access Dashboard
      </p>
      <div class="space-y-4">
        <router-link
          to="/public"
          class="block w-64 mx-auto px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Desktop Dashboard
        </router-link>
        <router-link
          to="/mobile"
          class="block w-64 mx-auto px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
        >
          Mobile Dashboard
        </router-link>
        <router-link
          to="/"
          class="block w-64 mx-auto px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
        >
          Full Application (Login Required)
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'PublicEntry',
  setup() {
    const router = useRouter()

    onMounted(() => {
      // Auto-redirect based on device
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
      const hasRedirectParam = new URLSearchParams(window.location.search).has('noredirect')
      
      if (!hasRedirectParam) {
        if (isMobile) {
          router.push('/mobile')
        } else {
          router.push('/public')
        }
      }
    })

    return {}
  }
}
</script>
