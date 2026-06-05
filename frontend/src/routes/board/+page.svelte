<script lang="ts">
	import { onMount } from 'svelte';
	import BoardColumn from '$lib/components/board/BoardColumn.svelte';
	import FilterBar from '$lib/components/tasks/FilterBar.svelte';
	import TaskModal from '$lib/components/tasks/TaskModal.svelte';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import ErrorBanner from '$lib/components/ui/ErrorBanner.svelte';
	import { tasksStore } from '$lib/stores/tasks.svelte';
	import { toastStore } from '$lib/stores/toasts.svelte';
	import { TASK_STATUSES, STATUS_LABELS } from '$lib/types/task';
	import type {
		TaskStatus,
		TaskSearchRequest,
		CreateTaskRequest,
		UpdateTaskRequest
	} from '$lib/types/task';

	type ModalState =
		| { mode: 'closed' }
		| { mode: 'create'; initialStatus: TaskStatus }
		| { mode: 'view'; taskId: string };

	let modal = $state<ModalState>({ mode: 'closed' });

	const tasksByStatus = $derived(
		TASK_STATUSES.reduce(
			(acc, s) => {
				acc[s] = tasksStore.tasks.filter((t) => t.status === s);
				return acc;
			},
			{} as Record<TaskStatus, typeof tasksStore.tasks>
		)
	);

	onMount(() => {
		tasksStore.load({ finished_within_weeks: 2 });
	});

	function openCreate(status: TaskStatus) {
		modal = { mode: 'create', initialStatus: status };
	}

	function openTask(taskId: string) {
		modal = { mode: 'view', taskId };
	}

	function closeModal() {
		modal = { mode: 'closed' };
	}

	async function handleCreate(data: CreateTaskRequest) {
		await tasksStore.create(data);
		toastStore.success('Task created');
	}

	async function handleUpdate(taskId: string, data: UpdateTaskRequest) {
		await tasksStore.update(taskId, data);
		await tasksStore.load();
		toastStore.success('Task updated');
	}

	async function handleDelete(taskId: string) {
		await tasksStore.remove(taskId);
		toastStore.success('Task deleted');
	}

	async function handleDrop(taskId: string, toStatus: TaskStatus) {
		const task = tasksStore.tasks.find((t) => t.id === taskId);
		if (!task || task.status === toStatus) return;
		try {
			await tasksStore.moveToStatus(taskId, toStatus);
		} catch (e) {
			toastStore.error(e instanceof Error ? e.message : 'Failed to move task');
		}
	}

	async function handleFilter(filters: TaskSearchRequest) {
		await tasksStore.load(filters);
	}
</script>

<svelte:head>
	<title>Board — TaskBoard</title>
</svelte:head>

<FilterBar onfilter={handleFilter} />

<div class="board">
	{#if tasksStore.loading}
		<div class="board__loading">
			<Spinner size={36} />
		</div>
	{:else if tasksStore.error}
		<div class="board__error">
			<ErrorBanner message={tasksStore.error} onretry={() => tasksStore.load()} />
		</div>
	{:else}
		<div class="board__columns">
			{#each TASK_STATUSES as status (status)}
				<BoardColumn
					{status}
					label={STATUS_LABELS[status]}
					tasks={tasksByStatus[status] ?? []}
					onopen={openTask}
					onadd={openCreate}
					ondrop={handleDrop}
				/>
			{/each}
		</div>
	{/if}
</div>

{#if modal.mode === 'create'}
	<TaskModal
		mode="create"
		initialStatus={modal.initialStatus}
		onclose={closeModal}
		oncreate={handleCreate}
	/>
{:else if modal.mode === 'view'}
	<TaskModal
		mode="view"
		taskId={modal.taskId}
		onclose={closeModal}
		onupdate={handleUpdate}
		ondelete={handleDelete}
	/>
{/if}

<style>
	.board {
		flex: 1;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.board__loading,
	.board__error {
		display: flex;
		align-items: center;
		justify-content: center;
		flex: 1;
		padding: 40px;
	}

	.board__columns {
		display: flex;
		gap: 14px;
		padding: 20px 24px;
		overflow-x: auto;
		height: calc(100vh - 112px);
		align-items: flex-start;
	}
</style>
