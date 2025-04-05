<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Generator Hub</h1>
    <p class="mb-4">Manage prompts and trace generation process.</p>

    <!-- LLM Configuration -->
    <div class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">生成模型配置</h2>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">模型选择</label>
          <select class="input w-full">
            <option value="mistral-7b">Mistral-7B</option>
            <option value="deepseek-7b">DeepSeek-7B</option>
            <option value="llama-3-8b">Llama-3-8B</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">温度</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value="0.7"
            class="w-full"
          />
          <div class="flex justify-between text-xs text-gray-500">
            <span>确定性 (0.0)</span>
            <span>创造性 (1.0)</span>
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">最大生成长度</label>
          <input
            type="number"
            min="10"
            max="4096"
            step="10"
            value="1024"
            class="input w-full"
          />
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">输出格式</label>
          <select class="input w-full">
            <option value="text">纯文本</option>
            <option value="markdown">Markdown</option>
            <option value="json">JSON</option>
          </select>
        </div>
      </div>

      <div class="mt-4">
        <div class="rounded border border-amber-200 bg-amber-50 p-3 text-amber-800">
          <p class="text-sm">
            <strong>提示:</strong> 在搜索控制台中提交查询将自动触发生成过程，使用此处的配置参数。
          </p>
        </div>
      </div>
    </div>

    <!-- Prompt Template -->
    <div class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">Prompt 模板</h2>

      <div>
        <label class="mb-2 block text-sm font-medium text-gray-700">系统指令</label>
        <textarea
          class="input w-full h-20"
          placeholder="你是一个知识丰富的AI助手..."
        >你是一个知识丰富的AI助手，擅长基于提供的上下文回答问题。只使用上下文中的信息。如果上下文中没有相关信息，请说明你不知道，不要编造信息。</textarea>
      </div>

      <div class="mt-4">
        <label class="mb-2 block text-sm font-medium text-gray-700">用户查询模板</label>
        <textarea
          class="input w-full h-20"
          placeholder="基于以下上下文回答我的问题..."
        >基于以下上下文回答我的问题:

\{\{context\}\}

问题: \{\{query\}\}</textarea>
      </div>
    </div>

    <!-- Generation History -->
    <div class="card">
      <h2 class="mb-4 text-lg font-semibold">生成历史</h2>

      <div v-if="store.generations.length === 0" class="text-gray-500">
        暂无生成记录
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="generation in sortedGenerations"
          :key="generation.gen_id"
          class="rounded border p-4"
        >
          <div class="mb-2 flex items-center justify-between">
            <h3 class="font-medium">查询: {{ generation.query }}</h3>
            <span class="text-sm text-gray-500">{{ formatDate(generation.created_at) }}</span>
          </div>

          <div class="rounded border border-green-100 bg-green-50 p-3 text-sm">
            {{ generation.response }}
          </div>

          <div class="mt-2 text-xs text-gray-500">
            使用的分块: {{ generation.used_chunks.join(', ') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();

// Sort generations by timestamp (newest first)
const sortedGenerations = computed(() => {
  return [...store.generations].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
});

// Format date for display
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>