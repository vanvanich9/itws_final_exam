import { browser } from '$app/environment';
import { getMe } from '$lib/api/users';
import { setAccessToken } from '$lib/api/client';
import { authStore } from '$lib/stores/auth.svelte';
import type { LayoutLoad } from './$types';

export const ssr = false;

export const load: LayoutLoad = async () => {
	if (!browser) return {};

	// getMe() already handles 401 internally:
	// 1. Gets 401 → tries cookie refresh → if OK, retries automatically
	// 2. If refresh also fails → throws FetchError → caught here
	try {
		const user = await getMe();
		authStore.setUser(user);
	} catch {
		setAccessToken(null);
		authStore.setUser(null);
	}

	return {};
};
