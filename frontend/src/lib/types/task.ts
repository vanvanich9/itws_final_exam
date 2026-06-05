export type TaskStatus = 'backlog' | 'to_do' | 'in_progress' | 'on_review' | 'done' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskType = 'feature' | 'bug' | 'documentation' | 'other';

export const TASK_STATUSES: TaskStatus[] = [
	'backlog',
	'to_do',
	'in_progress',
	'on_review',
	'done',
	'cancelled'
];

export const TASK_PRIORITIES: TaskPriority[] = ['low', 'medium', 'high', 'critical'];
export const TASK_TYPES: TaskType[] = ['feature', 'bug', 'documentation', 'other'];

export const STATUS_LABELS: Record<TaskStatus, string> = {
	backlog: 'Backlog',
	to_do: 'To Do',
	in_progress: 'In Progress',
	on_review: 'On Review',
	done: 'Done',
	cancelled: 'Cancelled'
};

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
	low: 'Low',
	medium: 'Medium',
	high: 'High',
	critical: 'Critical'
};

export const TYPE_LABELS: Record<TaskType, string> = {
	feature: 'Feature',
	bug: 'Bug',
	documentation: 'Docs',
	other: 'Other'
};

/** Summary returned by POST /api/tasks/search */
export interface TaskSummary {
	id: string;
	user_id: string;
	title: string;
	status: TaskStatus;
	priority: TaskPriority;
}

/** Full task returned by GET/POST/PUT/DELETE /api/tasks/{id} */
export interface TaskDetail {
	id: string;
	user_id: string;
	title: string;
	description: string | null;
	status: TaskStatus;
	priority: TaskPriority;
	task_type: TaskType;
	pull_request_url: string | null;
	created_at: string;
	updated_at: string;
}

export interface ListTaskResponse {
	count: number;
	finished_within_weeks: number;
	tasks: TaskSummary[];
}

export interface TaskSearchRequest {
	statuses?: TaskStatus[] | null;
	priorities?: TaskPriority[] | null;
	task_types?: TaskType[] | null;
	finished_within_weeks?: number;
}

export interface CreateTaskRequest {
	title: string;
	description?: string | null;
	status?: TaskStatus;
	priority?: TaskPriority;
	task_type?: TaskType;
	pull_request_url?: string | null;
}

export interface UpdateTaskRequest {
	title?: string | null;
	description?: string | null;
	status?: TaskStatus | null;
	priority?: TaskPriority | null;
	task_type?: TaskType | null;
	pull_request_url?: string | null;
}
