import { createRouter, createWebHistory } from 'vue-router';

// Import view components (we'll create these placeholders next)
import ChunkEngineView from '../views/ChunkEngineView.vue';
import EmbeddingLabView from '../views/EmbeddingLabView.vue';
import FileLoaderView from '../views/FileLoaderView.vue';
import GeneratorHubView from '../views/GeneratorHubView.vue';
import ParserStudioView from '../views/ParserStudioView.vue';
import PipelineMonitorView from '../views/PipelineMonitorView.vue';
import SearchConsoleView from '../views/SearchConsoleView.vue';
import VectorIndexerView from '../views/VectorIndexerView.vue';

const routes = [
  { path: '/', redirect: '/file-loader' }, // Default redirect
  {
    path: '/file-loader',
    name: 'FileLoader',
    component: FileLoaderView
  },
  {
    path: '/chunk-engine',
    name: 'ChunkEngine',
    component: ChunkEngineView
  },
  {
    path: '/parser-studio',
    name: 'ParserStudio',
    component: ParserStudioView
  },
  {
    path: '/embedding-lab',
    name: 'EmbeddingLab',
    component: EmbeddingLabView
  },
  {
    path: '/vector-indexer',
    name: 'VectorIndexer',
    component: VectorIndexerView
  },
  {
    path: '/search-console',
    name: 'SearchConsole',
    component: SearchConsoleView
  },
  {
    path: '/generator-hub',
    name: 'GeneratorHub',
    component: GeneratorHubView
  },
  {
    path: '/pipeline-monitor',
    name: 'PipelineMonitor',
    component: PipelineMonitorView
  },
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(), // Using HTML5 history mode
  routes,
});

export default router;