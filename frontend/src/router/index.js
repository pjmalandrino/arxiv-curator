import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import PapersView from '@/views/PapersView.vue'
import PaperDetail from '@/views/PaperDetail.vue'
import AboutView from '@/views/AboutView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage
  },
  {
    path: '/papers',
    name: 'papers',
    component: PapersView
  },
  {
    path: '/paper/:arxivId',
    name: 'paper-detail',
    component: PaperDetail
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
