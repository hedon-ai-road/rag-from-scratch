<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar Navigation -->
    <aside class="w-64 bg-gray-800 text-white p-4 flex flex-col">
      <h1 class="text-2xl font-bold mb-6">RAG 系统</h1>
      <nav class="flex flex-col space-y-2">
        <router-link
          v-for="route in routes"
          :key="route.path"
          :to="route.path"
          class="px-3 py-2 rounded hover:bg-gray-700"
          active-class="bg-gray-900 font-semibold"
        >
          {{ route.name }}
        </router-link>
      </nav>
      <div class="mt-auto text-xs text-gray-400">
         <!-- Footer or status area -->
         Status: Ready
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Optional Top Bar within Main Content -->
       <header class="bg-white shadow-sm p-4">
        <h2 class="text-xl font-semibold text-gray-800">{{ currentRouteName }}</h2>
      </header>

      <!-- Router View where page components are rendered -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useRagDataStore } from './stores/ragDataStore';

const router = useRouter();
const ragDataStore = useRagDataStore();

// Initialize mock data when component is mounted
onMounted(() => {
  ragDataStore.initializeMockData();
});

// Filter routes for navigation (optional, e.g., hide redirects)
const routes = router.options.routes.filter(r => r.component); // Only show routes with components

// Get the name of the current route for the header
const currentRouteName = computed(() => {
  // Find the matched route based on the current path
  const matchedRoute = routes.find(r => r.path === router.currentRoute.value.path);
  // Use the route's name property, fallback to a default
  return matchedRoute?.name || 'Dashboard';
});

// We no longer import FileUploadSection here as it's in FileLoaderView
// import FileUploadSection from "./components/FileUploadSection.vue";

</script>

<style>
/* Global styles can remain here if needed */

/* Basic styling for router links */
.router-link-exact-active {
  /* Tailwind's active-class takes precedence, but you can add more here */
}
</style>