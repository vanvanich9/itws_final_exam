import { describe, it, expect } from 'vitest';
import { statusLabel, priorityLabel, typeLabel, formatDate } from '$lib/utils/format';

describe('statusLabel', () => {
	it('returns human-readable labels', () => {
		expect(statusLabel('backlog')).toBe('Backlog');
		expect(statusLabel('in_progress')).toBe('In Progress');
		expect(statusLabel('on_review')).toBe('On Review');
		expect(statusLabel('to_do')).toBe('To Do');
		expect(statusLabel('done')).toBe('Done');
		expect(statusLabel('cancelled')).toBe('Cancelled');
	});
});

describe('priorityLabel', () => {
	it('returns human-readable labels', () => {
		expect(priorityLabel('low')).toBe('Low');
		expect(priorityLabel('medium')).toBe('Medium');
		expect(priorityLabel('high')).toBe('High');
		expect(priorityLabel('critical')).toBe('Critical');
	});
});

describe('typeLabel', () => {
	it('returns human-readable labels', () => {
		expect(typeLabel('feature')).toBe('Feature');
		expect(typeLabel('bug')).toBe('Bug');
		expect(typeLabel('documentation')).toBe('Docs');
		expect(typeLabel('other')).toBe('Other');
	});
});

describe('formatDate', () => {
	it('formats ISO date string', () => {
		const result = formatDate('2026-01-15T12:00:00Z');
		expect(result).toMatch(/Jan/);
		expect(result).toMatch(/2026/);
	});
});
