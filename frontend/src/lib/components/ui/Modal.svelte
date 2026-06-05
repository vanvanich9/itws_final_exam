<script lang="ts">
	import { type Snippet } from 'svelte';

	interface Props {
		open: boolean;
		title?: string;
		onclose: () => void;
		children: Snippet;
	}

	let { open, title, onclose, children }: Props = $props();

	function handleBackdrop(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onclose();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div class="backdrop" role="presentation" onclick={handleBackdrop}>
		<div class="modal" role="dialog" aria-modal="true" tabindex="-1">
			{#if title}
				<div class="modal__header">
					<h2 class="modal__title">{title}</h2>
					<button class="modal__close" aria-label="Close" onclick={onclose}>✕</button>
				</div>
			{/if}
			<div class="modal__body">
				{@render children()}
			</div>
		</div>
	</div>
{/if}

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.45);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: 16px;
	}

	.modal {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		width: 100%;
		max-width: 520px;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 20px 24px 0;
	}

	.modal__title {
		margin: 0;
		font-size: 17px;
		font-weight: 600;
		color: var(--color-text);
	}

	.modal__close {
		background: none;
		border: none;
		font-size: 16px;
		color: var(--color-text-muted);
		padding: 4px 8px;
		border-radius: var(--radius-sm);
		cursor: pointer;
		line-height: 1;
	}

	.modal__close:hover {
		background: var(--color-surface-alt);
		color: var(--color-text);
	}

	.modal__body {
		padding: 20px 24px 24px;
	}
</style>
