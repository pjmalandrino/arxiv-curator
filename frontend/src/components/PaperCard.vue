<template>
  <div class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
    <div class="flex justify-between items-start mb-4">
      <h3 class="text-lg font-semibold text-gray-900 flex-1 pr-4">
        <router-link 
          :to="`/paper/${paper.arxiv_id}`"
          class="hover:text-indigo-600 transition-colors"
        >
          {{ paper.title }}
        </router-link>
      </h3>
      <ScoreBadge :score="paper.relevance_score" />
    </div>
    
    <div class="text-sm text-gray-600 mb-3">
      <p class="mb-1">
        <span class="font-medium">Authors:</span> 
        {{ paper.authors.slice(0, 3).join(', ') }}
        <span v-if="paper.authors.length > 3">
          et al.
        </span>
      </p>
      <p>
        <span class="font-medium">Published:</span> 
        {{ formatDate(paper.published_date) }}
      </p>
    </div>
    
    <p class="text-gray-700 mb-4 line-clamp-3">
      {{ paper.abstract }}
    </p>
    
    <div class="flex flex-wrap gap-2 mb-4">
      <span 
        v-for="category in paper.categories.slice(0, 3)" 
        :key="category"
        class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
      >
        {{ category }}
      </span>
    </div>
    
    <div class="flex justify-between items-center">
      <router-link
        :to="`/paper/${paper.arxiv_id}`"
        class="text-indigo-600 hover:text-indigo-700 font-medium text-sm"
      >
        Read summary →
      </router-link>
      <a 
        :href="paper.pdf_url" 
        target="_blank"
        rel="noopener noreferrer"
        class="text-gray-500 hover:text-gray-700 text-sm"
      >
        View PDF ↗
      </a>
    </div>
  </div>
</template>

<script>
import { format } from 'date-fns'
import ScoreBadge from './ScoreBadge.vue'

export default {
  name: 'PaperCard',
  components: {
    ScoreBadge
  },
  props: {
    paper: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatDate(date) {
      return format(new Date(date), 'MMM d, yyyy')
    }
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
