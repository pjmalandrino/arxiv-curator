import { defineStore } from 'pinia'
import api from '@/services/api'

export const usePapersStore = defineStore('papers', {
  state: () => ({
    papers: [],
    currentPaper: null,
    loading: false,
    error: null,
    filters: {
      days: 7,
      minScore: 0.4,
      categories: []
    },
    stats: {
      totalPapers: 0,
      recentPapers: 0,
      averageScore: 0
    }
  }),

  getters: {
    sortedPapers: (state) => {
      return [...state.papers].sort((a, b) => {
        return new Date(b.published_date) - new Date(a.published_date)
      })
    },
    
    highScoringPapers: (state) => {
      return state.papers.filter(paper => paper.relevance_score >= 0.7)
    }
  },

  actions: {
    async fetchPapers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.papers.list(this.filters)
        this.papers = response.data.papers || []
      } catch (error) {
        this.error = error.message
        console.error('Error fetching papers:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchPaperById(arxivId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.papers.get(arxivId)
        this.currentPaper = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error fetching paper:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        const response = await api.stats()
        this.stats = response.data
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    },

    updateFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.fetchPapers()
    },

    clearCurrentPaper() {
      this.currentPaper = null
    }
  }
})
