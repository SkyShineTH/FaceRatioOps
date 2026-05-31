import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// FastAPI serves the built assets from /static_dist and the SPA shell from "/".
// In dev, proxy the API routes to the locally running uvicorn server on :8000.
const API_TARGET = "http://localhost:8000";
const API_ROUTES = ["/analyze", "/health", "/model-info", "/model/info", "/metrics"];

export default defineConfig({
  base: "/static_dist/",
  plugins: [react()],
  build: {
    outDir: "../app/static_dist",
    emptyOutDir: true,
  },
  server: {
    proxy: Object.fromEntries(
      API_ROUTES.map((route) => [route, { target: API_TARGET, changeOrigin: true }]),
    ),
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    css: true,
  },
});
