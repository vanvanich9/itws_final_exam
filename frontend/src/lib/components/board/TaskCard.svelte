<script lang="ts">
	import Badge from '$lib/components/ui/Badge.svelte';
	import { priorityLabel } from '$lib/utils/format';
	import type { TaskSummary } from '$lib/types/task';

	interface Props {
		task: TaskSummary;
		onopen: (taskId: string) => void;
		ondragstart?: (taskId: string) => void;
	}

	let { task, onopen, ondragstart }: Props = $props();

	function handleDragStart(e: DragEvent) {
		if (e.dataTransfer) {
			e.dataTransfer.effectAllowed = 'move';
			e.dataTransfer.setData('text/plain', task.id);
		}
		ondragstart?.(task.id);
	}
</script>

<div
	class="card"
	role="button"
	tabindex="0"
	draggable="true"
	ondragstart={handleDragStart}
	onclick={() => onopen(task.id)}
	onkeydown={(e) => e.key === 'Enter' && onopen(task.id)}
>
	<p class="card__title">{task.title}</p>
	<div class="card__footer">
		<Badge kind="priority" value={task.priority} label={priorityLabel(task.priority)} />
	</div>
</div>

<style>
	.card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 12px;
		cursor: pointer;
		transition:
			box-shadow 0.15s,
			border-color 0.15s;
		user-select: none;
	}

	.card:hover {
		box-shadow: var(--shadow-sm);
		border-color: var(--color-border-hover);
	}

	.card:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.card__title {
		margin: 0 0 10px;
		font-size: 13px;
		font-weight: 500;
		color: var(--color-text);
		line-height: 1.4;
		word-break: break-word;
	}

	.card__footer {
		display: flex;
		align-items: center;
		gap: 6px;
	}
</style>
