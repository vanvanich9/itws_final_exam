import { api } from './client';
import type {
	CreateTaskRequest,
	ListTaskResponse,
	TaskDetail,
	TaskSearchRequest,
	UpdateTaskRequest
} from '$lib/types/task';

export async function searchTasks(filters: TaskSearchRequest = {}): Promise<ListTaskResponse> {
	return api.post<ListTaskResponse>('/api/tasks/search', filters);
}

export async function createTask(data: CreateTaskRequest): Promise<TaskDetail> {
	return api.post<TaskDetail>('/api/tasks', data);
}

export async function getTask(taskId: string): Promise<TaskDetail> {
	return api.get<TaskDetail>(`/api/tasks/${taskId}`);
}

export async function updateTask(taskId: string, data: UpdateTaskRequest): Promise<TaskDetail> {
	return api.put<TaskDetail>(`/api/tasks/${taskId}`, data);
}

export async function deleteTask(taskId: string): Promise<TaskDetail> {
	return api.delete<TaskDetail>(`/api/tasks/${taskId}`);
}
