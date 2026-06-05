import { describe, it, expect } from 'vitest';
import { parseApiError } from '$lib/utils/errors';

describe('parseApiError', () => {
	it('parses a 422 validation error with field errors', () => {
		const body = {
			detail: [
				{ loc: ['body', 'title'], msg: 'Title is required', type: 'missing' },
				{ loc: ['body', 'email'], msg: 'Invalid email', type: 'value_error' }
			]
		};
		const result = parseApiError(422, body);
		expect(result.status).toBe(422);
		expect(result.fieldErrors?.title).toBe('Title is required');
		expect(result.fieldErrors?.email).toBe('Invalid email');
	});

	it('parses a string detail', () => {
		const result = parseApiError(401, { detail: 'Authentication required' });
		expect(result.status).toBe(401);
		expect(result.message).toBe('Authentication required');
	});

	it('falls back to http status message for unknown body', () => {
		const result = parseApiError(404, null);
		expect(result.status).toBe(404);
		expect(result.message).toMatch(/not found/i);
	});

	it('handles 409 conflict', () => {
		const result = parseApiError(409, null);
		expect(result.status).toBe(409);
		expect(result.message).toMatch(/conflict/i);
	});

	it('handles completely unknown status', () => {
		const result = parseApiError(503, null);
		expect(result.status).toBe(503);
		expect(result.message).toMatch(/503/);
	});
});
