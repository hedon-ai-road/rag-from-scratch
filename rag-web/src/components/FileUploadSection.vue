<template>
  <div class="rounded-lg border bg-white p-6 shadow">
    <h2 class="mb-4 text-lg font-semibold">文件上传</h2>
    <div
      class="flex h-32 items-center justify-center rounded border-2 border-dashed border-gray-300 hover:border-blue-500"
      @drop.prevent="handleDrop"
      @dragover.prevent
      @dragleave.prevent
    >
      <!-- Hidden file input triggered by button -->
      <input type="file" ref="fileInput" @change="handleSelect" hidden multiple />

      <div class="text-center">
        <p class="mb-2 text-gray-500">拖拽文件到这里，或</p>
        <button
          @click="triggerFileInput"
          class="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          选择文件
        </button>
        <!-- Display selected file names or status -->
        <div v-if="selectedFiles.length > 0" class="mt-3 text-sm text-gray-600">
          <p>已选择 {{ selectedFiles.length }} 个文件:</p>
          <ul>
            <li v-for="file in selectedFiles" :key="file.name">{{ file.name }}</li>
          </ul>
        </div>
      </div>
    </div>
     <!-- Optional: Add a button to trigger processing manually -->
     <div class="mt-4 text-right" v-if="selectedFiles.length > 0">
        <button
          @click="processSelectedFiles"
          class="rounded bg-green-500 px-4 py-2 text-white hover:bg-green-600 disabled:opacity-50"
          :disabled="isProcessing"
        >
          {{ isProcessing ? '处理中...' : '开始处理' }}
        </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
// Only import invoke when needed to avoid browser errors
// import { invoke } from "@tauri-apps/api/core";

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFiles = ref<File[]>([]);
const isProcessing = ref(false);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files) {
    selectedFiles.value = Array.from(e.dataTransfer.files);
    // Optionally process immediately: processFiles(selectedFiles.value);
  }
};

const handleSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files) {
    selectedFiles.value = Array.from(target.files);
    // Optionally process immediately: processFiles(selectedFiles.value);
  }
};

const processSelectedFiles = () => {
  if (selectedFiles.value.length > 0) {
    processFiles(selectedFiles.value);
  }
};

// --- Mocked Interaction ---
async function processFiles(files: File[]) {
  isProcessing.value = true;
  console.log(`Simulating processing for ${files.length} file(s)...`);

  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  try {
    // Simulate a successful response
    // In a real scenario, this would be the result from invoke
    const mockResponse = {
      message: `Successfully processed ${files[0]?.name || 'file'}`,
      data: { someId: 123, status: 'completed' },
    };

    // Simulate random failure (optional)
    // if (Math.random() < 0.3) {
    //   throw new Error("Random processing error occurred!");
    // }

    console.log("模拟处理结果:", mockResponse);
    alert(`文件处理成功: ${JSON.stringify(mockResponse)}`);

    // Clear selection after successful mock processing (optional)
    // selectedFiles.value = [];
  } catch (error) {
    console.error("模拟文件处理失败:", error);
    alert(`模拟文件处理失败: ${error}`);
  } finally {
    isProcessing.value = false;
  }
}
</script>

<style scoped>
/* Add component-specific styles here if needed */
</style>