<script lang="ts">
	import Navbar from '$lib/components/layout/Navbar.svelte';
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="board-shell">
	<Navbar />
	<main class="board-main">
		{@render children()}
	</main>
</div>

<style>
	.board-shell {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--color-bg);
	}

	.board-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}
</style>
