<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Embedding Lab</h1>
    <p class="mb-4">Choose embedding models and evaluate quality.</p>

    <!-- Placeholder for Model Selection/Config UI -->
    <div class="mb-6 p-4 border rounded bg-gray-100">
       Embedding Model Configuration Placeholder (e.g., BGE-M3, OpenAI)
    </div>

    <!-- Display Vectors -->
    <h2 class="text-xl font-semibold mb-3">Generated Vectors (showing first 10)</h2>
    <div v-if="store.vectors.length === 0" class="text-gray-500">
      No vectors generated yet.
    </div>
    <div v-else class="space-y-2">
       <div v-for="vector in store.vectors.slice(0, 10)" :key="vector.id" class="p-3 border rounded bg-white shadow-sm text-sm">
         <p><strong>Vector ID:</strong> {{ vector.id }}</p>
         <p class="text-gray-600"><strong>File ID:</strong> {{ vector.payload.file_id }}</p>
         <p class="text-gray-600"><strong>Chunk ID:</strong> {{ vector.payload.chunk_id }}</p>
         <p class="text-gray-600 font-mono break-all"><strong>Vector (first 5 dims):</strong> [{{ vector.vector.slice(0, 5).map(v => v.toFixed(3)).join(', ') }}...]</p>
       </div>
       <p v-if="store.vectors.length > 10" class="text-sm text-gray-500 mt-2">... and {{ store.vectors.length - 10 }} more.</p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
</script>