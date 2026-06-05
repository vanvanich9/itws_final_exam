<script lang="ts">
	import TaskCard from './TaskCard.svelte';
	import type { TaskSummary, TaskStatus } from '$lib/types/task';

	interface Props {
		status: TaskStatus;
		label: string;
		tasks: TaskSummary[];
		onopen: (taskId: string) => void;
		onadd: (status: TaskStatus) => void;
		ondrop: (taskId: string, toStatus: TaskStatus) => void;
	}

	let { status, label, tasks, onopen, onadd, ondrop }: Props = $props();

	let isDragOver = $state(false);

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
		isDragOver = true;
	}

	function handleDragLeave() {
		isDragOver = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragOver = false;
		const taskId = e.dataTransfer?.getData('text/plain');
		if (taskId) ondrop(taskId, status);
	}
</script>

<div
	class="column"
	class:column--dragover={isDragOver}
	role="region"
	aria-label={label}
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	ondrop={handleDrop}
>
	<div class="column__header">
		<h3 class="column__title">{label}</h3>
		<span class="column__count">{tasks.length}</span>
	</div>

	<div class="column__cards">
		{#each tasks as task (task.id)}
			<TaskCard {task} {onopen} />
		{/each}

		{#if tasks.length === 0}
			<p class="column__empty">No tasks</p>
		{/if}
	</div>

	<button class="column__add" onclick={() => onadd(status)}>
		<span>+</span> Add task
	</button>
</div>

<style>
	.column {
		background: var(--color-surface-alt);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		width: 260px;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		max-height: calc(100vh - 120px);
		transition:
			border-color 0.15s,
			background 0.15s;
	}

	.column--dragover {
		border-color: var(--color-primary);
		background: var(--color-primary-light);
	}

	.column__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 14px 14px 10px;
		flex-shrink: 0;
	}

	.column__title {
		margin: 0;
		font-size: 13px;
		font-weight: 600;
		color: var(--color-text);
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.column__count {
		background: var(--color-border);
		color: var(--color-text-muted);
		font-size: 11px;
		font-weight: 700;
		padding: 1px 6px;
		border-radius: 10px;
	}

	.column__cards {
		flex: 1;
		overflow-y: auto;
		padding: 0 10px;
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-height: 40px;
	}

	.column__empty {
		margin: 0;
		padding: 16px 4px;
		font-size: 13px;
		color: var(--color-text-light);
		text-align: center;
	}

	.column__add {
		margin: 10px;
		padding: 8px;
		border: 1px dashed var(--color-border-hover);
		border-radius: var(--radius-md);
		background: none;
		color: var(--color-text-muted);
		font-size: 13px;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 6px;
		justify-content: center;
		transition:
			background 0.15s,
			color 0.15s;
		flex-shrink: 0;
	}

	.column__add:hover {
		background: var(--color-surface);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}
</style>
