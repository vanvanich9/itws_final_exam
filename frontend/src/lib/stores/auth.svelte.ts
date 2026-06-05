import { getAccessToken, setAccessToken } from '$lib/api/client';
import { login as apiLogin, logout as apiLogout } from '$lib/api/users';
import type { LoginRequest } from '$lib/types/user';
import type { User } from '$lib/types/user';

class AuthStore {
	user = $state<User | null>(null);

	get token(): string | null {
		return getAccessToken();
	}

	get isAuthenticated(): boolean {
		return this.user !== null;
	}

	async login(credentials: LoginRequest): Promise<void> {
		const { token } = await apiLogin(credentials);
		setAccessToken(token);
	}

	async logout(): Promise<void> {
		try {
			await apiLogout();
		} finally {
			setAccessToken(null);
			this.user = null;
		}
	}

	setUser(user: User | null): void {
		this.user = user;
	}

	setToken(token: string | null): void {
		setAccessToken(token);
	}
}

export const authStore = new AuthStore();
