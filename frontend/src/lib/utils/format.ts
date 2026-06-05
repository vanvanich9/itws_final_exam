import {
	PRIORITY_LABELS,
	STATUS_LABELS,
	TYPE_LABELS,
	type TaskPriority,
	type TaskStatus,
	type TaskType
} from '$lib/types/task';

export function formatDate(iso: string): string {
	return new Date(iso).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

export function formatDateTime(iso: string): string {
	return new Date(iso).toLocaleString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

export function statusLabel(status: TaskStatus): string {
	return STATUS_LABELS[status] ?? status;
}

export function priorityLabel(priority: TaskPriority): string {
	return PRIORITY_LABELS[priority] ?? priority;
}

export function typeLabel(type: TaskType): string {
	return TYPE_LABELS[type] ?? type;
}

export function capitalize(s: string): string {
	return s.charAt(0).toUpperCase() + s.slice(1);
}
