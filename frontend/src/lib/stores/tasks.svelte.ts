import { createTask, deleteTask, searchTasks, updateTask } from '$lib/api/tasks';
import type {
	CreateTaskRequest,
	TaskSearchRequest,
	TaskSummary,
	TaskStatus,
	UpdateTaskRequest
} from '$lib/types/task';

class TasksStore {
	tasks = $state<TaskSummary[]>([]);
	loading = $state(false);
	error = $state<string | null>(null);

	private _filters = $state<TaskSearchRequest>({});

	get filters(): TaskSearchRequest {
		return this._filters;
	}

	setFilters(f: TaskSearchRequest): void {
		this._filters = f;
	}

	async load(filters?: TaskSearchRequest): Promise<void> {
		this.loading = true;
		this.error = null;
		try {
			const result = await searchTasks(filters ?? this._filters);
			this.tasks = result.tasks;
		} catch (e) {
			this.error = e instanceof Error ? e.message : 'Failed to load tasks';
		} finally {
			this.loading = false;
		}
	}

	async create(data: CreateTaskRequest): Promise<void> {
		const task = await createTask(data);
		// Add as summary to list
		this.tasks = [
			...this.tasks,
			{
				id: task.id,
				user_id: task.user_id,
				title: task.title,
				status: task.status,
				priority: task.priority
			}
		];
	}

	async update(taskId: string, data: UpdateTaskRequest): Promise<void> {
		const updated = await updateTask(taskId, data);
		this.tasks = this.tasks.map((t) =>
			t.id === taskId
				? {
						id: updated.id,
						user_id: updated.user_id,
						title: updated.title,
						status: updated.status,
						priority: updated.priority
					}
				: t
		);
	}

	async moveToStatus(taskId: string, status: TaskStatus): Promise<void> {
		// Optimistic update
		const previous = this.tasks.find((t) => t.id === taskId);
		this.tasks = this.tasks.map((t) => (t.id === taskId ? { ...t, status } : t));
		try {
			await updateTask(taskId, { status });
		} catch (e) {
			// Revert on failure
			if (previous) {
				this.tasks = this.tasks.map((t) => (t.id === taskId ? previous : t));
			}
			throw e;
		}
	}

	async remove(taskId: string): Promise<void> {
		await deleteTask(taskId);
		this.tasks = this.tasks.filter((t) => t.id !== taskId);
	}
}

export const tasksStore = new TasksStore();
