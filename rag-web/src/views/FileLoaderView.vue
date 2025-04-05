<template>
  <div>
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- File Upload Section -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">文件上传</h2>
        <div
          class="flex h-32 items-center justify-center rounded border-2 border-dashed border-gray-300 hover:border-blue-500"
          @drop.prevent="handleDrop"
          @dragover.prevent
          @dragenter.prevent
        >
          <input
            type="file"
            @change="handleFileSelect"
            ref="fileInput"
            hidden
            accept=".pdf,.txt,.md"
          />
          <button
            @click="openFileSelector"
            class="btn btn-primary"
          >
            选择文件
          </button>
        </div>
        <div v-if="uploadStatus" class="mt-4 p-3" :class="uploadStatusClass">
          {{ uploadStatus }}
        </div>
      </div>

      <!-- Uploaded Files List -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">已上传文件</h2>
        <div v-if="store.files.length === 0" class="text-gray-500">
          暂无文件，请先上传
        </div>
        <ul v-else class="divide-y">
          <li v-for="file in store.files" :key="file.file_id" class="py-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium">{{ file.file_name }}</p>
                <p class="text-sm text-gray-500">
                  大小: {{ formatFileSize(file.file_size) }} |
                  上传时间: {{ formatDate(file.created_at) }}
                </p>
                <p class="text-xs text-gray-400">ID: {{ file.file_id }}</p>
              </div>
              <div class="flex space-x-2">
                <button
                  class="rounded-lg px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
                  @click="viewDetails(file)"
                >
                  查看
                </button>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- File Processing Pipeline -->
    <div class="mt-6 card">
      <h2 class="mb-4 text-lg font-semibold">文件处理链</h2>
      <div class="flex items-center justify-between">
        <div class="flex space-x-4">
          <div class="text-center">
            <div class="rounded-full bg-green-100 p-3">
              <span class="text-lg font-semibold text-green-600">{{ store.fileCount }}</span>
            </div>
            <p class="mt-1 text-sm">文件</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-blue-100 p-3">
              <span class="text-lg font-semibold text-blue-600">{{ store.chunkCount }}</span>
            </div>
            <p class="mt-1 text-sm">分块</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-purple-100 p-3">
              <span class="text-lg font-semibold text-purple-600">{{ store.vectorCount }}</span>
            </div>
            <p class="mt-1 text-sm">向量</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-amber-100 p-3">
              <span class="text-lg font-semibold text-amber-600">{{ store.searchCount }}</span>
            </div>
            <p class="mt-1 text-sm">查询</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-red-100 p-3">
              <span class="text-lg font-semibold text-red-600">{{ store.generationCount }}</span>
            </div>
            <p class="mt-1 text-sm">生成</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
const fileInput = ref<HTMLInputElement | null>(null);
const uploadStatus = ref('');
const uploadStatusClass = computed(() => {
  if (uploadStatus.value.includes('成功')) {
    return 'bg-green-100 text-green-700 rounded';
  } else if (uploadStatus.value.includes('错误') || uploadStatus.value.includes('失败')) {
    return 'bg-red-100 text-red-700 rounded';
  } else {
    return 'bg-blue-100 text-blue-700 rounded';
  }
});

// Open the file selector
const openFileSelector = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// Handle file drop
const handleDrop = (e: DragEvent) => {
  if (!e.dataTransfer) return;

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    processFile(files[0]);
  }
};

// Handle file select from input
const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    processFile(target.files[0]);
  }
};

// Process the file
const processFile = (file: File) => {
  uploadStatus.value = `处理文件: ${file.name}...`;

  // Check file type
  const allowedTypes = ['.pdf', '.txt', '.md'];
  const extension = '.' + file.name.split('.').pop()?.toLowerCase();

  if (!allowedTypes.includes(extension)) {
    uploadStatus.value = `错误: 不支持的文件类型 ${extension}，仅支持 PDF, TXT, MD`;
    return;
  }

  // Check file size (max 50MB)
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (file.size > maxSize) {
    uploadStatus.value = `错误: 文件过大 (${formatFileSize(file.size)})，最大限制为 50MB`;
    return;
  }

  // Mock processing delay
  setTimeout(() => {
    // Add the file to our store
    store.addFile(file.name, file.size);
    uploadStatus.value = `成功: 文件 ${file.name} 已上传并处理`;

    // Reset file input
    if (fileInput.value) {
      fileInput.value.value = '';
    }
  }, 1500);
};

// Format file size for display
const formatFileSize = (size: number): string => {
  if (size < 1024) {
    return `${size} B`;
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  } else {
    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }
};

// Format date for display
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

// View file details
const viewDetails = (file: any) => {
  console.log('View details for file:', file);
  // Could open a modal or navigate to a file detail view
};
</script>