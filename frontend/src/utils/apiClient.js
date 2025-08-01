import axios from 'axios';

// Get backend URL - works in both development and production
const getBackendURL = () => {
  // In production builds, environment variables are injected at build time
  if (typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // Fallback for production when process is not available
  // Since we're deployed on same domain, use relative paths
  return window.location.origin + '/api';
};

// Create axios instance with backend URL
const apiClient = axios.create({
  baseURL: getBackendURL(),
  timeout: 10000, // 10 second timeout
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth header if token exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout - please check your connection';
    } else if (!error.response) {
      error.message = 'Network error - please check your connection';
      error.code = 'NETWORK_ERROR';
    } else if (error.response.status === 401) {
      // Handle unauthorized - but don't auto-logout here to avoid loops
      error.message = 'Authentication failed';
    } else if (error.response.status >= 500) {
      error.message = 'Server error - please try again';
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;