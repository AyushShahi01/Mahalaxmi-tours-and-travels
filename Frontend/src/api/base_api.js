// Use proxy in development, direct URL in production
export const BASE_URL = import.meta.env.DEV 
  ? '' // Empty string will use the proxy configured in vite.config.ts
  : 'https://ayush2234.pythonanywhere.com'
 // http://127.0.0.1:8000
 //'https://ayush2234.pythonanywhere.com'