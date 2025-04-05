<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">File Loader</h1>
    <p>Upload and manage source documents (PDF, TXT, Markdown).</p>
    <!-- Include the FileUploadSection component here -->
    <FileUploadSection />
  </div>
</template>

<script setup lang="ts">
import FileUploadSection from '../components/FileUploadSection.vue';
</script>