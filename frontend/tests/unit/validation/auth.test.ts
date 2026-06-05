import { describe, it, expect } from 'vitest';
import {
	isValidEmail,
	isValidPassword,
	validateLogin,
	validateRegister
} from '$lib/validation/auth';

describe('isValidEmail', () => {
	it('accepts valid emails', () => {
		expect(isValidEmail('user@example.com')).toBe(true);
		expect(isValidEmail('name+tag@sub.domain.co')).toBe(true);
	});

	it('rejects invalid emails', () => {
		expect(isValidEmail('')).toBe(false);
		expect(isValidEmail('notanemail')).toBe(false);
		expect(isValidEmail('@nodomain')).toBe(false);
		expect(isValidEmail('no@')).toBe(false);
	});
});

describe('isValidPassword', () => {
	it('accepts valid passwords', () => {
		expect(isValidPassword('Secret@123')).toBe(true);
		expect(isValidPassword('MyP@ss1!')).toBe(true);
	});

	it('rejects passwords that are too short', () => {
		expect(isValidPassword('Ab1!')).toBe(false);
	});

	it('rejects passwords that are too long', () => {
		expect(isValidPassword('Abcdefghijk@1234567890')).toBe(false);
	});

	it('rejects passwords missing uppercase', () => {
		expect(isValidPassword('secret@123')).toBe(false);
	});

	it('rejects passwords missing lowercase', () => {
		expect(isValidPassword('SECRET@123')).toBe(false);
	});

	it('rejects passwords missing digit', () => {
		expect(isValidPassword('Secret@abc')).toBe(false);
	});

	it('rejects passwords missing special character', () => {
		expect(isValidPassword('Secret1234')).toBe(false);
	});
});

describe('validateLogin', () => {
	it('returns no errors for valid input', () => {
		const errors = validateLogin('user@example.com', 'anypassword');
		expect(errors).toEqual({});
	});

	it('requires email', () => {
		const errors = validateLogin('', 'pass');
		expect(errors.email).toBeDefined();
	});

	it('requires valid email format', () => {
		const errors = validateLogin('bademail', 'pass');
		expect(errors.email).toBeDefined();
	});

	it('requires password', () => {
		const errors = validateLogin('a@b.com', '');
		expect(errors.password).toBeDefined();
	});
});

describe('validateRegister', () => {
	it('returns no errors for valid input', () => {
		const errors = validateRegister('user@example.com', 'Secret@123', 'Jane');
		expect(errors).toEqual({});
	});

	it('requires name', () => {
		const errors = validateRegister('a@b.com', 'Secret@123', '');
		expect(errors.name).toBeDefined();
	});

	it('requires valid password', () => {
		const errors = validateRegister('a@b.com', 'weak', 'Jane');
		expect(errors.password).toBeDefined();
	});
});
