import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      '/api': {
        //http://127.0.0.1:8000
        //https://ayush2234.pythonanywhere.com
        target: 'https://ayush2234.pythonanywhere.com',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  base: "/Mahalaxmi-tours-and-travels/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
