<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Pipeline Monitor</h1>
    <p class="mb-4">Visualize pipeline execution, logs, and metrics.</p>

     <!-- Placeholder for Visualization UI -->
    <div class="mb-6 p-4 border rounded bg-gray-100">
       Pipeline Visualization Placeholder (e.g., using Mermaid or Cytoscape)
    </div>

    <!-- Display Summary Counts -->
    <h2 class="text-xl font-semibold mb-3">Data Summary</h2>
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div class="p-4 border rounded bg-white shadow-sm text-center">
        <p class="text-3xl font-bold">{{ store.files.length }}</p>
        <p class="text-gray-600">Files</p>
      </div>
      <div class="p-4 border rounded bg-white shadow-sm text-center">
        <p class="text-3xl font-bold">{{ store.chunks.length }}</p>
        <p class="text-gray-600">Chunks</p>
      </div>
       <div class="p-4 border rounded bg-white shadow-sm text-center">
        <p class="text-3xl font-bold">{{ store.vectors.length }}</p>
        <p class="text-gray-600">Vectors</p>
      </div>
       <div class="p-4 border rounded bg-white shadow-sm text-center">
        <p class="text-3xl font-bold">{{ store.searchLogs.length }}</p>
        <p class="text-gray-600">Search Logs</p>
      </div>
       <div class="p-4 border rounded bg-white shadow-sm text-center">
        <p class="text-3xl font-bold">{{ store.generations.length }}</p>
        <p class="text-gray-600">Generations</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
</script>