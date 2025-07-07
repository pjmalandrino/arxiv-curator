<template>
  <div class="bookmarks-view">
    <h1>My Bookmarks</h1>
    
    <div v-if="loading" class="loading">
      Loading bookmarks...
    </div>
    
    <div v-else-if="bookmarks.length === 0" class="empty-state">
      <p>You haven't bookmarked any papers yet.</p>
      <router-link to="/papers" class="btn btn-primary">
        Browse Papers
      </router-link>
    </div>
    
    <div v-else class="bookmarks-grid">
      <div 
        v-for="bookmark in bookmarks" 
        :key="bookmark.arxivId"
        class="bookmark-card"
      >
        <h3>
          <router-link :to="`/paper/${bookmark.arxivId}`">
            {{ bookmark.title }}
          </router-link>
        </h3>
        <p class="authors">{{ bookmark.authors.join(', ') }}</p>
        <p class="abstract">{{ bookmark.abstract }}</p>
        <div class="card-actions">
          <button 
            @click="removeBookmark(bookmark.arxivId)"
            class="btn btn-danger btn-sm"
          >
            Remove
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/services/api'

const api = useApi()
const bookmarks = ref([])
const loading = ref(true)

onMounted(async () => {
  await fetchBookmarks()
})

async function fetchBookmarks() {
  try {
    const response = await api.get('/api/user/bookmarks')
    bookmarks.value = response.data.bookmarks
  } catch (error) {
    console.error('Failed to fetch bookmarks:', error)
  } finally {
    loading.value = false
  }
}

async function removeBookmark(arxivId) {
  try {
    await api.delete(`/api/user/bookmarks/${arxivId}`)
    bookmarks.value = bookmarks.value.filter(b => b.arxivId !== arxivId)
  } catch (error) {
    console.error('Failed to remove bookmark:', error)
  }
}
</script>

<style scoped>
.bookmarks-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 2rem;
  color: #333;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
}

.bookmarks-grid {
  display: grid;
  gap: 1.5rem;
}

.bookmark-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bookmark-card h3 {
  margin: 0 0 0.5rem 0;
}

.bookmark-card h3 a {
  color: #333;
  text-decoration: none;
}

.bookmark-card h3 a:hover {
  color: #007bff;
}

.authors {
  color: #666;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.abstract {
  color: #555;
  line-height: 1.6;
  margin: 1rem 0;
}

.card-actions {
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}
</style>
