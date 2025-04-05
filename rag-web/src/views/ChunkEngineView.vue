<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Chunk Engine</h1>
    <p class="mb-4">Configure chunking strategies and preview results.</p>

    <!-- Placeholder for Chunking Configuration -->
    <div class="mb-6 p-4 border rounded bg-gray-100">
      Chunking Configuration UI Placeholder (e.g., window size, overlap)
    </div>

    <!-- Display Files and Chunks -->
    <h2 class="text-xl font-semibold mb-3">Chunks per File</h2>
     <div v-if="store.files.length === 0" class="text-gray-500">
      Upload a file first.
    </div>
    <div v-else class="space-y-4">
      <div v-for="file in store.files" :key="file.file_id" class="p-4 border rounded bg-white shadow-sm">
        <h3 class="text-lg font-semibold mb-2">{{ file.file_name }} ({{ file.file_id }})</h3>
        <div v-if="store.getChunksByFileId(file.file_id).length === 0" class="text-sm text-gray-500">
          No chunks generated for this file yet.
        </div>
        <div v-else class="space-y-2 max-h-60 overflow-y-auto pr-2">
          <div v-for="chunk in store.getChunksByFileId(file.file_id)" :key="chunk.chunk_id" class="p-2 border rounded bg-gray-50 text-sm">
            <p><strong>ID:</strong> {{ chunk.chunk_id }}</p>
            <p><strong>Offsets:</strong> [{{ chunk.start_offset }} - {{ chunk.end_offset }}]</p>
            <p class="font-mono bg-gray-200 p-1 rounded break-words">{{ chunk.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
</script>

<style scoped>
/* Optional: Add styles for scrollbar etc. */
.max-h-60::-webkit-scrollbar {
  width: 6px;
}
.max-h-60::-webkit-scrollbar-thumb {
  background-color: #cbd5e1; /* cool-gray-300 */
  border-radius: 3px;
}
</style>