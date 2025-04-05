<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Search Console</h1>
    <p class="mb-4">Debug retrieval, tune parameters, and analyze results.</p>

    <!-- Placeholder for Search/Query Input UI -->
    <div class="mb-6 p-4 border rounded bg-gray-100">
      Query Input and Parameter Tuning UI Placeholder (e.g., weights, top-k)
    </div>

    <!-- Display Search Logs -->
     <h2 class="text-xl font-semibold mb-3">Search Logs (latest 5)</h2>
      <div v-if="store.searchLogs.length === 0" class="text-gray-500">
      No search logs yet.
    </div>
    <div v-else class="space-y-2">
       <div v-for="(log, index) in store.searchLogs.slice(-5).reverse()" :key="index" class="p-3 border rounded bg-white shadow-sm text-sm">
         <p><strong>Timestamp:</strong> {{ new Date(log.timestamp).toLocaleString() }}</p>
         <p><strong>Query:</strong> "{{ log.query }}"</p>
         <p><strong>Top Chunks:</strong> {{ log.top_chunks.join(', ') }}</p>
         <p><strong>Scores:</strong> Vector={{ log.scores.vector.toFixed(2) }}, BM25={{ log.scores.bm25.toFixed(2) }}</p>
       </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
</script>