<script lang="ts">
	import '../app.css';
	import Toast from '$lib/components/ui/Toast.svelte';
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();
</script>

{@render children()}
<Toast />
