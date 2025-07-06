<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        Research Papers
      </h1>
      <p class="text-gray-600">
        Browse through our collection of curated research papers with AI-generated summaries.
      </p>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Days to look back
          </label>
          <select 
            v-model="filters.days"
            @change="applyFilters"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option :value="1">Last 24 hours</option>
            <option :value="3">Last 3 days</option>
            <option :value="7">Last week</option>
            <option :value="14">Last 2 weeks</option>
            <option :value="30">Last month</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Minimum relevance score
          </label>
          <select 
            v-model="filters.minScore"
            @change="applyFilters"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option :value="0">All papers</option>
            <option :value="0.4">40%+</option>
            <option :value="0.6">60%+</option>
            <option :value="0.8">80%+</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Sort by
          </label>
          <select 
            v-model="sortBy"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="date">Publication date</option>
            <option value="score">Relevance score</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Papers List -->
    <div v-if="loading" class="text-center py-12">
      <LoadingSpinner />
    </div>
    
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-600 mb-4">{{ error }}</p>
      <button 
        @click="retry"
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
      >
        Retry
      </button>
    </div>
    
    <div v-else-if="sortedPapers.length === 0" class="text-center py-12">
      <p class="text-gray-500">No papers found matching your criteria</p>
    </div>
    
    <div v-else>
      <div class="mb-4 text-sm text-gray-600">
        Showing {{ sortedPapers.length }} papers
      </div>
      <div class="grid gap-6">
        <PaperCard
          v-for="paper in paginatedPapers"
          :key="paper.arxiv_id"
          :paper="paper"
        />
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex space-x-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-md',
              page === currentPage
                ? 'bg-indigo-600 text-white'
                : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
          
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { usePapersStore } from '@/stores/papers'
import PaperCard from '@/components/PaperCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

export default {
  name: 'PapersView',
  components: {
    PaperCard,
    LoadingSpinner
  },
  setup() {
    const papersStore = usePapersStore()
    const currentPage = ref(1)
    const itemsPerPage = 10
    const sortBy = ref('date')
    
    const filters = ref({
      days: 7,
      minScore: 0.4
    })

    const sortedPapers = computed(() => {
      const papers = [...papersStore.papers]
      if (sortBy.value === 'date') {
        return papers.sort((a, b) => 
          new Date(b.published_date) - new Date(a.published_date)
        )
      } else {
        return papers.sort((a, b) => b.relevance_score - a.relevance_score)
      }
    })

    const totalPages = computed(() => 
      Math.ceil(sortedPapers.value.length / itemsPerPage)
    )

    const paginatedPapers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      return sortedPapers.value.slice(start, start + itemsPerPage)
    })

    const visiblePages = computed(() => {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, currentPage.value - 2)
      let end = Math.min(totalPages.value, start + maxVisible - 1)
      
      if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const applyFilters = () => {
      currentPage.value = 1
      papersStore.updateFilters(filters.value)
    }

    const retry = () => {
      papersStore.fetchPapers()
    }

    onMounted(() => {
      papersStore.fetchPapers()
    })

    return {
      loading: computed(() => papersStore.loading),
      error: computed(() => papersStore.error),
      sortedPapers,
      paginatedPapers,
      currentPage,
      totalPages,
      visiblePages,
      filters,
      sortBy,
      applyFilters,
      retry
    }
  }
}
</script>
