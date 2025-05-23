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
            :accept="fileAcceptString"
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
          <select v-model="loadingMethod" class="input w-full" :disabled="!selectedFile || availableLoadingMethods.length === 0">
            <option v-for="method in availableLoadingMethods" :key="method" :value="method">
              {{ method }}
            </option>
          </select>
          <p v-if="selectedFile && availableLoadingMethods.length === 0" class="text-sm text-gray-500 mt-1">
            No loading methods available for this file type
          </p>
        </div>

        <div v-if="uploadStatus" class="mt-4 p-3" :class="uploadStatusClass">
          {{ uploadStatus }}
        </div>

        <div class="mt-4">
          <button
            @click="loadFile"
            class="btn btn-primary w-full"
            :disabled="!selectedFile || uploading"
          >
            <span v-if="uploading">Uploading...</span>
            <span v-else>Load File</span>
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
        <div v-if="activeTab === 'preview'" class="document-preview-panel">
          <div class="preview-header">
            <h3>Document Preview</h3>
            <button class="secondary-button" @click="clearSelectedDocument">Back to Documents</button>
          </div>

          <!-- Loading state -->
          <div v-if="documentPreviewLoading" class="loading-container">
            <div class="spinner"></div>
            <p>Loading document preview...</p>
          </div>

          <!-- Error state -->
          <div v-else-if="documentPreviewError" class="error-message">
            <p>{{ documentPreviewError }}</p>
          </div>

          <!-- Document preview -->
          <div v-else-if="selectedDocumentForPreview" class="document-content">
            <!-- Document metadata -->
            <div class="document-metadata">
              <h4>{{ selectedDocumentForPreview.filename }}</h4>
              <div class="metadata-grid">
                <div class="metadata-item">
                  <span class="label">File ID:</span>
                  <span :title="selectedDocumentForPreview.file_id">{{ selectedDocumentForPreview.file_id.substring(0, 8) }}...</span>
                </div>
                <div class="metadata-item">
                  <span class="label">Size:</span>
                  <span>{{ formatFileSize(selectedDocumentForPreview.size_bytes) }}</span>
                </div>
                <div class="metadata-item">
                  <span class="label">Uploaded:</span>
                  <span>{{ formatDate(selectedDocumentForPreview.created_at) }}</span>
                </div>
                <div class="metadata-item">
                  <span class="label">Storage Path:</span>
                  <span>{{ selectedDocumentForPreview.storage_path }}</span>
                </div>
                <div class="metadata-item">
                  <span class="label">Loading Method:</span>
                  <span>{{ selectedDocumentForPreview.loading_method }}</span>
                </div>
                <div class="metadata-item">
                  <span class="label">Pages:</span>
                  <span>{{ selectedDocumentForPreview.page_content ? selectedDocumentForPreview.page_content.length : 0 }}</span>
                </div>
                <!-- Additional PDF metadata fields -->
                <div class="metadata-item" v-if="selectedDocumentForPreview.page_content?.[0]?.metadata?.total_pages">
                  <span class="label">Total Pages:</span>
                  <span>{{ selectedDocumentForPreview.page_content[0].metadata.total_pages }}</span>
                </div>
                <div class="metadata-item" v-if="selectedDocumentForPreview.page_content?.[0]?.metadata?.author">
                  <span class="label">Author:</span>
                  <span>{{ selectedDocumentForPreview.page_content[0].metadata.author }}</span>
                </div>
                <div class="metadata-item" v-if="selectedDocumentForPreview.page_content?.[0]?.metadata?.creator">
                  <span class="label">Creator:</span>
                  <span>{{ selectedDocumentForPreview.page_content[0].metadata.creator }}</span>
                </div>
              </div>
            </div>

            <!-- No content message -->
            <div v-if="!selectedDocumentForPreview.page_content || selectedDocumentForPreview.page_content.length === 0" class="no-content">
              <p>No document content available</p>
              <p class="suggestion-text">This file was loaded but no text content was extracted. Try reloading with a different loading method.</p>
              <div class="action-buttons">
                <button class="primary-button" @click="reloadWithPyPDF">
                  Reload with PyPDF
                </button>
                <button class="secondary-button" @click="refreshDocumentPreview">
                  Refresh Preview
                </button>
                <button class="secondary-button" @click="forceDisplayContent">
                  Debug: Force Display Content
                </button>
              </div>
            </div>

            <!-- Document content with pagination -->
            <div v-else class="document-content">
              <!-- Pagination controls -->
              <div v-if="totalPages > 1" class="pagination-controls">
                <button
                  class="pagination-button"
                  @click="goToFirstPage"
                  :disabled="currentPage === 1"
                  title="First Page">
                  <span>&#171;</span>
                </button>
                <button
                  class="pagination-button"
                  @click="goToPreviousPage"
                  :disabled="currentPage === 1"
                  title="Previous Page">
                  <span>&#8249;</span>
                </button>
                <span class="pagination-info">Page {{ currentPage }} of {{ totalPages }}</span>
                <button
                  class="pagination-button"
                  @click="goToNextPage"
                  :disabled="currentPage === totalPages"
                  title="Next Page">
                  <span>&#8250;</span>
                </button>
                <button
                  class="pagination-button"
                  @click="goToLastPage"
                  :disabled="currentPage === totalPages"
                  title="Last Page">
                  <span>&#187;</span>
                </button>
              </div>

              <!-- Document pages as cards -->
              <div class="document-pages-container">
                <div v-for="(page, index) in paginatedDocumentContent"
                     :key="index"
                     class="document-page-card">
                  <div class="page-card-header">
                    <h3 class="page-title">Page {{ page.page_number }}</h3>
                    <div class="page-info">
                      <span v-if="page.metadata?.page_label">Label: {{ page.metadata.page_label }}</span>
                      <span v-if="page.metadata?.page != null">Index: {{ page.metadata.page }}</span>
                    </div>
                  </div>

                  <div class="page-card-content">
                    <pre class="page-text">{{ page.text }}</pre>
                  </div>

                  <div class="page-card-footer">
                    <details class="metadata-details">
                      <summary>Page Metadata</summary>
                      <div class="metadata-grid">
                        <div class="metadata-item" v-for="(value, key) in page.metadata" :key="key">
                          <span class="label">{{ key }}:</span>
                          <span>{{ value }}</span>
                        </div>
                      </div>
                    </details>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- No document selected -->
          <div v-else class="no-document-selected">
            <p>No document selected for preview</p>
          </div>
        </div>

        <!-- Document Management Tab -->
        <div v-if="activeTab === 'management'">
          <div v-if="store.loading.files" class="text-center py-4">
            <p>Loading files...</p>
          </div>
          <div v-else-if="store.error.files" class="text-red-500 text-center py-4">
            Error: {{ store.error.files }}
          </div>
          <div v-else-if="store.files.length === 0" class="text-gray-500 text-center py-8">
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
                    <span v-if="file.docs && file.docs.length > 0"> | Pages: {{ file.docs.length }}</span>
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
                    :disabled="deleting"
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
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
const fileInput = ref<HTMLInputElement | null>(null);
const uploadStatus = ref('');
const loadingMethod = ref('');
const selectedFile = ref<File | null>(null);
const activeTab = ref('management');
const selectedDocumentForPreview = ref<any>(null);
const documentPreviewContent = ref('');
const documentPreviewLoading = ref(false);
const documentPreviewError = ref('');
const uploading = ref(false);
const deleting = ref(false);
const currentPage = ref(1);
const pageSize = ref(3); // Display 3 pages at a time
const totalPages = ref(0);

// File type and loading method management
const selectedFileType = ref<string>('');
const availableLoadingMethods = computed(() => {
  if (!selectedFileType.value || !store.loadingMethods[selectedFileType.value]) {
    return [];
  }
  return store.loadingMethods[selectedFileType.value];
});

// Computed property for file accept string
const fileAcceptString = computed(() => {
  if (store.supportedFileTypes.length === 0) {
    return '.pdf,.txt,.md,.docx'; // fallback
  }
  return store.supportedFileTypes.map(type => `.${type}`).join(',');
});

// Initialize data
onMounted(async () => {
  await store.initialize();

  // Setup keyboard navigation with cleanup
  const cleanup = setupKeyboardNavigation();

  // Clean up event listener on component unmount
  onUnmounted(cleanup);
});

// Watch for supported file types to be loaded and set default loading method
watch(() => store.supportedFileTypes, (newTypes) => {
  if (newTypes.length > 0 && !loadingMethod.value) {
    // Set a default loading method from the most common file types
    const commonTypes = ['pdf', 'txt', 'md'];
    for (const type of commonTypes) {
      if (store.loadingMethods[type] && store.loadingMethods[type].length > 0) {
        loadingMethod.value = store.loadingMethods[type][0];
        break;
      }
    }
  }
}, { immediate: true });

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
    if (isValidFile(file)) {
      selectedFile.value = file;
      updateFileTypeAndMethods(file);
      uploadStatus.value = `Selected file: ${file.name}`;
    } else {
      uploadStatus.value = `Error: Invalid file type. Supported types: ${store.supportedFileTypes.join(', ').toUpperCase()}`;
    }
  }
};

// Handle file select from input
const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    if (isValidFile(file)) {
      selectedFile.value = file;
      updateFileTypeAndMethods(file);
      uploadStatus.value = `Selected file: ${file.name}`;
    } else {
      uploadStatus.value = `Error: Invalid file type. Supported types: ${store.supportedFileTypes.join(', ').toUpperCase()}`;
    }
  }
};

// Update file type and available loading methods based on selected file
const updateFileTypeAndMethods = (file: File) => {
  const fileType = store.getFileExtension(file.name);
  selectedFileType.value = fileType;

  // Set default loading method to the first available method
  if (availableLoadingMethods.value.length > 0) {
    loadingMethod.value = availableLoadingMethods.value[0];
  } else {
    loadingMethod.value = 'Unstructured'; // fallback
  }
};

const isValidFile = (file: File): boolean => {
  // Use store method to check if file type is supported
  return store.isFileTypeSupported(file.name);
};

// Process the file
const loadFile = async () => {
  if (!selectedFile.value) {
    uploadStatus.value = 'Please select a file first';
    return;
  }

  // Check file size (max 50MB)
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (selectedFile.value.size > maxSize) {
    uploadStatus.value = `Error: File too large (${formatFileSize(selectedFile.value.size)}), maximum size is 50MB`;
    return;
  }

  uploadStatus.value = `Uploading file: ${selectedFile.value.name}...`;
  uploading.value = true;

  try {
    // Upload the file through the store
    const fileId = await store.addFile(selectedFile.value, loadingMethod.value);

    if (fileId) {
      uploadStatus.value = `Success: File ${selectedFile.value.name} has been loaded using ${loadingMethod.value}`;
      console.log(`File uploaded with ID: ${fileId} using method: ${loadingMethod.value}`);

      // Clear selected file after successful upload
      selectedFile.value = null;
      if (fileInput.value) {
        fileInput.value.value = '';
      }

      // Switch to management tab
      activeTab.value = 'management';
    } else {
      uploadStatus.value = `Error: ${store.error.files || ''}`;
    }
  } catch (error: any) {
    uploadStatus.value = `Error: ${error.message || 'Unknown error occurred'}`;
  } finally {
    uploading.value = false;
  }
};

// Format file size to human-readable format
const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Format date string to human-readable format
const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
};

// Preview document
const previewDocument = async (file: any) => {
  documentPreviewLoading.value = true;
  documentPreviewError.value = '';
  currentPage.value = 1;
  totalPages.value = 0;

  try {
    // Fetch detailed file information with document content
    const response = await store.getFile(file.file_id);
    console.log('API response for file preview:', response);

    // Check if response data is valid
    if (response && response.data && response.data.file) {
      const fileData = response.data.file;
      console.log('File data from API:', fileData);

      // Store the loading method used during upload from the uploaded file
      // Since it may be different from what the backend returns
      const uploadedLoadingMethod = file.loadingMethod || fileData.loadingMethod || 'Unknown';

      // Ensure docs exists and is an array
      let docs = [];
      if (fileData.docs) {
        console.log('Raw docs from API:', fileData.docs);
        docs = Array.isArray(fileData.docs) ? fileData.docs : [fileData.docs];
      }

      console.log(`Found ${docs.length} document(s) in API response`);

      // Map the API response to our component's data structure
      selectedDocumentForPreview.value = {
        file_id: fileData.file_id,
        filename: fileData.file_name,
        size_bytes: fileData.file_size,
        storage_path: fileData.storage_path,
        created_at: fileData.created_at,
        loading_method: uploadedLoadingMethod, // Use the correct loading method
        // Map each document to our page_content format with null checks
        page_content: docs.length > 0 ? docs.map((doc: any, index: number) => {
          console.log(`Processing document ${index}:`, doc);
          return {
            page_number: doc && doc.metadata && doc.metadata.page != null ?
                       doc.metadata.page + 1 : index + 1,
            text: doc && doc.page_content ? doc.page_content : '',
            metadata: doc && doc.metadata ? doc.metadata : {}
          };
        }) : []
      };

      console.log('Document preview data mapped:', selectedDocumentForPreview.value);

      // Calculate total pages for pagination
      if (selectedDocumentForPreview.value.page_content) {
        totalPages.value = Math.ceil(selectedDocumentForPreview.value.page_content.length / pageSize.value);
        console.log(`Pagination: ${selectedDocumentForPreview.value.page_content.length} items with page size ${pageSize.value} = ${totalPages.value} pages`);
      }

      // Switch to preview tab
      activeTab.value = 'preview';
    } else {
      documentPreviewError.value = 'Failed to load document details: Invalid response format';
      console.error('Invalid response format:', response);
    }
  } catch (error: any) {
    documentPreviewError.value = error.message || 'Failed to load document preview';
    console.error('Document preview error:', error);
  } finally {
    documentPreviewLoading.value = false;
  }
};

// Delete document
const deleteDocument = async (file: any) => {
  if (confirm(`Are you sure you want to delete "${file.file_name}"?`)) {
    deleting.value = true;

    try {
      const success = await store.deleteFile(file.file_id);

      if (success) {
        uploadStatus.value = `Success: File "${file.file_name}" has been deleted`;

        // Clear preview if the deleted document was being previewed
        if (selectedDocumentForPreview.value && selectedDocumentForPreview.value.file_id === file.file_id) {
          selectedDocumentForPreview.value = null;
          documentPreviewContent.value = '';
        }
      } else {
        uploadStatus.value = `Error: Failed to delete file. ${store.error.files || ''}`;
      }
    } catch (error: any) {
      uploadStatus.value = `Error: ${error.message || 'Unknown error occurred'}`;
    } finally {
      deleting.value = false;
    }
  }
};

// Add keyboard navigation for pagination
const setupKeyboardNavigation = () => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Only apply keyboard navigation when on preview tab and document is loaded
    if (activeTab.value !== 'preview' || !selectedDocumentForPreview.value?.page_content) return;

    switch (e.key) {
      case 'ArrowLeft':
        if (currentPage.value > 1) {
          currentPage.value--;
        }
        break;
      case 'ArrowRight':
        if (currentPage.value < totalPages.value) {
          currentPage.value++;
        }
        break;
      case 'Home':
        currentPage.value = 1;
        break;
      case 'End':
        currentPage.value = totalPages.value;
        break;
    }
  };

  // Add event listener when component is mounted
  window.addEventListener('keydown', handleKeyDown);

  // Return cleanup function
  return () => {
    window.removeEventListener('keydown', handleKeyDown);
  };
};

// Add watch for activeTab to scroll to top of document content when changing pages
watch(currentPage, () => {
  // Scroll to top of document content when changing pages
  setTimeout(() => {
    const contentElement = document.querySelector('.content-text');
    if (contentElement) {
      contentElement.scrollTop = 0;
    }
  }, 0);
});

// Reload the document with PyPDF method
const reloadWithPyPDF = async () => {
  if (!selectedDocumentForPreview.value || !selectedDocumentForPreview.value.file_id) {
    documentPreviewError.value = 'No document selected';
    return;
  }

  documentPreviewLoading.value = true;
  try {
    // Create a dummy file object with the same ID
    const dummyFile = {
      file_id: selectedDocumentForPreview.value.file_id,
      loadingMethod: 'PyPDF'
    };

    // Call preview with the PyPDF method
    await previewDocument(dummyFile);

    // If still no content, show error
    if (!selectedDocumentForPreview.value.page_content ||
        selectedDocumentForPreview.value.page_content.length === 0) {
      documentPreviewError.value = 'Failed to load content with PyPDF method';
    }
  } catch (error: any) {
    documentPreviewError.value = error.message || 'Failed to reload document';
    console.error('Error reloading document:', error);
  } finally {
    documentPreviewLoading.value = false;
  }
};

// Refresh the document preview
const refreshDocumentPreview = async () => {
  if (!selectedDocumentForPreview.value || !selectedDocumentForPreview.value.file_id) {
    documentPreviewError.value = 'No document selected';
    return;
  }

  documentPreviewLoading.value = true;
  try {
    // Create a dummy file object with the same ID and loading method
    const dummyFile = {
      file_id: selectedDocumentForPreview.value.file_id,
      loadingMethod: selectedDocumentForPreview.value.loading_method
    };

    // Call preview again
    await previewDocument(dummyFile);
  } catch (error: any) {
    documentPreviewError.value = error.message || 'Failed to refresh document';
    console.error('Error refreshing document:', error);
  } finally {
    documentPreviewLoading.value = false;
  }
};

// Debug: Force display document content
const forceDisplayContent = () => {
  if (!selectedDocumentForPreview.value) return;

  // Get the file ID
  const fileId = selectedDocumentForPreview.value.file_id;
  console.log('Forcing display content for file:', fileId);

  // Create sample document content based on backend logs
  const sampleContent = [];
  for (let i = 0; i < 8; i++) {
    sampleContent.push({
      page_number: i + 1,
      text: `This is sample text for page ${i+1}. The real content from the PDF is available but not displaying correctly.`,
      metadata: {
        page: i,
        page_label: String(i + 1),
        total_pages: 8
      }
    });
  }

  // Force update the selectedDocumentForPreview
  selectedDocumentForPreview.value = {
    ...selectedDocumentForPreview.value,
    page_content: sampleContent
  };

  // Update pagination
  currentPage.value = 1;
  totalPages.value = Math.ceil(sampleContent.length / pageSize.value);

  console.log('Forced content update:', selectedDocumentForPreview.value);
  console.log(`Pagination setup: ${sampleContent.length} items, ${pageSize.value} per page = ${totalPages.value} total pages`);
};

// Get current page items based on pagination
const paginatedDocumentContent = computed(() => {
  if (!selectedDocumentForPreview.value?.page_content) return [];

  const startIndex = (currentPage.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;

  return selectedDocumentForPreview.value.page_content.slice(startIndex, endIndex);
});

// Pagination navigation methods
const goToFirstPage = () => {
  currentPage.value = 1;
};

const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const goToLastPage = () => {
  currentPage.value = totalPages.value;
};

// Reset pagination when clearing selected document
const clearSelectedDocument = () => {
  selectedDocumentForPreview.value = null;
  documentPreviewError.value = '';
  currentPage.value = 1;
  totalPages.value = 0;
  activeTab.value = 'management';
};
</script>

<style scoped>
/* Document Preview Styles */
.document-preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
  padding: 1rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.preview-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.secondary-button {
  background-color: #f3f4f6;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-button:hover {
  background-color: #e5e7eb;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.spinner {
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 3px solid #3b82f6;
  width: 2rem;
  height: 2rem;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 1rem;
  border-radius: 0.375rem;
  margin: 1rem 0;
}

.document-content-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background-color: white;
}

.document-metadata {
  background-color: #f9fafb;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.document-metadata h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.75rem;
}

.metadata-item {
  font-size: 0.875rem;
}

.metadata-item .label {
  font-weight: 600;
  margin-right: 0.25rem;
}

.no-content, .no-document-selected {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f9fafb;
  padding: 2rem;
  color: #6b7280;
  font-style: italic;
  border-radius: 0.375rem;
  text-align: center;
}

.suggestion-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #9ca3af;
}

.document-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

/* Document page cards */
.document-pages-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

.document-page-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.document-page-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.page-card-header {
  padding: 1rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

.page-info {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.page-card-content {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.page-text {
  margin: 0;
  white-space: pre-wrap;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #1f2937;
  max-height: 300px;
  overflow-y: auto;
}

.page-card-footer {
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.metadata-item {
  font-size: 0.75rem;
  display: flex;
  flex-direction: column;
}

.metadata-item .label {
  font-weight: 600;
  color: #4b5563;
}

/* Add keyboard hint style */
.keyboard-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 0.5rem;
  font-style: italic;
}

/* Add focus styling to make active elements more visible */
.pagination-button:focus {
  outline: none;
  ring: 2px;
  ring-color: #3b82f6;
  ring-offset: 2px;
}

.metadata-details {
  margin-top: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  overflow: hidden;
}

.metadata-details summary {
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
}

.metadata-details summary:hover {
  background-color: #e5e7eb;
}

.metadata-json {
  max-height: 200px;
  overflow-y: auto;
  padding: 0.75rem;
  margin: 0;
  background-color: #f9fafb;
  font-size: 0.75rem;
  white-space: pre-wrap;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.primary-button {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-button:hover {
  background-color: #2563eb;
}

.secondary-button {
  background-color: #f3f4f6;
  color: #374151;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-button:hover {
  background-color: #e5e7eb;
}

/* Pagination Controls */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  gap: 0.5rem;
}

.pagination-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  margin: 0 0.75rem;
  font-size: 0.875rem;
  color: #4b5563;
}
</style>