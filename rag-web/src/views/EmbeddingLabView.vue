<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Embedding Lab</h1>
    <p class="mb-4">Choose embedding models and evaluate quality.</p>

    <!-- Embedding Configuration -->
    <div class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">嵌入模型配置</h2>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">模型选择</label>
          <select v-model="store.vectorSettings.model" class="input w-full">
            <option value="BGE-M3">BGE-M3</option>
            <option value="OpenAI-text-embedding-3-small">OpenAI-text-embedding-3-small</option>
            <option value="BERT-base">BERT-base</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">向量维度</label>
          <select v-model="store.vectorSettings.dimensions" class="input w-full">
            <option value="384">384</option>
            <option value="512">512</option>
            <option value="768">768</option>
            <option value="1024">1024</option>
          </select>
        </div>
      </div>

      <div class="mt-4">
        <button class="btn btn-primary">应用配置</button>
      </div>
    </div>

    <!-- Vector Visualization Placeholder -->
    <div class="card mb-6">
      <h2 class="mb-4 text-lg font-semibold">向量可视化 (PCA 降维)</h2>

      <div class="aspect-w-16 aspect-h-9 bg-gray-100 flex items-center justify-center">
        <p class="text-gray-500">3D 可视化区域 - 在实际应用中将显示向量降维图</p>
      </div>
    </div>

    <!-- Vector Data -->
    <div class="card">
      <h2 class="mb-4 text-lg font-semibold">向量数据</h2>

      <div v-if="store.vectors.length === 0" class="text-gray-500">
        暂无向量数据
      </div>

      <div v-else>
        <div class="mb-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">向量 ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分块 ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">文件 ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">预览</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="vector in store.vectors" :key="vector.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ vector.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ vector.chunk_id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ vector.file_id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button
                    @click="viewVector(vector)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    查看
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="text-right text-xs text-gray-500">
          总计 {{ store.vectors.length }} 个向量
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();

const viewVector = (vector: any) => {
  console.log('Viewing vector:', vector);
  // In a real application, this would open a modal or navigate to a detail view
  alert(`向量 ${vector.id} 的详细信息将在此处显示。在实际应用中，这里会展示完整的768维向量以及相关可视化。`);
};
</script>

<style>
.aspect-w-16 {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
}
.aspect-h-9 {
  position: absolute;
  width: 100%;
  height: 100%;
}
</style>