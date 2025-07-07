<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Lightweight Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-900">ArXiv Research Papers</h1>
          <span class="text-sm text-gray-500">Public Dashboard</span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm text-gray-500">Total Papers</div>
          <div class="text-2xl font-bold text-gray-900">{{ stats.totalPapers }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm text-gray-500">This Week</div>
          <div class="text-2xl font-bold text-gray-900">{{ stats.recentPapers }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm text-gray-500">Avg Score</div>
          <div class="text-2xl font-bold text-gray-900">{{ formatScore(stats.averageScore) }}</div>
        </div>
      </div>

      <!-- Recent Papers List -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-900">Recent Papers</h2>
        </div>
        
        <div v-if="loading" class="p-6 text-center">
          <div class="inline-flex items-center">
            <svg class="animate-spin h-5 w-5 mr-3 text-gray-400" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading papers...
          </div>
        </div>

        <div v-else-if="papers.length === 0" class="p-6 text-center text-gray-500">
          No papers available
        </div>

        <div v-else class="divide-y divide-gray-200">
          <article v-for="paper in papers" :key="paper.arxiv_id" class="p-6 hover:bg-gray-50">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-base font-medium text-gray-900 mb-1">
                  {{ paper.title }}
                </h3>
                <p class="text-sm text-gray-600 mb-2">
                  {{ paper.authors.slice(0, 3).join(', ') }}
                  <span v-if="paper.authors.length > 3">et al.</span>
                </p>
                <p class="text-sm text-gray-500 line-clamp-2">
                  {{ paper.abstract }}
                </p>
                <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                  <span>{{ formatDate(paper.published_date) }}</span>
                  <span>•</span>
                  <span>Score: {{ formatScore(paper.relevance_score) }}</span>
                  <span>•</span>
                  <a 
                    :href="`https://arxiv.org/abs/${paper.arxiv_id}`"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-600 hover:underline"
                  >
                    View on ArXiv →
                  </a>
                </div>
              </div>
            </div>
          </article>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'PublicDashboard',
  setup() {
    const papers = ref([])
    const stats = ref({
      totalPapers: 0,
      recentPapers: 0,
      averageScore: 0
    })
    const loading = ref(true)

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const options = { month: 'short', day: 'numeric', year: 'numeric' }
      return date.toLocaleDateString('en-US', options)
    }

    const formatScore = (score) => {
      return score ? score.toFixed(2) : '0.00'
    }

    const fetchPublicData = async () => {
      try {
        // Fetch stats
        const statsResponse = await fetch('/api/public/stats')
        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          stats.value = {
            totalPapers: statsData.total_papers || 0,
            recentPapers: statsData.recent_papers || 0,
            averageScore: statsData.average_score || 0
          }
        }

        // Fetch recent papers
        const papersResponse = await fetch('/api/public/papers?limit=10')
        if (papersResponse.ok) {
          const papersData = await papersResponse.json()
          papers.value = papersData.papers || []
        }
      } catch (error) {
        console.error('Error fetching public data:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchPublicData()
    })

    return {
      papers,
      stats,
      loading,
      formatDate,
      formatScore
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
