// API service for connecting to the backend
import axios, { AxiosError } from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // Adjust to your backend URL
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// File service
export const fileService = {
  /**
   * Upload a file to the backend
   * @param file File to upload
   * @param loadingMethod Method to use for loading the file
   * @returns File information
   */
  async uploadFile(file: File, loadingMethod: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('loading_method', loadingMethod);

    try {
      const response = await api.post('/files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: unknown) {
      const err = error as AxiosError;
      console.error('Error uploading file:', err);
      throw err;
    }
  },

  /**
   * Get all files
   * @param page Page number
   * @param limit Items per page
   * @returns List of files
   */
  async getAllFiles(page = 1, limit = 10) {
    try {
      const response = await api.get(`/files?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error: unknown) {
      const err = error as AxiosError;
      console.error('Error getting files:', err);
      throw err;
    }
  },

  /**
   * Get file details
   * @param fileId File ID
   * @returns File details
   */
  async getFile(fileId: string) {
    try {
      const response = await api.get(`/files/${fileId}`);
      return response.data;
    } catch (error: unknown) {
      const err = error as AxiosError;
      console.error(`Error getting file ${fileId}:`, err);
      throw err;
    }
  },

  /**
   * Delete file
   * @param fileId File ID
   * @returns Success status
   */
  async deleteFile(fileId: string) {
    try {
      const response = await api.delete(`/files/${fileId}`);
      return response.data;
    } catch (error: unknown) {
      const err = error as AxiosError;
      console.error(`Error deleting file ${fileId}:`, err);
      throw err;
    }
  },

  /**
   * Get all supported file types and their loading methods
   * @returns Supported file types and loading methods
   */
  async getSupportedFileTypes() {
    try {
      const response = await api.get('/files/supported-types');
      return response.data;
    } catch (error: unknown) {
      const err = error as AxiosError;
      console.error('Error getting supported file types:', err);
      throw err;
    }
  },

  /**
   * Get available loading methods for a specific file type
   * @param fileType File type (e.g., 'pdf', 'txt')
   * @returns Available loading methods for the file type
   */
  async getLoadingMethodsForFileType(fileType: string) {
    try {
      const response = await api.get(`/files/loading-methods/${fileType}`);
      return response.data;
    } catch (error: unknown) {
      const err = error as AxiosError;
      console.error(`Error getting loading methods for file type ${fileType}:`, err);
      throw err;
    }
  },
};

// Export additional services as needed
export default api;