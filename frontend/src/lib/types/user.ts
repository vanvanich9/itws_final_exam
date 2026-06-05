export interface User {
	id: string;
	email: string;
	name: string;
	created_at: string;
	updated_at: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface RegisterRequest {
	email: string;
	password: string;
	name: string;
}

export interface UpdateUserRequest {
	email?: string | null;
	password?: string | null;
	name?: string | null;
}

export interface TokenResponse {
	token: string;
}

export interface SuccessResponse {
	success: boolean;
}
