import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        // The dev backend runs on 8001 (see README). This must match the
        // `--port` uvicorn is started with, or every /api call is refused.
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },
    },
  },
});
