import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 1 : 0,
	workers: process.env.CI ? 1 : undefined,
	webServer: {
		command: 'npm run build && npm run preview -- --port 4173 --host 0.0.0.0',
		port: 4173,
		timeout: 180_000,
		reuseExistingServer: !process.env.CI,
		env: {
			PUBLIC_API_URL: process.env.PUBLIC_API_URL ?? '',
			BACKEND_URL: process.env.BACKEND_URL ?? 'http://localhost:8000',
			ORIGIN: process.env.ORIGIN ?? 'http://localhost:4173'
		}
	},
	testDir: 'tests/e2e',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	use: {
		baseURL: process.env.ORIGIN ?? 'http://localhost:4173'
	}
};

export default config;
