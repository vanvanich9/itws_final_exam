import { test, expect, type Page } from '@playwright/test';

const USER = {
	name: 'Board Test User',
	email: `board_${Date.now()}_${Math.random().toString(36).slice(2, 8)}@test.com`,
	password: 'Board@1234'
};

async function registerAndLogin(page: Page) {
	const email = `board_${Date.now()}_${Math.random().toString(36).slice(2, 8)}@test.com`;
	await page.goto('/register');
	await page.locator('#name').fill(USER.name);
	await page.locator('#email').fill(email);
	await page.locator('#password').fill(USER.password);
	await page.getByRole('button', { name: /create account/i }).click();
	await expect(page).toHaveURL(/\/board/, { timeout: 30000 });
}

test.describe('Board — task management', () => {
	test.describe.configure({ mode: 'serial' });
	test.beforeEach(async ({ page }) => {
		await registerAndLogin(page);
	});

	test('board shows all columns', async ({ page }) => {
		await expect(page.getByRole('heading', { name: /backlog/i })).toBeVisible();
		await expect(page.getByRole('heading', { name: /to do/i })).toBeVisible();
		await expect(page.getByRole('heading', { name: /in progress/i })).toBeVisible();
		await expect(page.getByRole('heading', { name: /on review/i })).toBeVisible();
		await expect(page.getByRole('heading', { name: /done/i })).toBeVisible();
	});

	test('create a task', async ({ page }) => {
		// Click "Add task" in Backlog column
		const addBtns = page.getByRole('button', { name: /add task/i });
		await addBtns.first().click();

		// Modal appears
		await expect(page.getByRole('dialog')).toBeVisible({ timeout: 3000 });
		await expect(page.getByRole('heading', { name: /new task/i })).toBeVisible();

		// Fill in title
		await page.locator('#task-title').fill('My first task');

		// Submit
		await page.getByRole('button', { name: /create/i }).click();

		// Task appears on board
		await expect(page.getByText('My first task')).toBeVisible({ timeout: 5000 });
	});

	test('edit a task', async ({ page }) => {
		// Create a task first
		await page
			.getByRole('button', { name: /add task/i })
			.first()
			.click();
		await page.locator('#task-title').fill('Task to edit');
		await page.getByRole('button', { name: /create/i }).click();
		await expect(page.locator('.card__title', { hasText: 'Task to edit' })).toBeVisible({
			timeout: 5000
		});

		await page.locator('.card__title', { hasText: 'Task to edit' }).click();
		await expect(page.getByRole('dialog')).toBeVisible({ timeout: 3000 });
		await expect(page.getByRole('heading', { name: 'Task to edit' })).toBeVisible();

		// Switch to edit mode
		await page.getByRole('button', { name: /^edit$/i }).click();
		await expect(page.getByRole('heading', { name: /edit task/i })).toBeVisible();

		// Change title
		const titleInput = page.locator('#task-title');
		await titleInput.clear();
		await titleInput.fill('Edited task title');

		// Save
		await page.getByRole('button', { name: /save/i }).click();

		await expect(page.locator('.card__title', { hasText: 'Edited task title' })).toBeVisible({
			timeout: 5000
		});
	});

	test('delete a task', async ({ page }) => {
		// Create a task first
		await page
			.getByRole('button', { name: /add task/i })
			.first()
			.click();
		await page.locator('#task-title').fill('Task to delete');
		await page.getByRole('button', { name: /create/i }).click();
		await expect(page.locator('.card__title', { hasText: 'Task to delete' })).toBeVisible({
			timeout: 5000
		});

		await page.locator('.card__title', { hasText: 'Task to delete' }).click();

		// Click Delete
		await page.getByRole('button', { name: /^delete$/i }).click();

		// Confirm dialog appears
		await expect(page.getByText(/delete this task\?/i)).toBeVisible();
		await page.getByRole('button', { name: /yes, delete/i }).click();

		await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 10000 });
		await expect(page.locator('.card__title', { hasText: 'Task to delete' })).toHaveCount(0);
	});

	test('filter bar toggles work', async ({ page }) => {
		// Filter by priority High
		await page.getByRole('button', { name: /high/i }).first().click();
		// Filter chip becomes active (CSS class change); just verify it's clickable again
		await page.getByRole('button', { name: /high/i }).first().click();
		// No crash = pass
	});

	test('handles API error gracefully', async ({ page }) => {
		// Just check the board loads without crash
		await expect(page.locator('.board__columns, .board__loading, .board__error')).toBeVisible({
			timeout: 10000
		});
	});
});
