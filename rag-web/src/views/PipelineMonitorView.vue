<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Pipeline Monitor</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- System Overview -->
      <div class="lg:col-span-1">
        <div class="card mb-6">
          <h2 class="mb-4 text-lg font-semibold">System Overview</h2>

          <div class="grid grid-cols-2 gap-4">
            <div class="rounded bg-blue-50 p-3 text-center">
              <p class="text-sm text-blue-700">Files</p>
              <p class="text-2xl font-semibold text-blue-800">{{ store.fileCount }}</p>
            </div>

            <div class="rounded bg-green-50 p-3 text-center">
              <p class="text-sm text-green-700">Chunks</p>
              <p class="text-2xl font-semibold text-green-800">{{ store.chunkCount }}</p>
            </div>

            <div class="rounded bg-purple-50 p-3 text-center">
              <p class="text-sm text-purple-700">Vectors</p>
              <p class="text-2xl font-semibold text-purple-800">{{ store.vectorCount }}</p>
            </div>

            <div class="rounded bg-amber-50 p-3 text-center">
              <p class="text-sm text-amber-700">Searches</p>
              <p class="text-2xl font-semibold text-amber-800">{{ store.searchCount }}</p>
            </div>
          </div>

          <div class="mt-4 rounded bg-indigo-50 p-3 text-center">
            <p class="text-sm text-indigo-700">Total Generations</p>
            <p class="text-2xl font-semibold text-indigo-800">{{ store.generationCount }}</p>
          </div>

          <div class="mt-4">
            <p class="text-sm text-gray-600">System Status: <span class="text-green-600 font-medium">Operational</span></p>
            <p class="text-sm text-gray-600">Last updated: {{ getCurrentTime() }}</p>
          </div>
        </div>

        <!-- Stage Configuration -->
        <div class="card mb-6">
          <h2 class="mb-4 text-lg font-semibold">Current Configuration</h2>

          <div class="space-y-3">
            <div>
              <p class="text-sm font-medium text-gray-700">Chunk Strategy</p>
              <p class="text-sm bg-gray-50 p-2 rounded">{{ store.chunkSettings.strategy }} (Window: {{ store.chunkSettings.window_size }}, Overlap: {{ store.chunkSettings.overlap }})</p>
            </div>

            <div>
              <p class="text-sm font-medium text-gray-700">Vector Model</p>
              <p class="text-sm bg-gray-50 p-2 rounded">{{ store.vectorSettings.model }} (Dimensions: {{ store.vectorSettings.dimensions }})</p>
            </div>

            <div>
              <p class="text-sm font-medium text-gray-700">Search Settings</p>
              <p class="text-sm bg-gray-50 p-2 rounded">Vector: {{ store.searchSettings.vectorWeight }}, BM25: {{ store.searchSettings.bm25Weight }}, Top-K: {{ store.searchSettings.topK }}</p>
            </div>
          </div>

          <div class="mt-4">
            <button class="btn">Export Configuration</button>
          </div>
        </div>
      </div>

      <!-- Pipeline Stages and Metrics -->
      <div class="lg:col-span-2">
        <div class="card mb-6">
          <h2 class="mb-4 text-lg font-semibold">Pipeline Stages</h2>

          <div class="relative">
            <!-- Pipeline flow diagram -->
            <div class="space-y-4">
              <div class="flex items-center">
                <div class="w-56 rounded border border-l-4 border-l-blue-500 p-3">
                  <p class="font-medium">Document Loading</p>
                  <p class="text-xs text-gray-500">{{ formatTimeDifference(getFirstDocumentTime()) }}</p>
                </div>
                <div class="w-10 text-center">
                  <svg class="mx-auto h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                  </svg>
                </div>
                <div class="w-56 rounded border border-l-4 border-l-green-500 p-3">
                  <p class="font-medium">Chunking</p>
                  <p class="text-xs text-gray-500">{{ store.chunkCount }} chunks generated</p>
                </div>
              </div>

              <div class="ml-28 flex items-center">
                <div class="w-10 text-center">
                  <svg class="mx-auto h-5 w-5 text-gray-400 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                  </svg>
                </div>
              </div>

              <div class="flex items-center">
                <div class="w-56 rounded border border-l-4 border-l-amber-500 p-3">
                  <p class="font-medium">Generation</p>
                  <p class="text-xs text-gray-500">{{ store.generationCount }} responses</p>
                </div>
                <div class="w-10 text-center">
                  <svg class="mx-auto h-5 w-5 text-gray-400 transform -scale-x-100" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                  </svg>
                </div>
                <div class="w-56 rounded border border-l-4 border-l-indigo-500 p-3">
                  <p class="font-medium">Search & Retrieval</p>
                  <p class="text-xs text-gray-500">{{ store.searchCount }} searches</p>
                </div>
              </div>

              <div class="ml-28 flex items-center">
                <div class="w-10 text-center">
                  <svg class="mx-auto h-5 w-5 text-gray-400 transform -rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                  </svg>
                </div>
              </div>

              <div class="flex items-center">
                <div class="w-56 rounded border border-l-4 border-l-purple-500 p-3">
                  <p class="font-medium">Vector Embedding</p>
                  <p class="text-xs text-gray-500">{{ store.vectorCount }} vectors</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Log -->
        <div class="card mb-6">
          <h2 class="mb-4 text-lg font-semibold">Activity Log</h2>

          <div class="h-80 overflow-y-auto">
            <div v-if="activityLog.length === 0" class="text-center text-gray-500 py-8">
              No activity recorded yet
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="(activity, index) in activityLog"
                :key="index"
                class="rounded border p-3"
                :class="{
                  'border-blue-100 bg-blue-50': activity.type === 'file',
                  'border-green-100 bg-green-50': activity.type === 'chunk',
                  'border-purple-100 bg-purple-50': activity.type === 'vector',
                  'border-amber-100 bg-amber-50': activity.type === 'search',
                  'border-indigo-100 bg-indigo-50': activity.type === 'generation'
                }"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-medium">{{ activity.title }}</p>
                    <p class="text-sm">{{ activity.description }}</p>
                  </div>
                  <span class="text-xs text-gray-500">{{ formatDate(activity.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Metrics -->
        <div class="card">
          <h2 class="mb-4 text-lg font-semibold">Performance Metrics</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="rounded border p-4">
              <h3 class="text-sm font-medium mb-2">Retrieval Accuracy</h3>
              <div class="h-8 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-blue-600 rounded-full" style="width: 78%"></div>
              </div>
              <p class="mt-1 text-sm text-right">78%</p>
            </div>

            <div class="rounded border p-4">
              <h3 class="text-sm font-medium mb-2">Response Generation Time</h3>
              <div class="h-8 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-green-600 rounded-full" style="width: 65%"></div>
              </div>
              <p class="mt-1 text-sm text-right">1.2s avg</p>
            </div>

            <div class="rounded border p-4">
              <h3 class="text-sm font-medium mb-2">Chunk Quality</h3>
              <div class="h-8 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-purple-600 rounded-full" style="width: 82%"></div>
              </div>
              <p class="mt-1 text-sm text-right">82%</p>
            </div>

            <div class="rounded border p-4">
              <h3 class="text-sm font-medium mb-2">Embedding Throughput</h3>
              <div class="h-8 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-amber-600 rounded-full" style="width: 90%"></div>
              </div>
              <p class="mt-1 text-sm text-right">25 docs/min</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();

interface ActivityLogItem {
  type: 'file' | 'chunk' | 'vector' | 'search' | 'generation';
  title: string;
  description: string;
  timestamp: string;
}

// Activity log (would be populated from real events in a production app)
const activityLog = ref<ActivityLogItem[]>([]);

// Generate mock activity log
onMounted(() => {
  // Mock activity log based on store data
  generateMockActivityLog();
});

const generateMockActivityLog = () => {
  const now = new Date();

  // Add file activities
  store.files.forEach(file => {
    const timestamp = new Date(file.created_at).getTime();
    activityLog.value.push({
      type: 'file',
      title: `File Loaded: ${file.file_name}`,
      description: `File size: ${formatFileSize(file.file_size)}, Method: ${file.loadingMethod || 'PyMuPDF'}`,
      timestamp: file.created_at
    });

    // Add chunking activities shortly after
    const chunkTime = new Date(timestamp + 2 * 60 * 1000);
    const chunks = store.getChunksForFile(file.file_id);
    if (chunks.length > 0) {
      activityLog.value.push({
        type: 'chunk',
        title: `Chunking Completed: ${file.file_name}`,
        description: `${chunks.length} chunks created with ${store.chunkSettings.strategy} strategy`,
        timestamp: chunkTime.toISOString()
      });

      // Add embedding activities
      const embedTime = new Date(timestamp + 5 * 60 * 1000);
      const vectors = store.vectors.filter(v => v.file_id === file.file_id);
      if (vectors.length > 0) {
        activityLog.value.push({
          type: 'vector',
          title: 'Vector Embeddings Generated',
          description: `Created ${vectors.length} embeddings using ${store.vectorSettings.model}`,
          timestamp: embedTime.toISOString()
        });
      }
    }
  });

  // Add search activities
  store.searchLogs.forEach(log => {
    activityLog.value.push({
      type: 'search',
      title: `Search Performed: "${log.query}"`,
      description: `Retrieved ${log.top_chunks.length} chunks with vector score: ${log.scores.vector.toFixed(2)}`,
      timestamp: log.timestamp
    });
  });

  // Add generation activities
  store.generations.forEach(gen => {
    activityLog.value.push({
      type: 'generation',
      title: `Response Generated: "${gen.query}"`,
      description: `Response generated using ${gen.used_chunks.length} chunks`,
      timestamp: gen.created_at
    });
  });

  // Sort by timestamp, newest first
  activityLog.value.sort((a, b) => {
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });
};

const getFirstDocumentTime = () => {
  if (store.files.length === 0) return new Date().toISOString();

  // Find oldest file
  return store.files.reduce((oldest, file) => {
    return new Date(file.created_at) < new Date(oldest) ? file.created_at : oldest;
  }, store.files[0].created_at);
};

const formatTimeDifference = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays > 0) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  }

  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  if (diffHours > 0) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  }

  const diffMins = Math.floor(diffMs / (1000 * 60));
  if (diffMins > 0) {
    return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  }

  return 'Just now';
};

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

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

const getCurrentTime = () => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date());
};
</script>