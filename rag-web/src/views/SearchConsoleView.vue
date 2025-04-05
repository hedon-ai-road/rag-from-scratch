<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Search Console</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Search Panel -->
      <div class="lg:col-span-1">
        <div class="card">
          <h2 class="mb-4 text-lg font-semibold">Search Settings</h2>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Search Type</label>
            <select v-model="searchType" class="input w-full">
              <option value="vector">Vector Search</option>
              <option value="hybrid">Hybrid Search (Vector + BM25)</option>
              <option value="keyword">Keyword Search (BM25 only)</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Top K Results</label>
            <input
              v-model.number="topK"
              type="number"
              min="1"
              max="20"
              class="input w-full"
            />
          </div>

          <div class="mb-4" v-if="searchType === 'hybrid'">
            <label class="mb-2 block text-sm font-medium text-gray-700">Hybrid Weight</label>
            <div class="flex items-center">
              <span class="text-sm mr-2 w-16">Vector: {{ hybridWeight }}</span>
              <input
                v-model.number="hybridWeight"
                type="range"
                min="0"
                max="1"
                step="0.1"
                class="w-full"
              />
              <span class="text-sm ml-2 w-16">BM25: {{ (1 - hybridWeight).toFixed(1) }}</span>
            </div>
          </div>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Filter By Document</label>
            <select v-model="selectedFileId" class="input w-full">
              <option value="">All Documents</option>
              <option
                v-for="file in indexedFiles"
                :key="file.file_id"
                :value="file.file_id"
              >
                {{ file.file_name }}
              </option>
            </select>
          </div>

          <div class="mb-6">
            <label class="mb-2 block text-sm font-medium text-gray-700">Query</label>
            <textarea
              v-model="searchQuery"
              rows="3"
              class="input w-full text-sm"
              placeholder="Enter your search query here..."
            ></textarea>
          </div>

          <div class="flex space-x-2">
            <button
              class="btn btn-primary flex-1"
              @click="search"
              :disabled="!searchQuery || isSearching"
            >
              {{ isSearching ? 'Searching...' : 'Search' }}
            </button>
            <button
              class="btn"
              @click="resetSearch"
            >
              Reset
            </button>
          </div>
        </div>

        <!-- Search History -->
        <div class="card mt-6">
          <h2 class="mb-4 text-lg font-semibold">Recent Searches</h2>

          <div v-if="store.searchLogs.length === 0" class="text-gray-500 text-center py-4">
            No search history yet
          </div>

          <ul v-else class="divide-y">
            <li
              v-for="(log, index) in store.searchLogs.slice().reverse().slice(0, 5)"
              :key="index"
              class="py-2 cursor-pointer hover:bg-gray-50"
              @click="loadSearchFromHistory(log)"
            >
              <p class="font-medium truncate">{{ log.query }}</p>
              <p class="text-xs text-gray-500">
                {{ formatDate(log.timestamp) }} • {{ log.top_chunks.length }} results
              </p>
            </li>
          </ul>
        </div>
      </div>

      <!-- Results Panel -->
      <div class="lg:col-span-2">
        <div class="card">
          <div class="border-b mb-4">
            <div class="flex">
              <button
                @click="activeTab = 'results'"
                class="px-4 py-2 font-medium border-b-2 transition-colors"
                :class="activeTab === 'results' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
              >
                Search Results
              </button>
              <button
                @click="activeTab = 'visualization'"
                class="px-4 py-2 font-medium border-b-2 transition-colors"
                :class="activeTab === 'visualization' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
              >
                Results Visualization
              </button>
            </div>
          </div>

          <!-- Placeholder for no results -->
          <div v-if="!searchResults.retrievedChunks || searchResults.retrievedChunks.length === 0" class="py-12">
            <div class="text-center">
              <div class="mb-4">
                <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900">No search results yet</h3>
              <p class="mt-1 text-sm text-gray-500">
                Enter your query and click the search button to find relevant information
              </p>
            </div>
          </div>

          <!-- Results Tab -->
          <div v-else-if="activeTab === 'results'" class="h-[calc(100vh-280px)] overflow-y-auto">
            <div class="mb-4 flex justify-between items-center">
              <h3 class="font-medium">{{ searchResults.retrievedChunks.length }} results for "{{ searchResults.query }}"</h3>
              <p class="text-sm text-gray-500">{{ formatDate(searchResults.timestamp) }}</p>
            </div>

            <div
              v-for="(chunk, index) in searchResults.retrievedChunks"
              :key="chunk.chunk_id"
              class="mb-4 p-4 border rounded hover:border-blue-300 transition-colors"
            >
              <div class="mb-2 flex justify-between">
                <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded">
                  Rank #{{ index + 1 }}
                </span>
                <span class="text-xs text-gray-500">
                  {{ getDocumentName(chunk.file_id) }} ({{ chunk.chunk_id }})
                </span>
              </div>

              <p class="mb-2 text-sm whitespace-pre-line">{{ chunk.content }}</p>

              <div class="flex justify-end space-x-2">
                <button
                  class="text-xs bg-gray-100 px-2 py-1 rounded hover:bg-gray-200"
                  @click="copyToClipboard(chunk.content)"
                >
                  Copy
                </button>
                <button
                  class="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded hover:bg-blue-100"
                  @click="requestGeneration(chunk.content)"
                >
                  Use for Generation
                </button>
              </div>
            </div>
          </div>

          <!-- Visualization Tab -->
          <div v-else-if="activeTab === 'visualization'" class="h-[calc(100vh-280px)] overflow-y-auto">
            <div class="mb-4">
              <h3 class="font-medium mb-2">Search Score Distribution</h3>

              <div v-if="searchResults.searchScores" class="mb-6">
                <div class="mb-2">
                  <div class="flex justify-between mb-1">
                    <span class="text-sm font-medium text-blue-700">Vector Similarity</span>
                    <span class="text-sm text-blue-700">{{ searchResults.searchScores.vector * 100 }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full" :style="{ width: `${searchResults.searchScores.vector * 100}%` }"></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between mb-1">
                    <span class="text-sm font-medium text-green-700">BM25 Relevance</span>
                    <span class="text-sm text-green-700">{{ searchResults.searchScores.bm25 * 100 }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-green-600 h-2 rounded-full" :style="{ width: `${searchResults.searchScores.bm25 * 100}%` }"></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="mb-4">
              <h3 class="font-medium mb-2">Document Distribution</h3>

              <div class="relative h-40">
                <!-- Simple bar chart for document distribution -->
                <div class="flex h-full items-end space-x-2">
                  <div
                    v-for="(count, fileId) in documentDistribution"
                    :key="fileId"
                    class="flex-1 bg-indigo-500 rounded-t"
                    :style="{ height: `${(count / searchResults.retrievedChunks.length) * 100}%` }"
                  ></div>
                </div>

                <!-- X-axis labels -->
                <div class="flex mt-2 space-x-2 overflow-hidden">
                  <div
                    v-for="(count, fileId) in documentDistribution"
                    :key="fileId"
                    class="flex-1 truncate text-xs text-center"
                  >
                    {{ getDocumentName(String(fileId)).split('.')[0] }}
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 class="font-medium mb-2">Keyword Highlights</h3>

              <div class="grid grid-cols-3 gap-2">
                <div
                  v-for="(weight, keyword) in keywordHighlights"
                  :key="keyword"
                  class="p-2 rounded text-center"
                  :style="{
                    backgroundColor: `rgba(59, 130, 246, ${weight * 0.5})`,
                    color: weight > 0.5 ? 'white' : 'black'
                  }"
                >
                  {{ keyword }}
                </div>
              </div>
            </div>
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
const searchType = ref('vector');
const topK = ref(5);
const hybridWeight = ref<number>(0.7);
const selectedFileId = ref('');
const searchQuery = ref('');
const isSearching = ref(false);
const activeTab = ref('results');
const searchResults = ref<any>({});

// Computed properties
const indexedFiles = computed(() => {
  // In a real app, this would be files that have been indexed
  // For mock purposes, we'll use all files with vectors
  return store.files.filter(file => {
    return store.vectors.some(v => v.file_id === file.file_id);
  });
});

const documentDistribution = computed(() => {
  if (!searchResults.value.retrievedChunks) return {};

  const distribution: {[key: string]: number} = {};

  searchResults.value.retrievedChunks.forEach((chunk: any) => {
    if (!distribution[chunk.file_id]) {
      distribution[chunk.file_id] = 0;
    }
    distribution[chunk.file_id]++;
  });

  return distribution;
});

const keywordHighlights = computed(() => {
  if (!searchResults.value.query) return {};

  // Extract keywords and assign mock weights
  const keywords = searchResults.value.query.split(' ')
    .filter((word: string) => word.length > 3)
    .reduce((acc: {[key: string]: number}, word: string) => {
      acc[word] = Math.random() * 0.5 + 0.3; // Random weight between 0.3 and 0.8
      return acc;
    }, {});

  return keywords;
});

// Methods
const getDocumentName = (fileId: string): string => {
  const file = store.files.find(f => f.file_id === fileId);
  return file ? file.file_name : 'Unknown Document';
};

const search = () => {
  if (!searchQuery.value || isSearching.value) return;

  isSearching.value = true;

  // Update search settings in store
  store.searchSettings.vectorWeight = searchType.value === 'keyword' ? 0 : (searchType.value === 'hybrid' ? hybridWeight.value : 1);
  store.searchSettings.bm25Weight = searchType.value === 'vector' ? 0 : (searchType.value === 'hybrid' ? 1 - hybridWeight.value : 1);
  store.searchSettings.topK = topK.value;

  // If a specific file is selected, modify the query to target that file
  let finalQuery = searchQuery.value;
  if (selectedFileId.value) {
    const file = store.files.find(f => f.file_id === selectedFileId.value);
    if (file) {
      finalQuery = `${finalQuery} (in document: ${file.file_name})`;
    }
  }

  // Simulate async search
  setTimeout(() => {
    // Call the store method to search
    const result = store.performMockRagQuery(finalQuery);
    searchResults.value = result;

    isSearching.value = false;
    activeTab.value = 'results';
  }, 1000);
};

const resetSearch = () => {
  searchQuery.value = '';
  searchResults.value = {};
  activeTab.value = 'results';
};

const loadSearchFromHistory = (log: any) => {
  searchQuery.value = log.query;

  // Construct search results from log
  const chunks = log.top_chunks.map((chunkId: string) => {
    return store.chunks.find(c => c.chunk_id === chunkId);
  }).filter(Boolean);

  searchResults.value = {
    query: log.query,
    retrievedChunks: chunks,
    searchScores: log.scores,
    timestamp: log.timestamp
  };

  activeTab.value = 'results';
};

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
    .catch(err => console.error('Failed to copy text: ', err));
};

const requestGeneration = (context: string) => {
  // In a real application, this would navigate to the generator view
  // or set up a generation with this context
  alert('Generation requested with the selected context. In a real application, this would navigate to the Generator Hub.');
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '';

  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};
</script>