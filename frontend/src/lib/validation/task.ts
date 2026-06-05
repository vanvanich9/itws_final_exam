import type { CreateTaskRequest, UpdateTaskRequest } from '$lib/types/task';

export type TaskErrors = Record<string, string>;

export function validateCreateTask(data: Partial<CreateTaskRequest>): TaskErrors {
	const errors: TaskErrors = {};
	if (!data.title?.trim()) {
		errors.title = 'Title is required';
	}
	if (data.pull_request_url && !isValidUrl(data.pull_request_url)) {
		errors.pull_request_url = 'Enter a valid URL';
	}
	return errors;
}

export function validateUpdateTask(data: Partial<UpdateTaskRequest>): TaskErrors {
	const errors: TaskErrors = {};
	if (data.title !== undefined && data.title !== null && !data.title.trim()) {
		errors.title = 'Title cannot be empty';
	}
	if (data.pull_request_url && !isValidUrl(data.pull_request_url)) {
		errors.pull_request_url = 'Enter a valid URL';
	}
	return errors;
}

function isValidUrl(url: string): boolean {
	try {
		new URL(url);
		return true;
	} catch {
		return false;
	}
}
