import { redirect } from '@sveltejs/kit';
import { authStore } from '$lib/stores/auth.svelte';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ parent }) => {
	// Wait for the root layout to finish (getMe / token refresh)
	// before checking authentication state.
	await parent();

	if (!authStore.user) {
		throw redirect(302, '/login');
	}

	return {};
};
