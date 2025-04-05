import { createRouter, createWebHistory } from 'vue-router';

// Import view components (we'll create these placeholders next)

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/file-loader'
    },
    {
      path: '/file-loader',
      name: 'FileLoader',
      component: () => import('../views/FileLoaderView.vue')
    },
    {
      path: '/chunk-engine',
      name: 'ChunkEngine',
      component: () => import('../views/ChunkEngineView.vue')
    },
    {
      path: '/parser-studio',
      name: 'ParserStudio',
      component: () => import('../views/ParserStudioView.vue')
    },
    {
      path: '/embedding-lab',
      name: 'EmbeddingLab',
      component: () => import('../views/EmbeddingLabView.vue')
    },
    {
      path: '/vector-indexer',
      name: 'VectorIndexer',
      component: () => import('../views/VectorIndexerView.vue')
    },
    {
      path: '/search-console',
      name: 'SearchConsole',
      component: () => import('../views/SearchConsoleView.vue')
    },
    {
      path: '/generator-hub',
      name: 'GeneratorHub',
      component: () => import('../views/GeneratorHubView.vue')
    },
    {
      path: '/pipeline-monitor',
      name: 'PipelineMonitor',
      component: () => import('../views/PipelineMonitorView.vue')
    }
  ]
});

export default router;