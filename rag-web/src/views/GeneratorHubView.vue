<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Generator Hub</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Generator Configuration Panel -->
      <div class="lg:col-span-1">
        <div class="card mb-6">
          <h2 class="mb-4 text-lg font-semibold">LLM Configuration</h2>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Model Provider</label>
            <select v-model="modelProvider" class="input w-full">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="llama">Meta Llama</option>
              <option value="mistral">Mistral AI</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Model</label>
            <select v-model="modelName" class="input w-full">
              <template v-if="modelProvider === 'openai'">
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </template>

              <template v-else-if="modelProvider === 'anthropic'">
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="claude-3-haiku">Claude 3 Haiku</option>
              </template>

              <template v-else-if="modelProvider === 'llama'">
                <option value="llama-3-70b">Llama 3 70B</option>
                <option value="llama-3-8b">Llama 3 8B</option>
                <option value="llama-2-70b">Llama 2 70B</option>
              </template>

              <template v-else-if="modelProvider === 'mistral'">
                <option value="mistral-large">Mistral Large</option>
                <option value="mistral-small">Mistral Small</option>
                <option value="mistral-7b">Mistral 7B</option>
              </template>

              <template v-else-if="modelProvider === 'ollama'">
                <option value="llama3">Llama 3</option>
                <option value="mistral">Mistral</option>
                <option value="mixtral">Mixtral</option>
              </template>
            </select>
          </div>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">System Prompt</label>
            <textarea
              v-model="systemPrompt"
              rows="5"
              class="input w-full text-sm"
              placeholder="You are a helpful assistant answering questions based on the provided context..."
            ></textarea>
          </div>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Temperature</label>
            <div class="flex items-center">
              <span class="text-sm mr-2 w-10">{{ temperature.toFixed(1) }}</span>
              <input
                v-model.number="temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                class="w-full"
              />
              <span class="text-sm ml-2 w-24">
                {{ temperature < 0.3 ? 'Precise' : temperature > 0.7 ? 'Creative' : 'Balanced' }}
              </span>
            </div>
          </div>

          <div class="flex space-x-2">
            <button
              @click="saveSettings"
              class="btn flex-1"
            >
              Save Settings
            </button>
            <button
              @click="resetSettings"
              class="btn"
            >
              Reset
            </button>
          </div>
        </div>

        <!-- Context Settings -->
        <div class="card">
          <h2 class="mb-4 text-lg font-semibold">Context Settings</h2>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Context Strategy</label>
            <select v-model="contextStrategy" class="input w-full">
              <option value="recent">Recent Search Results</option>
              <option value="custom">Custom Context</option>
              <option value="hybrid">Hybrid (Search + Custom)</option>
              <option value="none">No Context (Pure LLM)</option>
            </select>
          </div>

          <div class="mb-4" v-if="contextStrategy !== 'none'">
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">Max Context Length</label>
              <span class="text-xs text-gray-500">{{ maxContextLength }} tokens</span>
            </div>
            <input
              v-model.number="maxContextLength"
              type="range"
              min="1000"
              max="16000"
              step="1000"
              class="w-full"
            />
          </div>

          <div v-if="contextStrategy === 'custom' || contextStrategy === 'hybrid'" class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Custom Context</label>
            <textarea
              v-model="customContext"
              rows="4"
              class="input w-full text-sm"
              placeholder="Enter custom context information here..."
            ></textarea>
          </div>

          <div v-if="contextStrategy === 'recent' || contextStrategy === 'hybrid'" class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">Recent Search Results</label>
            <div v-if="!store.latestQueryResult" class="text-sm text-gray-500">
              No recent search results available. Perform a search first.
            </div>
            <div v-else class="text-sm bg-gray-50 p-2 rounded max-h-36 overflow-y-auto">
              <p class="font-medium mb-1">Query: "{{ store.latestQueryResult.query }}"</p>
              <p class="text-xs text-gray-500 mb-2">{{ store.latestQueryResult.retrievedChunks.length }} results available</p>
              <div v-for="(chunk, index) in store.latestQueryResult.retrievedChunks.slice(0, 2)" :key="index" class="mb-1">
                <p class="truncate">{{ chunk.content.substring(0, 100) }}...</p>
              </div>
              <p v-if="store.latestQueryResult.retrievedChunks.length > 2" class="text-xs text-gray-500">
                ...and {{ store.latestQueryResult.retrievedChunks.length - 2 }} more chunks
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Generation Area -->
      <div class="lg:col-span-2">
        <div class="card mb-6">
          <h2 class="mb-4 text-lg font-semibold">Generate Response</h2>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700">User Query</label>
            <textarea
              v-model="userQuery"
              rows="3"
              class="input w-full"
              placeholder="Enter your question here..."
            ></textarea>
          </div>

          <div class="flex justify-between">
            <button
              @click="generate"
              class="btn btn-primary"
              :disabled="isGenerating || !userQuery.trim() || (contextStrategy.includes('recent') && !hasRecentSearchResults)"
            >
              {{ isGenerating ? 'Generating...' : 'Generate Response' }}
            </button>
            <button
              @click="clearGeneration"
              class="btn"
              :disabled="isGenerating"
            >
              Clear
            </button>
          </div>
        </div>

        <!-- Generated Response -->
        <div class="card">
          <div class="border-b mb-4">
            <div class="flex">
              <button
                @click="activeTab = 'response'"
                class="px-4 py-2 font-medium border-b-2 transition-colors"
                :class="activeTab === 'response' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
              >
                Response
              </button>
              <button
                @click="activeTab = 'prompt'"
                class="px-4 py-2 font-medium border-b-2 transition-colors"
                :class="activeTab === 'prompt' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
              >
                Prompt Details
              </button>
              <button
                @click="activeTab = 'history'"
                class="px-4 py-2 font-medium border-b-2 transition-colors"
                :class="activeTab === 'history' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
              >
                Generation History
              </button>
            </div>
          </div>

          <!-- Response Tab -->
          <div v-if="activeTab === 'response'" class="h-[calc(100vh-320px)] overflow-y-auto">
            <div v-if="!generatedResponse" class="text-center text-gray-500 py-12">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
              </svg>
              <p class="mt-2">No response generated yet. Enter a query and click "Generate Response".</p>
            </div>

            <div v-else>
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-medium">Response</h3>
                <div class="flex space-x-2">
                  <button
                    @click="copyResponse"
                    class="text-xs bg-gray-100 px-3 py-1 rounded hover:bg-gray-200"
                    title="Copy to clipboard"
                  >
                    Copy
                  </button>
                  <button
                    @click="regenerateResponse"
                    class="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded hover:bg-blue-100"
                    :disabled="isGenerating"
                    title="Regenerate with the same settings"
                  >
                    Regenerate
                  </button>
                </div>
              </div>

              <div class="bg-green-50 border border-green-100 rounded p-4 whitespace-pre-line">
                {{ generatedResponse }}
              </div>

              <div v-if="generationMetadata" class="mt-4 text-xs text-gray-500">
                Generated with {{ generationMetadata.model }} in {{ generationMetadata.time }}ms •
                {{ formatDate(generationMetadata.timestamp) }}
              </div>
            </div>
          </div>

          <!-- Prompt Details Tab -->
          <div v-if="activeTab === 'prompt'" class="h-[calc(100vh-320px)] overflow-y-auto">
            <div v-if="!lastPrompt" class="text-center text-gray-500 py-12">
              <p>No prompt data available. Generate a response first.</p>
            </div>

            <div v-else>
              <div class="mb-4">
                <h3 class="font-medium mb-2">System Prompt</h3>
                <div class="bg-gray-50 p-3 rounded border text-sm font-mono whitespace-pre-wrap">
                  {{ lastPrompt.system }}
                </div>
              </div>

              <div class="mb-4">
                <h3 class="font-medium mb-2">Context ({{ lastPrompt.contextTokens }} tokens)</h3>
                <div class="bg-gray-50 p-3 rounded border text-sm font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                  {{ lastPrompt.context || "No context was used." }}
                </div>
              </div>

              <div>
                <h3 class="font-medium mb-2">User Query</h3>
                <div class="bg-gray-50 p-3 rounded border text-sm font-mono whitespace-pre-wrap">
                  {{ lastPrompt.query }}
                </div>
              </div>
            </div>
          </div>

          <!-- History Tab -->
          <div v-if="activeTab === 'history'" class="h-[calc(100vh-320px)] overflow-y-auto">
            <div v-if="store.generations.length === 0" class="text-center text-gray-500 py-12">
              <p>No generation history available.</p>
            </div>

            <div v-else>
              <div
                v-for="(gen, index) in sortedGenerations.slice(0, 10)"
                :key="gen.gen_id"
                class="mb-4 p-3 border rounded hover:border-blue-200 cursor-pointer"
                @click="loadFromHistory(gen)"
              >
                <div class="flex justify-between mb-2">
                  <h3 class="font-medium">{{ gen.query }}</h3>
                  <span class="text-xs text-gray-500">{{ formatDate(gen.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-600 truncate">{{ gen.response.substring(0, 150) }}...</p>
                <div class="mt-2 flex">
                  <span class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                    {{ gen.used_chunks.length }} chunks used
                  </span>
                </div>
              </div>

              <div v-if="store.generations.length > 10" class="text-center text-xs text-gray-500">
                Showing 10 most recent generations of {{ store.generations.length }} total
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

// LLM settings
const modelProvider = ref('openai');
const modelName = ref('gpt-4o');
const systemPrompt = ref('You are a helpful assistant. Answer the user\'s question based on the provided context. If the context doesn\'t contain relevant information, say so instead of making up an answer.');
const temperature = ref(0.7);

// Context settings
const contextStrategy = ref('recent');
const maxContextLength = ref(4000);
const customContext = ref('');

// Generation
const userQuery = ref('');
const isGenerating = ref(false);
const generatedResponse = ref('');
const activeTab = ref('response');
const lastPrompt = ref<any>(null);
const generationMetadata = ref<any>(null);

// Computed properties
const hasRecentSearchResults = computed(() => {
  return store.latestQueryResult &&
         store.latestQueryResult.retrievedChunks &&
         store.latestQueryResult.retrievedChunks.length > 0;
});

const sortedGenerations = computed(() => {
  return [...store.generations].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
});

// Methods
const saveSettings = () => {
  // In a real app, this would save settings to local storage or server
  alert('Settings saved successfully');
};

const resetSettings = () => {
  modelProvider.value = 'openai';
  modelName.value = 'gpt-4o';
  systemPrompt.value = 'You are a helpful assistant. Answer the user\'s question based on the provided context. If the context doesn\'t contain relevant information, say so instead of making up an answer.';
  temperature.value = 0.7;
  contextStrategy.value = 'recent';
  maxContextLength.value = 4000;
  customContext.value = '';
};

const generate = () => {
  if (!userQuery.value.trim() || isGenerating.value) return;

  isGenerating.value = true;
  activeTab.value = 'response';

  // Prepare context based on strategy
  let context = '';
  let contextTokens = 0;

  if (contextStrategy.value === 'recent' || contextStrategy.value === 'hybrid') {
    if (store.latestQueryResult && store.latestQueryResult.retrievedChunks.length > 0) {
      context += '### Search Results:\n\n';
      store.latestQueryResult.retrievedChunks.forEach((chunk, index) => {
        context += `[${index + 1}] ${chunk.content}\n\n`;
      });
      // Estimate tokens (rough estimate: 4 chars = 1 token)
      contextTokens += Math.floor(context.length / 4);
    }
  }

  if (contextStrategy.value === 'custom' || contextStrategy.value === 'hybrid') {
    if (customContext.value.trim()) {
      context += contextStrategy.value === 'hybrid' ? '\n### Custom Context:\n\n' : '';
      context += customContext.value.trim() + '\n\n';
      // Estimate additional tokens
      contextTokens += Math.floor(customContext.value.length / 4);
    }
  }

  // Save prompt details for display
  lastPrompt.value = {
    system: systemPrompt.value,
    context: context,
    query: userQuery.value,
    contextTokens: contextTokens
  };

  // Simulate generation delay
  setTimeout(() => {
    // In a real app, this would call an API with the model
    const generateMockResponse = () => {
      if (context) {
        // Return a response that references the context
        return `Based on the provided information, I can answer your question about "${userQuery.value}".\n\nThe key points to consider are:\n\n1. ${context.split('\n')[0]}\n\n2. This relates to your question because it addresses the core concepts you're asking about.\n\n3. To elaborate further, the context explains that this technology works by retrieving relevant information and then using it to generate more accurate responses.\n\nIn conclusion, the answer to your question is that RAG systems combine retrieval of information with generation capabilities to provide more accurate, grounded responses.`;
      } else {
        // No context response
        return `I don't have specific context to answer your question about "${userQuery.value}". However, based on my general knowledge, I can provide some information.\n\nWithout specific context, I can only offer general guidance. If you'd like a more specific answer, consider providing context or performing a search first.`;
      }
    };

    generatedResponse.value = generateMockResponse();
    generationMetadata.value = {
      model: modelName.value,
      time: Math.floor(Math.random() * 2000) + 1000, // Random time between 1-3 seconds
      timestamp: new Date().toISOString()
    };

    // Create a generation record
    const usedChunks = [];
    if (store.latestQueryResult && contextStrategy.value.includes('recent')) {
      usedChunks.push(...store.latestQueryResult.retrievedChunks.map(chunk => chunk.chunk_id));
    }

    const generationRecord = {
      gen_id: `gen_${Date.now()}`,
      query: userQuery.value,
      used_chunks: usedChunks,
      response: generatedResponse.value,
      created_at: new Date().toISOString()
    };

    store.generations.push(generationRecord);
    isGenerating.value = false;
  }, 2000);
};

const clearGeneration = () => {
  userQuery.value = '';
  generatedResponse.value = '';
  lastPrompt.value = null;
  generationMetadata.value = null;
  activeTab.value = 'response';
};

const copyResponse = () => {
  if (!generatedResponse.value) return;

  navigator.clipboard.writeText(generatedResponse.value)
    .catch(err => console.error('Failed to copy response: ', err));
};

const regenerateResponse = () => {
  if (isGenerating.value) return;

  // Keep the same query and regenerate
  generate();
};

const loadFromHistory = (generation: any) => {
  userQuery.value = generation.query;
  generatedResponse.value = generation.response;
  activeTab.value = 'response';

  // Mock metadata
  generationMetadata.value = {
    model: 'Historical Model',
    time: '?',
    timestamp: generation.created_at
  };
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
</script>