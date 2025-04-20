import { AxiosError, AxiosResponse } from 'axios'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import api from './services/api'
import './style.css'

// Configure axios interceptors for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    console.error('API Error:', error);
    // You can add global error handling here
    // e.g., show a toast notification or redirect to an error page
    return Promise.reject(error);
  }
);

// Create pinia store
const pinia = createPinia();

// Create and mount app
const app = createApp(App);
app.use(pinia);
app.use(router);
app.mount('#app');
