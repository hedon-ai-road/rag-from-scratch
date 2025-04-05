<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Chunk Engine</h1>
    <p class="mb-4">Configure chunking strategies and preview results.</p>

    <!-- Chunking Configuration -->
    <div class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">分块配置</h2>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">分块策略</label>
          <select class="input w-full">
            <option value="sliding_window">滑动窗口</option>
            <option value="semantic">语义分块</option>
            <option value="recursive">递归分割</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">最大窗口大小 (字符数)</label>
          <input
            v-model="store.chunkSettings.window_size"
            type="number"
            min="100"
            max="2048"
            step="128"
            class="input w-full"
          />
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">重叠大小 (字符数)</label>
          <input
            v-model="store.chunkSettings.overlap"
            type="number"
            min="0"
            max="512"
            step="32"
            class="input w-full"
          />
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">分块策略</label>
          <select v-model="store.chunkSettings.strategy" class="input w-full">
            <option value="sliding_window">滑动窗口</option>
            <option value="semantic">语义分块</option>
          </select>
        </div>
      </div>

      <div class="mt-4">
        <button class="btn btn-primary">应用配置</button>
      </div>
    </div>

    <!-- Files and Chunks -->
    <div class="card">
      <h2 class="mb-4 text-lg font-semibold">文件分块结果</h2>

      <div v-if="store.files.length === 0" class="text-gray-500">
        暂无文件，请先上传
      </div>

      <div v-else class="space-y-6">
        <div v-for="file in store.files" :key="file.file_id" class="border-b pb-4 last:border-b-0">
          <div class="mb-2 flex items-center">
            <h3 class="text-md font-medium">{{ file.file_name }}</h3>
            <span class="ml-2 text-sm text-gray-500">{{ formatFileSize(file.file_size) }}</span>
          </div>

          <div class="ml-4">
            <div v-if="getChunksForFile(file.file_id).length === 0" class="text-gray-500">
              该文件没有分块
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="chunk in getChunksForFile(file.file_id)"
                :key="chunk.chunk_id"
                class="rounded border border-green-100 bg-green-50 p-2"
              >
                <div class="mb-1 flex items-center justify-between">
                  <span class="text-sm font-semibold text-green-800">{{ chunk.chunk_id }}</span>
                  <span class="text-xs text-gray-500">位置: {{ chunk.start_offset }}-{{ chunk.end_offset }}</span>
                </div>
                <p class="text-sm">{{ chunk.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();

// Get chunks for a specific file
const getChunksForFile = (fileId: string) => {
  return store.getChunksForFile(fileId);
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