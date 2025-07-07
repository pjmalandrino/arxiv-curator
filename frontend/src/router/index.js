import { createRouter, createWebHistory } from 'vue-router'
import { authGuard, publicGuard } from './guards'
import HomePage from '@/views/HomePage.vue'
import PapersView from '@/views/PapersView.vue'
import PaperDetail from '@/views/PaperDetail.vue'
import AboutView from '@/views/AboutView.vue'
import PublicDashboard from '@/views/public/PublicDashboard.vue'
import MobileDashboard from '@/views/public/MobileDashboard.vue'
import PublicEntry from '@/views/public/PublicEntry.vue'
import UnauthorizedView from '@/views/UnauthorizedView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/papers',
    name: 'papers',
    component: PapersView,
    meta: { requiresAuth: true }
  },
  {
    path: '/paper/:arxivId',
    name: 'paper-detail',
    component: PaperDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/views/AdminDashboard.vue'),
    meta: { 
      requiresAuth: true,
      requiresRole: 'admin'
    }
  },
  {
    path: '/bookmarks',
    name: 'bookmarks',
    component: () => import('@/views/BookmarksView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/unauthorized',
    name: 'unauthorized',
    component: UnauthorizedView
  },
  {
    path: '/login',
    name: 'login',
    beforeEnter: (to, from, next) => {
      // Trigger Keycloak login
      const authStore = useAuthStore()
      authStore.login()
    }
  },
  {
    path: '/logout',
    name: 'logout',
    beforeEnter: (to, from, next) => {
      // Trigger Keycloak logout
      const authStore = useAuthStore()
      authStore.logout()
    }
  },
  // Catch all 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Apply authentication guard to all routes
router.beforeEach(authGuard)

// Import auth store
import { useAuthStore } from '@/stores/auth'

export default router
