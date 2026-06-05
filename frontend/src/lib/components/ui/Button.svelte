<script lang="ts">
	type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
	type Size = 'sm' | 'md' | 'lg';

	interface Props {
		variant?: Variant;
		size?: Size;
		loading?: boolean;
		disabled?: boolean;
		type?: 'button' | 'submit' | 'reset';
		class?: string;
		onclick?: (e: MouseEvent) => void;
		children: import('svelte').Snippet;
	}

	let {
		variant = 'primary',
		size = 'md',
		loading = false,
		disabled = false,
		type = 'button',
		class: extraClass = '',
		onclick,
		children
	}: Props = $props();
</script>

<button
	{type}
	class="btn btn--{variant} btn--{size} {extraClass}"
	disabled={disabled || loading}
	{onclick}
>
	{#if loading}
		<span class="btn__spinner"></span>
	{/if}
	{@render children()}
</button>

<style>
	.btn {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-weight: 500;
		border: none;
		border-radius: var(--radius-md);
		cursor: pointer;
		transition:
			background 0.15s,
			opacity 0.15s;
		white-space: nowrap;
	}

	.btn:disabled {
		opacity: 0.55;
		cursor: not-allowed;
	}

	/* variants */
	.btn--primary {
		background: var(--color-primary);
		color: #fff;
	}
	.btn--primary:hover:not(:disabled) {
		background: var(--color-primary-hover);
	}

	.btn--secondary {
		background: var(--color-surface);
		color: var(--color-text);
		border: 1px solid var(--color-border);
	}
	.btn--secondary:hover:not(:disabled) {
		background: var(--color-surface-alt);
	}

	.btn--danger {
		background: var(--color-danger);
		color: #fff;
	}
	.btn--danger:hover:not(:disabled) {
		background: var(--color-danger-hover);
	}

	.btn--ghost {
		background: transparent;
		color: var(--color-text-muted);
		border: none;
	}
	.btn--ghost:hover:not(:disabled) {
		background: var(--color-surface-alt);
		color: var(--color-text);
	}

	/* sizes */
	.btn--sm {
		padding: 4px 10px;
		font-size: 12px;
	}
	.btn--md {
		padding: 8px 16px;
		font-size: 14px;
	}
	.btn--lg {
		padding: 12px 24px;
		font-size: 15px;
	}

	/* spinner */
	.btn__spinner {
		width: 12px;
		height: 12px;
		border: 2px solid rgba(255, 255, 255, 0.4);
		border-top-color: #fff;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
