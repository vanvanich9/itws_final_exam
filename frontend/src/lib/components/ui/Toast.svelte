<script lang="ts">
	import { toastStore } from '$lib/stores/toasts.svelte';
</script>

<div class="toast-stack" aria-live="polite">
	{#each toastStore.toasts as toast (toast.id)}
		<div class="toast toast--{toast.kind}" role="alert">
			<span class="toast__msg">{toast.message}</span>
			<button class="toast__close" aria-label="Dismiss" onclick={() => toastStore.remove(toast.id)}>
				✕
			</button>
		</div>
	{/each}
</div>

<style>
	.toast-stack {
		position: fixed;
		bottom: 24px;
		right: 24px;
		display: flex;
		flex-direction: column;
		gap: 10px;
		z-index: 200;
		max-width: 360px;
	}

	.toast {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		padding: 12px 16px;
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		font-size: 14px;
		animation: slide-in 0.2s ease;
	}

	@keyframes slide-in {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	.toast--success {
		background: var(--color-success-light);
		color: #065f46;
		border-left: 4px solid var(--color-success);
	}

	.toast--error {
		background: var(--color-danger-light);
		color: #991b1b;
		border-left: 4px solid var(--color-danger);
	}

	.toast--info {
		background: var(--color-primary-light);
		color: #3730a3;
		border-left: 4px solid var(--color-primary);
	}

	.toast__msg {
		flex: 1;
	}

	.toast__close {
		background: none;
		border: none;
		font-size: 13px;
		opacity: 0.6;
		cursor: pointer;
		padding: 0 2px;
		line-height: 1;
		color: inherit;
	}
	.toast__close:hover {
		opacity: 1;
	}
</style>
