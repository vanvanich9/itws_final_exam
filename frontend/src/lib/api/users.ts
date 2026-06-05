import { api } from './client';
import type {
	LoginRequest,
	RegisterRequest,
	SuccessResponse,
	TokenResponse,
	UpdateUserRequest,
	User
} from '$lib/types/user';

export async function register(data: RegisterRequest): Promise<User> {
	return api.post<User>('/api/users/register', data);
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
	return api.post<TokenResponse>('/api/users/login', data);
}

export async function logout(): Promise<SuccessResponse> {
	return api.post<SuccessResponse>('/api/users/logout');
}

export async function refreshTokens(): Promise<TokenResponse> {
	return api.post<TokenResponse>('/api/users/refresh');
}

export async function getMe(): Promise<User> {
	return api.get<User>('/api/users/me');
}

export async function getUserById(userId: string): Promise<User> {
	return api.get<User>(`/api/users/${userId}`);
}

export async function updateUser(userId: string, data: UpdateUserRequest): Promise<User> {
	return api.put<User>(`/api/users/${userId}`, data);
}

export async function deleteUser(userId: string): Promise<User> {
	return api.delete<User>(`/api/users/${userId}`);
}
