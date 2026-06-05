<script lang="ts">
	interface Props {
		message: string;
		onretry?: () => void;
	}
	let { message, onretry }: Props = $props();
</script>

<div class="banner" role="alert">
	<span class="banner__icon">⚠</span>
	<p class="banner__msg">{message}</p>
	{#if onretry}
		<button class="banner__retry" onclick={onretry}>Retry</button>
	{/if}
</div>

<style>
	.banner {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 12px 16px;
		background: var(--color-danger-light);
		border: 1px solid #fecaca;
		border-radius: var(--radius-md);
		color: #991b1b;
		font-size: 14px;
	}

	.banner__icon {
		font-size: 16px;
		flex-shrink: 0;
	}

	.banner__msg {
		margin: 0;
		flex: 1;
	}

	.banner__retry {
		background: none;
		border: 1px solid #f87171;
		border-radius: var(--radius-sm);
		color: #991b1b;
		font-size: 13px;
		padding: 4px 10px;
		cursor: pointer;
	}

	.banner__retry:hover {
		background: #fee2e2;
	}
</style>
