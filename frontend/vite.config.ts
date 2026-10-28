import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, `npm run dev` proxies API calls to the running Compose stack.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://localhost:8080" },
  },
});
