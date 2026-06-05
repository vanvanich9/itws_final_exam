export interface ApiError {
	status: number;
	message: string;
	fieldErrors?: Record<string, string>;
}

interface ValidationErrorDetail {
	loc: (string | number)[];
	msg: string;
	type: string;
}

export function parseApiError(status: number, body: unknown): ApiError {
	if (typeof body === 'object' && body !== null) {
		const b = body as Record<string, unknown>;

		if (Array.isArray(b.detail)) {
			const details = b.detail as ValidationErrorDetail[];
			const fieldErrors: Record<string, string> = {};
			for (const d of details) {
				const field = d.loc.filter((l) => l !== 'body').join('.');
				fieldErrors[field] = d.msg;
			}
			return { status, message: 'Validation error', fieldErrors };
		}

		if (typeof b.detail === 'string') {
			return { status, message: b.detail };
		}

		if (typeof b.message === 'string') {
			return { status, message: b.message };
		}
	}

	return { status, message: httpStatusMessage(status) };
}

function httpStatusMessage(status: number): string {
	const messages: Record<number, string> = {
		400: 'Bad request',
		401: 'Authentication required',
		403: 'You are not allowed to do that',
		404: 'Not found',
		409: 'Conflict — resource already exists',
		422: 'Validation error',
		500: 'Server error — please try again'
	};
	return messages[status] ?? `Unexpected error (${status})`;
}
