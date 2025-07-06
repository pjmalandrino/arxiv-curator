<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        AI-Powered Research Paper Discovery
      </h1>
      <p class="text-xl text-gray-600 max-w-3xl mx-auto">
        Automatically curate and summarize the latest research papers from ArXiv 
        using advanced AI models. Stay up-to-date with cutting-edge research in 
        AI, Machine Learning, and Computer Science.
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <StatsCard
        title="Total Papers"
        :value="stats.totalPapers"
        icon="document-text"
        color="blue"
      />
      <StatsCard
        title="Recent Papers"
        :value="stats.recentPapers"
        icon="clock"
        color="green"
      />
      <StatsCard
        title="Average Score"
        :value="stats.averageScore.toFixed(2)"
        icon="chart-bar"
        color="purple"
      />
    </div>

    <!-- Recent High-Scoring Papers -->
    <div class="mb-12">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900">
          Recent High-Scoring Papers
        </h2>
        <router-link
          to="/papers"
          class="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          View all papers →
        </router-link>
      </div>
      
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
      </div>
      
      <div v-else-if="error" class="text-center py-8">
        <p class="text-red-600">{{ error }}</p>
      </div>
      
      <div v-else-if="highScoringPapers.length === 0" class="text-center py-8">
        <p class="text-gray-500">No papers found</p>
      </div>
      
      <div v-else class="grid gap-6">
        <PaperCard
          v-for="paper in highScoringPapers.slice(0, 5)"
          :key="paper.arxiv_id"
          :paper="paper"
        />
      </div>
    </div>

    <!-- Call to Action -->
    <div class="bg-indigo-50 rounded-lg p-8 text-center">
      <h3 class="text-2xl font-bold text-gray-900 mb-4">
        Start Exploring Research
      </h3>
      <p class="text-gray-600 mb-6">
        Browse through our curated collection of research papers with AI-generated summaries
      </p>
      <router-link
        to="/papers"
        class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
      >
        Browse Papers
      </router-link>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { usePapersStore } from '@/stores/papers'
import StatsCard from '@/components/StatsCard.vue'
import PaperCard from '@/components/PaperCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

export default {
  name: 'HomePage',
  components: {
    StatsCard,
    PaperCard,
    LoadingSpinner
  },
  setup() {
    const papersStore = usePapersStore()

    onMounted(() => {
      papersStore.fetchPapers()
      papersStore.fetchStats()
    })

    return {
      stats: computed(() => papersStore.stats),
      highScoringPapers: computed(() => papersStore.highScoringPapers),
      loading: computed(() => papersStore.loading),
      error: computed(() => papersStore.error)
    }
  }
}
</script>
