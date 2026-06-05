<script lang="ts">
	import type { TaskSearchRequest, TaskPriority, TaskType } from '$lib/types/task';
	import { TASK_PRIORITIES, TASK_TYPES, PRIORITY_LABELS, TYPE_LABELS } from '$lib/types/task';

	interface WeekPreset {
		label: string;
		value: number | null;
	}

	const WEEK_PRESETS: WeekPreset[] = [
		{ label: 'This week', value: 1 },
		{ label: '2 weeks', value: 2 },
		{ label: 'Month', value: 4 },
		{ label: 'Quarter', value: 13 }
	];

	interface Props {
		onfilter: (filters: TaskSearchRequest) => void;
	}

	let { onfilter }: Props = $props();

	let selectedPriorities = $state<TaskPriority[]>([]);
	let selectedTypes = $state<TaskType[]>([]);
	let selectedWeeks = $state<number | null>(2);

	function togglePriority(p: TaskPriority) {
		selectedPriorities = selectedPriorities.includes(p)
			? selectedPriorities.filter((x) => x !== p)
			: [...selectedPriorities, p];
		emit();
	}

	function toggleType(t: TaskType) {
		selectedTypes = selectedTypes.includes(t)
			? selectedTypes.filter((x) => x !== t)
			: [...selectedTypes, t];
		emit();
	}

	function setWeeks(w: number | null) {
		selectedWeeks = selectedWeeks === w ? null : w;
		emit();
	}

	function clearAll() {
		selectedPriorities = [];
		selectedTypes = [];
		selectedWeeks = null;
		emit();
	}

	function emit() {
		const filters: TaskSearchRequest = {
			priorities: selectedPriorities.length ? selectedPriorities : null,
			task_types: selectedTypes.length ? selectedTypes : null
		};
		if (selectedWeeks !== null) {
			filters.finished_within_weeks = selectedWeeks;
		}
		onfilter(filters);
	}

	const hasFilters = $derived(
		selectedPriorities.length > 0 || selectedTypes.length > 0 || selectedWeeks !== null
	);
</script>

<div class="filterbar">
	<span class="filterbar__label">Priority:</span>
	{#each TASK_PRIORITIES as p (p)}
		<button
			class="chip"
			class:chip--active={selectedPriorities.includes(p)}
			onclick={() => togglePriority(p)}
		>
			{PRIORITY_LABELS[p]}
		</button>
	{/each}

	<span class="filterbar__sep">|</span>

	<span class="filterbar__label">Type:</span>
	{#each TASK_TYPES as t (t)}
		<button
			class="chip"
			class:chip--active={selectedTypes.includes(t)}
			onclick={() => toggleType(t)}
		>
			{TYPE_LABELS[t]}
		</button>
	{/each}

	<span class="filterbar__sep">|</span>

	<span class="filterbar__label">Due within:</span>
	{#each WEEK_PRESETS as preset (preset.value)}
		<button
			class="chip"
			class:chip--active={selectedWeeks === preset.value}
			onclick={() => setWeeks(preset.value)}
		>
			{preset.label}
		</button>
	{/each}

	{#if hasFilters}
		<button class="filterbar__clear" onclick={clearAll}>✕ Clear</button>
	{/if}
</div>

<style>
	.filterbar {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 6px;
		padding: 10px 24px;
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
	}

	.filterbar__label {
		font-size: 12px;
		font-weight: 600;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.filterbar__sep {
		color: var(--color-border-hover);
		margin: 0 4px;
	}

	.chip {
		padding: 4px 10px;
		border: 1px solid var(--color-border);
		border-radius: 20px;
		background: var(--color-surface);
		color: var(--color-text-muted);
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s;
	}

	.chip:hover {
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.chip--active {
		background: var(--color-primary);
		border-color: var(--color-primary);
		color: #fff;
	}

	.filterbar__clear {
		margin-left: 6px;
		padding: 4px 10px;
		background: none;
		border: none;
		font-size: 12px;
		color: var(--color-text-muted);
		cursor: pointer;
		border-radius: 4px;
	}

	.filterbar__clear:hover {
		color: var(--color-danger);
		background: var(--color-danger-light);
	}
</style>
