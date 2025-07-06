<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="loading" class="text-center py-12">
      <LoadingSpinner />
    </div>
    
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-600 mb-4">{{ error }}</p>
      <router-link 
        to="/papers"
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
      >
        Back to papers
      </router-link>
    </div>
    
    <div v-else-if="paper">
      <!-- Back button -->
      <router-link 
        to="/papers"
        class="inline-flex items-center text-indigo-600 hover:text-indigo-700 mb-6"
      >
        ← Back to papers
      </router-link>
      
      <!-- Paper Header -->
      <div class="bg-white rounded-lg shadow p-8 mb-8">
        <div class="flex justify-between items-start mb-4">
          <h1 class="text-2xl font-bold text-gray-900 flex-1 pr-4">
            {{ paper.title }}
          </h1>
          <ScoreBadge :score="paper.relevance_score" />
        </div>
        
        <div class="text-gray-600 mb-6">
          <p class="mb-2">
            <span class="font-medium">Authors:</span> 
            {{ paper.authors.join(', ') }}
          </p>
          <p class="mb-2">
            <span class="font-medium">Published:</span> 
            {{ formatDate(paper.published_date) }}
          </p>
          <p>
            <span class="font-medium">ArXiv ID:</span> 
            {{ paper.arxiv_id }}
          </p>
        </div>
        
        <div class="flex flex-wrap gap-2 mb-6">
          <span 
            v-for="category in paper.categories" 
            :key="category"
            class="px-3 py-1 text-sm font-medium bg-gray-100 text-gray-700 rounded-full"
          >
            {{ category }}
          </span>
        </div>
        
        <div class="flex gap-4">
          <a 
            :href="paper.pdf_url" 
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            View PDF ↗
          </a>
          <a 
            :href="`https://arxiv.org/abs/${paper.arxiv_id}`" 
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            View on ArXiv ↗
          </a>
        </div>
      </div>
      
      <!-- Abstract -->
      <div class="bg-white rounded-lg shadow p-8 mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Abstract</h2>
        <p class="text-gray-700 leading-relaxed">
          {{ paper.abstract }}
        </p>
      </div>
      
      <!-- AI Summary -->
      <div v-if="paper.summary" class="bg-white rounded-lg shadow p-8 mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4">
          AI-Generated Summary
        </h2>
        <div class="prose max-w-none">
          <p class="text-gray-700 leading-relaxed mb-6">
            {{ paper.summary.summary }}
          </p>
          
          <div v-if="paper.summary.key_points && paper.summary.key_points.length > 0">
            <h3 class="text-lg font-semibold text-gray-900 mb-3">
              Key Points
            </h3>
            <ul class="list-disc list-inside space-y-2">
              <li 
                v-for="(point, index) in paper.summary.key_points" 
                :key="index"
                class="text-gray-700"
              >
                {{ point }}
              </li>
            </ul>
          </div>
          
          <div class="mt-6 pt-6 border-t border-gray-200">
            <p class="text-sm text-gray-500">
              <span class="font-medium">Model used:</span> 
              {{ paper.summary.model_used }}
            </p>
            <p class="text-sm text-gray-500">
              <span class="font-medium">Generated on:</span> 
              {{ formatDate(paper.summary.created_at) }}
            </p>
          </div>
        </div>
      </div>
      
      <!-- No Summary -->
      <div v-else class="bg-yellow-50 rounded-lg p-8 mb-8">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">
              No AI summary available
            </h3>
            <p class="mt-2 text-sm text-yellow-700">
              This paper hasn't been summarized yet. Check back later for an AI-generated summary.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePapersStore } from '@/stores/papers'
import { format } from 'date-fns'
import ScoreBadge from '@/components/ScoreBadge.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

export default {
  name: 'PaperDetail',
  components: {
    ScoreBadge,
    LoadingSpinner
  },
  setup() {
    const route = useRoute()
    const papersStore = usePapersStore()
    
    onMounted(async () => {
      const arxivId = route.params.arxivId
      await papersStore.fetchPaperById(arxivId)
    })
    
    return {
      paper: computed(() => papersStore.currentPaper),
      loading: computed(() => papersStore.loading),
      error: computed(() => papersStore.error),
      formatDate: (date) => format(new Date(date), 'MMMM d, yyyy')
    }
  }
}
</script>
