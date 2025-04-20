<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Sidebar Navigation -->
    <aside class="w-64 bg-gray-800 p-6">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold text-white">RAG From Scratch</h2>
      </div>

      <nav class="mt-8">
        <ul class="space-y-2">
          <li v-for="(item, index) in navItems" :key="index">
            <router-link
              :to="item.path"
              class="flex items-center rounded-lg px-3 py-2 text-gray-200 hover:bg-gray-700"
              :class="{ 'bg-gray-700': $route.path === item.path }"
            >
              <span class="ml-3">{{ item.name }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="flex-1">
      <!-- Page Header -->
      <header class="bg-white p-4 shadow">
        <h1 class="text-xl font-semibold">{{ currentPageTitle }}</h1>
      </header>

      <!-- Page Content -->
      <main class="p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useRagDataStore } from './stores/ragDataStore';

// Initialize the store with data from the backend
const ragStore = useRagDataStore();
onMounted(async () => {
  await ragStore.initialize();
});

// Navigation items
const navItems = [
  { name: 'File Loader', path: '/file-loader' },
  { name: 'Chunk Engine', path: '/chunk-engine' },
  { name: 'Embedding Engine', path: '/embedding-engine' },
  { name: 'Vector Indexer', path: '/vector-indexer' },
  { name: 'Search Console', path: '/search-console' },
  { name: 'Generator Hub', path: '/generator-hub' },
  { name: 'Pipeline Monitor', path: '/pipeline-monitor' },
];

// Current page title based on route
const route = useRoute();
const currentPageTitle = computed(() => {
  const currentNav = navItems.find(item => item.path === route.path);
  return currentNav ? currentNav.name : 'RAG Management System';
});
</script>

<style>
/* Global styles can remain here if needed */

/* Basic styling for router links */
.router-link-exact-active {
  /* Tailwind's active-class takes precedence, but you can add more here */
}
</style>