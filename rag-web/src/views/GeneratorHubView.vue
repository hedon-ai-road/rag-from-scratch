<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Generator Hub</h1>
    <p class="mb-4">Manage prompts and trace generation process.</p>

    <!-- Placeholder for Prompt Editing UI -->
    <div class="mb-6 p-4 border rounded bg-gray-100">
      Prompt Template Editor Placeholder
    </div>

    <!-- Display Generation Records -->
     <h2 class="text-xl font-semibold mb-3">Generation History (latest 5)</h2>
      <div v-if="store.generations.length === 0" class="text-gray-500">
        No generations recorded yet.
      </div>
      <div v-else class="space-y-3">
        <div v-for="gen in store.generations.slice(-5).reverse()" :key="gen.gen_id" class="p-3 border rounded bg-white shadow-sm text-sm">
           <p><strong>Timestamp:</strong> {{ new Date(gen.created_at).toLocaleString() }}</p>
           <p><strong>Query:</strong> "{{ gen.query }}"</p>
           <p><strong>Used Chunks:</strong> {{ gen.used_chunks.join(', ') }}</p>
           <p><strong>Response:</strong> {{ gen.response }}</p>
           <p class="text-gray-600"><strong>Generation ID:</strong> {{ gen.gen_id }}</p>
        </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
</script>