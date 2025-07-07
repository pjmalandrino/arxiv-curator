<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Compact Header -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-semibold text-gray-900">ArXiv Papers</h1>
        <button 
          @click="refreshData" 
          :disabled="loading"
          class="p-2 rounded-md hover:bg-gray-100"
        >
          <svg 
            :class="{ 'animate-spin': loading }"
            class="w-5 h-5 text-gray-600" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Stats Bar -->
    <div class="bg-white border-b px-4 py-2">
      <div class="flex justify-around text-center">
        <div>
          <div class="text-xs text-gray-500">Papers</div>
          <div class="font-semibold text-gray-900">{{ stats.totalPapers }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-500">This Week</div>
          <div class="font-semibold text-gray-900">{{ stats.recentPapers }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-500">Avg Score</div>
          <div class="font-semibold text-gray-900">{{ formatScore(stats.averageScore) }}</div>
        </div>
      </div>
    </div>

    <!-- Papers List -->
    <main class="pb-4">
      <div v-if="loading && papers.length === 0" class="flex justify-center py-8">
        <div class="text-gray-500">Loading...</div>
      </div>

      <div v-else-if="papers.length === 0" class="text-center py-8 text-gray-500">
        No papers available
      </div>

      <div v-else class="space-y-2 px-4 pt-4">
        <article 
          v-for="paper in papers" 
          :key="paper.arxiv_id"
          class="bg-white rounded-lg shadow-sm p-4"
        >
          <h3 class="font-medium text-gray-900 text-sm mb-1 line-clamp-2">
            {{ paper.title }}
          </h3>
          <p class="text-xs text-gray-600 mb-2">
            {{ formatAuthors(paper.authors) }}
          </p>
          <p class="text-xs text-gray-500 line-clamp-3 mb-2">
            {{ paper.abstract }}
          </p>
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-3 text-gray-500">
              <span>{{ formatDate(paper.published_date) }}</span>
              <span class="inline-flex items-center">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {{ formatScore(paper.relevance_score) }}
              </span>
            </div>
            <a 
              :href="`https://arxiv.org/abs/${paper.arxiv_id}`"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-600 hover:underline"
            >
              View →
            </a>
          </div>
        </article>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading" class="px-4 pt-4">
        <button
          @click="loadMore"
          class="w-full py-2 bg-white rounded-lg shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Load More
        </button>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import publicApi from '@/services/publicApi'

export default {
  name: 'MobileDashboard',
  setup() {
    const papers = ref([])
    const stats = ref({
      totalPapers: 0,
      recentPapers: 0,
      averageScore: 0
    })
    const loading = ref(false)
    const offset = ref(0)
    const hasMore = ref(true)
    const limit = 10

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) return 'Today'
      if (diffDays === 1) return 'Yesterday'
      if (diffDays < 7) return `${diffDays} days ago`
      
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    const formatScore = (score) => {
      return score ? score.toFixed(2) : '0.00'
    }

    const formatAuthors = (authors) => {
      if (!authors || authors.length === 0) return 'Unknown'
      if (authors.length === 1) return authors[0]
      if (authors.length === 2) return authors.join(' & ')
      return `${authors[0]} et al.`
    }

    const fetchData = async (append = false) => {
      loading.value = true
      try {
        // Fetch stats only on initial load
        if (!append) {
          const statsData = await publicApi.getStats()
          stats.value = {
            totalPapers: statsData.total_papers || 0,
            recentPapers: statsData.recent_papers || 0,
            averageScore: statsData.average_score || 0
          }
        }

        // Fetch papers
        const papersData = await publicApi.getPapers({ 
          limit, 
          offset: offset.value,
          minScore: 0.4 
        })
        
        if (append) {
          papers.value.push(...(papersData.papers || []))
        } else {
          papers.value = papersData.papers || []
        }

        hasMore.value = papersData.papers && papersData.papers.length === limit
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        loading.value = false
      }
    }

    const loadMore = () => {
      offset.value += limit
      fetchData(true)
    }

    const refreshData = () => {
      offset.value = 0
      fetchData(false)
    }

    onMounted(() => {
      fetchData()
    })

    return {
      papers,
      stats,
      loading,
      hasMore,
      formatDate,
      formatScore,
      formatAuthors,
      loadMore,
      refreshData
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

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
