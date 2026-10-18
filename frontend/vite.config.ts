import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        // The dev backend runs on 8000. This used to say 8001, which nothing was
        // listening on, so every /api call was refused and the pages rendered as
        // empty rather than reporting an error.
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
