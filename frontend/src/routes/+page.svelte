<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';

	$effect(() => {
		if (authStore.isAuthenticated) {
			goto('/board');
		} else {
			goto('/login');
		}
	});
</script>
