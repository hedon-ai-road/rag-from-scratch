<template>
  <div>
    <!-- Query Interface -->
    <div class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">搜索查询</h2>

      <div class="mb-4">
        <label class="mb-2 block text-sm font-medium text-gray-700">输入查询</label>
        <div class="flex">
          <input
            v-model="queryInput"
            type="text"
            class="input flex-1"
            placeholder="例如: RAG架构原理是什么?"
            @keyup.enter="submitQuery"
          />
          <button
            @click="submitQuery"
            class="btn btn-primary ml-2"
            :disabled="isProcessing || !queryInput.trim()"
          >
            提交查询
          </button>
        </div>
      </div>

      <div class="mb-4">
        <label class="mb-2 block text-sm font-medium text-gray-700">检索设置</label>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-sm text-gray-600">向量权重: {{ store.searchSettings.vectorWeight }}</span>
            <input
              v-model="store.searchSettings.vectorWeight"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full"
            />
          </div>
          <div>
            <span class="text-sm text-gray-600">BM25权重: {{ store.searchSettings.bm25Weight }}</span>
            <input
              v-model="store.searchSettings.bm25Weight"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <div v-if="isProcessing" class="flex items-center justify-center py-4">
        <div class="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
        <span class="ml-2 text-gray-600">处理中...</span>
      </div>
    </div>

    <!-- Latest Query Result -->
    <div v-if="store.latestQueryResult" class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">查询结果</h2>

      <div class="mb-4">
        <h3 class="text-md font-medium">查询</h3>
        <p class="mt-1 rounded bg-gray-100 p-2">{{ store.latestQueryResult.query }}</p>
      </div>

      <div class="mb-4">
        <h3 class="text-md font-medium">生成回答</h3>
        <div class="mt-1 rounded border border-green-200 bg-green-50 p-3 text-green-800">
          {{ store.latestQueryResult.generatedResponse }}
        </div>
      </div>

      <div>
        <h3 class="text-md font-medium">检索到的分块</h3>
        <div v-if="store.latestQueryResult.retrievedChunks.length === 0" class="text-gray-500">
          没有检索到相关分块
        </div>
        <div v-else class="mt-2">
          <div
            v-for="(chunk, index) in store.latestQueryResult.retrievedChunks"
            :key="chunk.chunk_id"
            class="mb-2 rounded border border-blue-100 bg-blue-50 p-2"
          >
            <div class="mb-1 flex items-center justify-between">
              <span class="text-sm font-semibold text-blue-800">Chunk #{{ index + 1 }}</span>
              <span class="text-xs text-gray-500">ID: {{ chunk.chunk_id }}</span>
            </div>
            <p class="text-sm">{{ chunk.content }}</p>
          </div>
        </div>
      </div>

      <div class="mt-4 text-right text-xs text-gray-500">
        检索得分: 向量 {{ store.latestQueryResult.searchScores.vector.toFixed(2) }},
        BM25 {{ store.latestQueryResult.searchScores.bm25.toFixed(2) }} |
        时间: {{ formatDate(store.latestQueryResult.timestamp) }}
      </div>
    </div>

    <!-- Search History -->
    <div class="card">
      <h2 class="mb-4 text-lg font-semibold">搜索历史</h2>
      <div v-if="store.searchLogs.length === 0" class="text-gray-500">
        暂无搜索历史
      </div>
      <ul v-else class="divide-y">
        <li
          v-for="(log, index) in sortedSearchLogs"
          :key="index"
          class="py-3"
          @click="replaySearch(log.query)"
          style="cursor: pointer;"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium">{{ log.query }}</p>
              <p class="text-sm text-gray-500">
                查询时间: {{ formatDate(log.timestamp) }}
              </p>
              <p class="text-xs text-gray-400">
                检索到的分块: {{ log.top_chunks.length }} |
                得分: 向量 {{ log.scores.vector.toFixed(2) }}, BM25 {{ log.scores.bm25.toFixed(2) }}
              </p>
            </div>
            <button
              class="btn btn-secondary px-2 py-1 text-xs"
              @click.stop="replaySearch(log.query)"
            >
              重新查询
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
const queryInput = ref('');
const isProcessing = ref(false);

// Sort search logs by timestamp (newest first)
const sortedSearchLogs = computed(() => {
  return [...store.searchLogs].sort((a, b) => {
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });
});

// Submit a new query
const submitQuery = async () => {
  if (!queryInput.value.trim() || isProcessing.value) return;

  isProcessing.value = true;

  try {
    // Simulate network delay for realism
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Process the query through our mock RAG pipeline
    store.performMockRagQuery(queryInput.value);

    // Clear the input after successful query
    queryInput.value = '';
  } finally {
    isProcessing.value = false;
  }
};

// Replay a previous search
const replaySearch = (query: string) => {
  queryInput.value = query;
  submitQuery();
};

// Format date for display
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>