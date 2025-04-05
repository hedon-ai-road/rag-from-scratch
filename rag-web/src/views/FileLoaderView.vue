<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">File Loader</h1>
    <p class="mb-4">Upload and manage source documents (PDF, TXT, Markdown).</p>

    <!-- File Upload Section -->
    <FileUploadSection @file-processed="handleFileProcessed" class="mb-6"/>

    <!-- Display Existing Files -->
    <h2 class="text-xl font-semibold mb-3">Uploaded Files</h2>
    <div v-if="store.files.length === 0" class="text-gray-500">
      No files uploaded yet.
    </div>
    <div v-else class="space-y-2">
      <div v-for="file in store.files" :key="file.file_id" class="p-3 border rounded bg-white shadow-sm">
        <p><strong>Name:</strong> {{ file.file_name }}</p>
        <p class="text-sm text-gray-600">ID: {{ file.file_id }}</p>
        <p class="text-sm text-gray-600">Size: {{ (file.file_size / 1024).toFixed(2) }} KB</p>
        <p class="text-sm text-gray-600">Created: {{ new Date(file.created_at).toLocaleString() }}</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import FileUploadSection from '../components/FileUploadSection.vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();

// Optional: Handle event from FileUploadSection if needed later
const handleFileProcessed = (/* potential event data */) => {
  // The store's addFile action is triggered directly in the mock now
  // but you could trigger it here based on an event if preferred
  console.log('File processing simulation finished in FileUploadSection.');
};

</script>