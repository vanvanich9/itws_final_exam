<script lang="ts">
	interface Props {
		size?: number;
		color?: string;
	}
	let { size = 24, color = 'var(--color-primary)' }: Props = $props();
</script>

<span
	class="spinner"
	role="status"
	aria-label="Loading"
	style="width:{size}px;height:{size}px;border-color:{color}33;border-top-color:{color}"
></span>

<style>
	.spinner {
		display: inline-block;
		border-width: 2px;
		border-style: solid;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
		flex-shrink: 0;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
