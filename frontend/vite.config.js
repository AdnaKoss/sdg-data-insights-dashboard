import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During `npm run dev`, proxy /api to the FastAPI backend (python run.py,
// port 8000) so the frontend can just call relative "/api/..." URLs in both
// dev and the production build (where FastAPI serves this app's built
// files itself, same-origin).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
