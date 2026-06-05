import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import { parseApiError, type ApiError } from '$lib/utils/errors';

let _accessToken: string | null = null;
let _refreshPromise: Promise<string | null> | null = null;

export function setAccessToken(token: string | null): void {
	_accessToken = token;
}

export function getAccessToken(): string | null {
	return _accessToken;
}

async function doRefresh(): Promise<string | null> {
	try {
		const res = await fetch(`${env.PUBLIC_API_URL}/api/users/refresh`, {
			method: 'POST',
			credentials: 'include'
		});
		if (!res.ok) return null;
		const data = (await res.json()) as { token: string };
		_accessToken = data.token;
		return data.token;
	} catch {
		return null;
	}
}

async function refreshToken(): Promise<string | null> {
	if (_refreshPromise) return _refreshPromise;
	_refreshPromise = doRefresh().finally(() => {
		_refreshPromise = null;
	});
	return _refreshPromise;
}

export class FetchError extends Error {
	constructor(public readonly apiError: ApiError) {
		super(apiError.message);
	}
}

const AUTH_PATHS = ['/api/users/login', '/api/users/register', '/api/users/refresh'];

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(init.headers as Record<string, string>)
	};

	if (_accessToken) {
		headers['Authorization'] = `Bearer ${_accessToken}`;
	}

	const res = await fetch(`${env.PUBLIC_API_URL}${path}`, {
		...init,
		credentials: 'include',
		headers
	});

	// Only attempt silent token refresh for protected endpoints, not for auth endpoints
	const isAuthPath = AUTH_PATHS.some((p) => path.startsWith(p));
	if (res.status === 401 && retry && browser && !isAuthPath) {
		const newToken = await refreshToken();
		if (newToken) {
			return request<T>(path, init, false);
		} else {
			_accessToken = null;
			throw new FetchError({ status: 401, message: 'Session expired' });
		}
	}

	if (!res.ok) {
		let body: unknown;
		try {
			body = await res.json();
		} catch {
			body = null;
		}
		throw new FetchError(parseApiError(res.status, body));
	}

	if (res.status === 204) return undefined as T;

	return res.json() as Promise<T>;
}

export const api = {
	get: <T>(path: string) => request<T>(path, { method: 'GET' }),
	post: <T>(path: string, body?: unknown) =>
		request<T>(path, {
			method: 'POST',
			body: body !== undefined ? JSON.stringify(body) : undefined
		}),
	put: <T>(path: string, body?: unknown) =>
		request<T>(path, {
			method: 'PUT',
			body: body !== undefined ? JSON.stringify(body) : undefined
		}),
	delete: <T>(path: string) => request<T>(path, { method: 'DELETE' })
};
