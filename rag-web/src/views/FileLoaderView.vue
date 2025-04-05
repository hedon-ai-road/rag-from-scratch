<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Load File</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- File Upload Section -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">Upload PDF</h2>
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
            accept=".pdf"
          />
          <button
            @click="openFileSelector"
            class="btn btn-primary"
          >
            Select File
          </button>
        </div>

        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Loading Method</label>
          <select v-model="loadingMethod" class="input w-full">
            <option value="PyMuPDF">PyMuPDF</option>
            <option value="PyPDF">PyPDF</option>
            <option value="Unstructured">Unstructured</option>
            <option value="rust_pdf">Rust PDF Library</option>
          </select>
        </div>

        <div v-if="uploadStatus" class="mt-4 p-3" :class="uploadStatusClass">
          {{ uploadStatus }}
        </div>

        <div class="mt-4">
          <button
            @click="loadFile"
            class="btn btn-primary w-full"
            :disabled="!selectedFile"
          >
            Load File
          </button>
        </div>
      </div>

      <!-- Document Preview & Management Section -->
      <div class="card">
        <div class="border-b mb-4">
          <div class="flex">
            <button
              @click="activeTab = 'preview'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'preview' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Document Preview
            </button>
            <button
              @click="activeTab = 'management'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'management' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Document Management
            </button>
          </div>
        </div>

        <!-- Document Preview Tab -->
        <div v-if="activeTab === 'preview'">
          <div v-if="!selectedDocumentForPreview" class="text-gray-500 text-center py-8">
            Select a document to view its content
          </div>
          <div v-else>
            <h3 class="font-medium text-lg mb-2">{{ selectedDocumentForPreview.file_name }}</h3>
            <div class="bg-gray-100 p-4 rounded-lg h-80 overflow-y-auto">
              <p class="whitespace-pre-line">{{ documentPreviewContent }}</p>
            </div>
          </div>
        </div>

        <!-- Document Management Tab -->
        <div v-if="activeTab === 'management'">
          <div v-if="store.files.length === 0" class="text-gray-500 text-center py-8">
            No documents available. Upload documents first.
          </div>
          <ul v-else class="divide-y">
            <li v-for="file in store.files" :key="file.file_id" class="py-3">
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium">{{ file.file_name }}</p>
                  <p class="text-sm text-gray-500">
                    Size: {{ formatFileSize(file.file_size) }} |
                    Uploaded: {{ formatDate(file.created_at) }} |
                    Method: {{ file.loadingMethod || 'PyMuPDF' }}
                  </p>
                </div>
                <div class="flex space-x-2">
                  <button
                    class="rounded-lg px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
                    @click="previewDocument(file)"
                  >
                    View
                  </button>
                  <button
                    class="rounded-lg px-3 py-1 text-sm text-red-600 hover:bg-red-50"
                    @click="deleteDocument(file)"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- File Processing Pipeline -->
    <div class="mt-6 card">
      <h2 class="mb-4 text-lg font-semibold">Processing Pipeline</h2>
      <div class="flex items-center justify-between">
        <div class="flex space-x-4">
          <div class="text-center">
            <div class="rounded-full bg-green-100 p-3">
              <span class="text-lg font-semibold text-green-600">{{ store.fileCount }}</span>
            </div>
            <p class="mt-1 text-sm">Files</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-blue-100 p-3">
              <span class="text-lg font-semibold text-blue-600">{{ store.chunkCount }}</span>
            </div>
            <p class="mt-1 text-sm">Chunks</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-purple-100 p-3">
              <span class="text-lg font-semibold text-purple-600">{{ store.vectorCount }}</span>
            </div>
            <p class="mt-1 text-sm">Vectors</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-amber-100 p-3">
              <span class="text-lg font-semibold text-amber-600">{{ store.searchCount }}</span>
            </div>
            <p class="mt-1 text-sm">Searches</p>
          </div>
          <div class="text-center">
            <div class="rounded-full bg-red-100 p-3">
              <span class="text-lg font-semibold text-red-600">{{ store.generationCount }}</span>
            </div>
            <p class="mt-1 text-sm">Generations</p>
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
const loadingMethod = ref('PyMuPDF');
const selectedFile = ref<File | null>(null);
const activeTab = ref('preview');
const selectedDocumentForPreview = ref<any>(null);
const documentPreviewContent = ref('');

const uploadStatusClass = computed(() => {
  if (uploadStatus.value.includes('Success')) {
    return 'bg-green-100 text-green-700 rounded';
  } else if (uploadStatus.value.includes('Error') || uploadStatus.value.includes('Failed')) {
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
    const file = files[0];
    if (isPdfFile(file)) {
      selectedFile.value = file;
      uploadStatus.value = `Selected file: ${file.name}`;
    } else {
      uploadStatus.value = 'Error: Only PDF files are supported';
    }
  }
};

// Handle file select from input
const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    if (isPdfFile(file)) {
      selectedFile.value = file;
      uploadStatus.value = `Selected file: ${file.name}`;
    } else {
      uploadStatus.value = 'Error: Only PDF files are supported';
    }
  }
};

const isPdfFile = (file: File): boolean => {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
};

// Process the file
const loadFile = () => {
  if (!selectedFile.value) {
    uploadStatus.value = 'Please select a file first';
    return;
  }

  uploadStatus.value = `Processing file: ${selectedFile.value.name}...`;

  // Check file size (max 50MB)
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (selectedFile.value.size > maxSize) {
    uploadStatus.value = `Error: File too large (${formatFileSize(selectedFile.value.size)}), maximum size is 50MB`;
    return;
  }

  // Mock processing delay
  setTimeout(() => {
    // Add the file to our store with loading method info
    const fileId = store.addFile({
      file_name: selectedFile.value!.name,
      file_size: selectedFile.value!.size,
      storage_path: `./data/original/${Date.now()}_${selectedFile.value!.name}`,
      loadingMethod: loadingMethod.value
    });

    uploadStatus.value = `Success: File ${selectedFile.value!.name} has been loaded using ${loadingMethod.value}`;

    // Clear selected file after successful upload
    selectedFile.value = null;
    if (fileInput.value) {
      fileInput.value.value = '';
    }

    // Switch to management tab
    activeTab.value = 'management';
  }, 1500);
};

// Format file size
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

// Format date
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// Preview document
const previewDocument = (file: any) => {
  selectedDocumentForPreview.value = file;
  activeTab.value = 'preview';

  // Mock document content
  documentPreviewContent.value =
    `This is a preview of the document "${file.file_name}" loaded with ${file.loadingMethod || 'PyMuPDF'}.

    The document contains information about RAG (Retrieval Augmented Generation) systems and how they work to improve AI responses.

    Retrieval Augmented Generation is a technique that combines traditional information retrieval with generative AI to produce more accurate and contextually relevant responses.

    File details:
    - Size: ${formatFileSize(file.file_size)}
    - Uploaded: ${formatDate(file.created_at)}
    - Storage path: ${file.storage_path}
    `;
};

// Delete document
const deleteDocument = (file: any) => {
  if (confirm(`Are you sure you want to delete "${file.file_name}"?`)) {
    store.deleteFile(file.file_id);
    uploadStatus.value = `Success: File "${file.file_name}" has been deleted`;

    // Clear preview if the deleted document was being previewed
    if (selectedDocumentForPreview.value && selectedDocumentForPreview.value.file_id === file.file_id) {
      selectedDocumentForPreview.value = null;
      documentPreviewContent.value = '';
    }
  }
};
</script>