import { test, expect } from '@playwright/test';

const TEST_USER = {
	name: 'E2E Test User',
	email: `e2e_${Date.now()}_${Math.random().toString(36).slice(2, 8)}@test.com`,
	password: 'Test@1234'
};

test.describe('Authentication flows', () => {
	test.describe.configure({ mode: 'serial' });
	test('register page loads', async ({ page }) => {
		await page.goto('/register');
		await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
		await expect(page.getByLabel(/name/i)).toBeVisible();
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/password/i)).toBeVisible();
	});

	test('login page loads', async ({ page }) => {
		await page.goto('/login');
		await expect(page.getByRole('heading', { name: /taskboard/i })).toBeVisible();
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/password/i)).toBeVisible();
	});

	test('shows validation error on empty login', async ({ page }) => {
		await page.goto('/login');
		const email = page.locator('#email');
		await page.getByRole('button', { name: /sign in/i }).click();
		await expect
			.poll(async () => email.evaluate((el) => (el as HTMLInputElement).validationMessage))
			.not.toBe('');
	});

	test('shows error for invalid credentials', async ({ page }) => {
		await page.goto('/login');
		await page.getByLabel(/email/i).fill('nobody@example.com');
		await page.getByLabel(/password/i).fill('WrongPass@1');
		await page.getByRole('button', { name: /sign in/i }).click();
		await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });
	});

	test('register → login → board flow', async ({ page }) => {
		await page.goto('/register');
		await page.locator('#name').fill(TEST_USER.name);
		await page.locator('#email').fill(TEST_USER.email);
		await page.locator('#password').fill(TEST_USER.password);
		await page.getByRole('button', { name: /create account/i }).click();

		// Should redirect to board after registration
		await expect(page).toHaveURL(/\/board/, { timeout: 30000 });
		await expect(page.getByRole('button', { name: /user menu/i })).toBeVisible();
	});

	test('logout redirects to login', async ({ page }) => {
		// First login
		await page.goto('/login');
		await page.locator('#email').fill(TEST_USER.email);
		await page.locator('#password').fill(TEST_USER.password);
		await page.getByRole('button', { name: /sign in/i }).click();
		await expect(page).toHaveURL(/\/board/, { timeout: 10000 });

		// Logout via user menu
		await page.getByRole('button', { name: /user menu/i }).click();
		await page.getByRole('menuitem', { name: /sign out/i }).click();
		await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
	});
});
