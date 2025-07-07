// Public API service for non-authenticated users
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const publicApi = {
  // Fetch public statistics
  async getStats() {
    const response = await fetch(`${API_BASE_URL}/public/stats`)
    if (!response.ok) {
      throw new Error('Failed to fetch stats')
    }
    return response.json()
  },

  // Fetch public papers (limited)
  async getPapers(params = {}) {
    const queryParams = new URLSearchParams({
      limit: params.limit || 10,
      offset: params.offset || 0,
      min_score: params.minScore || 0.5
    })

    const response = await fetch(`${API_BASE_URL}/public/papers?${queryParams}`)
    if (!response.ok) {
      throw new Error('Failed to fetch papers')
    }
    return response.json()
  },

  // Get paper details by ArXiv ID
  async getPaper(arxivId) {
    const response = await fetch(`${API_BASE_URL}/public/papers/${arxivId}`)
    if (!response.ok) {
      throw new Error('Paper not found')
    }
    return response.json()
  }
}

export default publicApi
