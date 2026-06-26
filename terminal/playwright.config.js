import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './test',
  testMatch: /.*\.pw\.test\.js$/,
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:8765',
    headless: true,
    viewport: { width: 1280, height: 800 },
    deviceScaleFactor: 1,
  },
  webServer: {
    command: 'python serve.py --port 8765',
    url: 'http://127.0.0.1:8765/',
    reuseExistingServer: true,
    timeout: 10_000,
  },
});
