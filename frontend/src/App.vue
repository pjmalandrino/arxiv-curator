<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation Header -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <span class="text-2xl font-bold text-indigo-600">ArXiv Curator</span>
            </router-link>
            
            <div class="hidden md:ml-10 md:flex md:space-x-8">
              <router-link 
                to="/" 
                class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-indigo-600"
                :class="{ 'border-b-2 border-indigo-500': $route.path === '/' }"
              >
                Dashboard
              </router-link>
              <router-link 
                to="/papers" 
                class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-indigo-600"
                :class="{ 'border-b-2 border-indigo-500': $route.path === '/papers' }"
              >
                Papers
              </router-link>
              <router-link 
                to="/about" 
                class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-indigo-600"
                :class="{ 'border-b-2 border-indigo-500': $route.path === '/about' }"
              >
                About
              </router-link>
            </div>
          </div>
          
          <!-- Auth Button -->
          <div class="flex items-center">
            <AuthButton />
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script>
import AuthButton from '@/components/AuthButton.vue'

export default {
  name: 'App',
  components: {
    AuthButton
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
