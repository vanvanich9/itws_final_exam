import { describe, it, expect } from 'vitest';
import { validateCreateTask, validateUpdateTask } from '$lib/validation/task';

describe('validateCreateTask', () => {
	it('returns no errors for valid data', () => {
		const errors = validateCreateTask({ title: 'My task' });
		expect(errors).toEqual({});
	});

	it('requires title', () => {
		const errors = validateCreateTask({ title: '' });
		expect(errors.title).toBeDefined();
	});

	it('requires non-whitespace title', () => {
		const errors = validateCreateTask({ title: '   ' });
		expect(errors.title).toBeDefined();
	});

	it('validates pull_request_url format', () => {
		const errors = validateCreateTask({ title: 'Task', pull_request_url: 'not-a-url' });
		expect(errors.pull_request_url).toBeDefined();
	});

	it('accepts valid pull_request_url', () => {
		const errors = validateCreateTask({
			title: 'Task',
			pull_request_url: 'https://github.com/org/repo/pull/1'
		});
		expect(errors.pull_request_url).toBeUndefined();
	});
});

describe('validateUpdateTask', () => {
	it('returns no errors for empty update', () => {
		const errors = validateUpdateTask({});
		expect(errors).toEqual({});
	});

	it('rejects empty string title when title is provided', () => {
		const errors = validateUpdateTask({ title: '' });
		expect(errors.title).toBeDefined();
	});

	it('allows null title', () => {
		const errors = validateUpdateTask({ title: null });
		expect(errors.title).toBeUndefined();
	});
});
