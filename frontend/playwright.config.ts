import { defineConfig, devices } from "@playwright/test";

// Browser tests against a running stack (Docker Compose locally and in CI). They need no model:
// asking a question without ANTHROPIC_API_KEY is itself one of the checks.
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:8080",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "phone", use: { ...devices["Pixel 7"] } },
  ],
});
