const PASSWORD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,20}$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(email: string): boolean {
	return EMAIL_PATTERN.test(email.trim());
}

export function isValidPassword(password: string): boolean {
	return PASSWORD_PATTERN.test(password);
}

export type FormErrors = Record<string, string>;

export function validateLogin(email: string, password: string): FormErrors {
	const errors: FormErrors = {};
	if (!email.trim()) errors.email = 'Email is required';
	else if (!isValidEmail(email)) errors.email = 'Enter a valid email address';
	if (!password) errors.password = 'Password is required';
	return errors;
}

export function validateRegister(email: string, password: string, name: string): FormErrors {
	const errors: FormErrors = {};
	if (!email.trim()) errors.email = 'Email is required';
	else if (!isValidEmail(email)) errors.email = 'Enter a valid email address';
	if (!name.trim()) errors.name = 'Name is required';
	if (!password) {
		errors.password = 'Password is required';
	} else if (!isValidPassword(password)) {
		errors.password =
			'Password must be 8–20 characters and include uppercase, lowercase, digit, and special character';
	}
	return errors;
}
