<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import { getTask } from '$lib/api/tasks';
	import { FetchError } from '$lib/api/client';
	import { validateCreateTask, validateUpdateTask } from '$lib/validation/task';
	import type {
		TaskDetail,
		TaskStatus,
		TaskPriority,
		TaskType,
		CreateTaskRequest,
		UpdateTaskRequest
	} from '$lib/types/task';
	import {
		TASK_STATUSES,
		TASK_PRIORITIES,
		TASK_TYPES,
		STATUS_LABELS,
		PRIORITY_LABELS,
		TYPE_LABELS
	} from '$lib/types/task';
	import { priorityLabel, statusLabel, typeLabel, formatDateTime } from '$lib/utils/format';
	import { untrack } from 'svelte';

	interface Props {
		mode: 'create' | 'view';
		initialStatus?: TaskStatus;
		taskId?: string;
		onclose: () => void;
		oncreate?: (data: CreateTaskRequest) => Promise<void>;
		onupdate?: (taskId: string, data: UpdateTaskRequest) => Promise<void>;
		ondelete?: (taskId: string) => Promise<void>;
	}

	let {
		mode,
		initialStatus = 'backlog',
		taskId,
		onclose,
		oncreate,
		onupdate,
		ondelete
	}: Props = $props();

	let editing = $state(false);
	let title = $state('');
	let description = $state('');
	let status = $state<TaskStatus>(untrack(() => initialStatus));
	let priority = $state<TaskPriority>('low');
	let taskType = $state<TaskType>('other');
	let prUrl = $state('');
	let errors = $state<Record<string, string>>({});
	let submitting = $state(false);
	let loadingDetail = $state(false);
	let loadError = $state('');
	let taskDetail = $state<TaskDetail | null>(null);
	let confirmDelete = $state(false);

	const statusOptions = TASK_STATUSES.map((s) => ({ value: s, label: STATUS_LABELS[s] }));
	const priorityOptions = TASK_PRIORITIES.map((p) => ({ value: p, label: PRIORITY_LABELS[p] }));
	const typeOptions = TASK_TYPES.map((t) => ({ value: t, label: TYPE_LABELS[t] }));

	const modalTitle = $derived(
		mode === 'create' ? 'New Task' : editing ? 'Edit task' : (taskDetail?.title ?? 'Task')
	);

	$effect(() => {
		if (mode === 'view' && taskId) {
			editing = false;
			confirmDelete = false;
			loadDetail(taskId);
		}
	});

	function syncFormFromDetail(detail: TaskDetail) {
		title = detail.title;
		description = detail.description ?? '';
		status = detail.status;
		priority = detail.priority;
		taskType = detail.task_type;
		prUrl = detail.pull_request_url ?? '';
	}

	async function loadDetail(id: string) {
		loadingDetail = true;
		loadError = '';
		try {
			const detail = await getTask(id);
			taskDetail = detail;
			syncFormFromDetail(detail);
		} catch (e) {
			loadError = e instanceof Error ? e.message : 'Failed to load task';
		} finally {
			loadingDetail = false;
		}
	}

	function startEditing() {
		if (!taskDetail) return;
		errors = {};
		syncFormFromDetail(taskDetail);
		editing = true;
	}

	function cancelEditing() {
		if (taskDetail) syncFormFromDetail(taskDetail);
		errors = {};
		editing = false;
	}

	async function handleCreateSubmit() {
		errors = {};
		const data: CreateTaskRequest = {
			title: title.trim(),
			description: description.trim() || null,
			status,
			priority,
			task_type: taskType,
			pull_request_url: prUrl.trim() || null
		};
		const errs = validateCreateTask(data);
		if (Object.keys(errs).length > 0) {
			errors = errs;
			return;
		}

		submitting = true;
		try {
			await oncreate?.(data);
			onclose();
		} catch (e) {
			if (e instanceof FetchError && e.apiError.fieldErrors) {
				errors = e.apiError.fieldErrors;
			} else {
				errors = { _form: e instanceof Error ? e.message : 'Failed to create task' };
			}
		} finally {
			submitting = false;
		}
	}

	async function handleUpdateSubmit() {
		if (!taskId) return;

		errors = {};
		const data: UpdateTaskRequest = {
			title: title.trim() || null,
			description: description.trim(),
			status,
			priority,
			task_type: taskType,
			pull_request_url: prUrl.trim()
		};
		const errs = validateUpdateTask(data);
		if (Object.keys(errs).length > 0) {
			errors = errs;
			return;
		}

		submitting = true;
		try {
			await onupdate?.(taskId, data);
			await loadDetail(taskId);
			editing = false;
		} catch (e) {
			if (e instanceof FetchError && e.apiError.fieldErrors) {
				errors = e.apiError.fieldErrors;
			} else {
				errors = { _form: e instanceof Error ? e.message : 'Failed to update task' };
			}
		} finally {
			submitting = false;
		}
	}

	async function handleDelete() {
		if (!taskId) return;
		submitting = true;
		try {
			await ondelete?.(taskId);
			onclose();
		} catch (e) {
			errors = { _form: e instanceof Error ? e.message : 'Failed to delete task' };
			submitting = false;
			confirmDelete = false;
		}
	}
</script>

<Modal open={true} title={modalTitle} {onclose}>
	{#if loadingDetail}
		<div class="modal-loading">Loading…</div>
	{:else if loadError}
		<p class="modal-error">{loadError}</p>
	{:else if mode === 'view' && taskDetail && !editing}
		<div class="task-view">
			<div class="task-view__badges">
				<Badge kind="status" value={taskDetail.status} label={statusLabel(taskDetail.status)} />
				<Badge
					kind="priority"
					value={taskDetail.priority}
					label={priorityLabel(taskDetail.priority)}
				/>
				<Badge kind="type" value={taskDetail.task_type} label={typeLabel(taskDetail.task_type)} />
			</div>

			<dl class="task-view__fields">
				<div class="task-view__field">
					<dt>Status</dt>
					<dd>{statusLabel(taskDetail.status)}</dd>
				</div>
				<div class="task-view__field">
					<dt>Priority</dt>
					<dd>{priorityLabel(taskDetail.priority)}</dd>
				</div>
				<div class="task-view__field">
					<dt>Type</dt>
					<dd>{typeLabel(taskDetail.task_type)}</dd>
				</div>
				<div class="task-view__field task-view__field--full">
					<dt>Description</dt>
					<dd
						class:task-view__empty={!taskDetail.description?.trim()}
						class:task-view__description={!!taskDetail.description?.trim()}
					>
						{taskDetail.description?.trim() ? taskDetail.description : 'No description'}
					</dd>
				</div>
				{#if taskDetail.pull_request_url}
					<div class="task-view__field task-view__field--full">
						<dt>Pull request</dt>
						<dd>
							<a href={taskDetail.pull_request_url} target="_blank" rel="noopener noreferrer">
								{taskDetail.pull_request_url}
							</a>
						</dd>
					</div>
				{/if}
			</dl>

			<p class="task-view__meta">
				Created {formatDateTime(taskDetail.created_at)} · Updated {formatDateTime(
					taskDetail.updated_at
				)}
			</p>

			{#if errors._form}
				<p class="form-error">{errors._form}</p>
			{/if}

			<div class="task-view__actions">
				{#if ondelete}
					{#if !confirmDelete}
						<Button variant="ghost" size="sm" onclick={() => (confirmDelete = true)}>Delete</Button>
					{:else}
						<div class="confirm-delete">
							<span>Delete this task?</span>
							<Button variant="danger" size="sm" loading={submitting} onclick={handleDelete}>
								Yes, delete
							</Button>
							<Button variant="ghost" size="sm" onclick={() => (confirmDelete = false)}
								>Cancel</Button
							>
						</div>
					{/if}
				{/if}
				<div class="task-view__actions-right">
					<Button variant="secondary" onclick={startEditing}>Edit</Button>
				</div>
			</div>
		</div>
	{:else}
		<form
			class="task-form"
			onsubmit={(e) => {
				e.preventDefault();
				if (mode === 'create') handleCreateSubmit();
				else handleUpdateSubmit();
			}}
		>
			{#if errors._form}
				<p class="form-error">{errors._form}</p>
			{/if}

			<Input
				id="task-title"
				label="Title"
				bind:value={title}
				placeholder="Task title…"
				autocomplete="off"
				required
				error={errors.title}
			/>

			<div class="form-row">
				<Select id="task-status" label="Status" bind:value={status} options={statusOptions} />
				<Select
					id="task-priority"
					label="Priority"
					bind:value={priority}
					options={priorityOptions}
				/>
			</div>

			<Select id="task-type" label="Type" bind:value={taskType} options={typeOptions} />

			<div class="form-field">
				<label class="form-label" for="task-desc">Description</label>
				<textarea
					id="task-desc"
					class="form-textarea"
					bind:value={description}
					placeholder="Optional description…"
					rows="3"
				></textarea>
			</div>

			<Input
				id="task-pr"
				label="Pull Request URL"
				bind:value={prUrl}
				placeholder="https://github.com/…"
				error={errors.pull_request_url}
			/>

			{#if taskDetail && mode === 'view' && editing}
				<p class="form-meta">
					Created {formatDateTime(taskDetail.created_at)} · Updated {formatDateTime(
						taskDetail.updated_at
					)}
				</p>
			{/if}

			<div class="form-actions">
				<div class="form-actions__right">
					<Button variant="secondary" onclick={mode === 'view' ? cancelEditing : onclose}>
						Cancel
					</Button>
					<Button type="submit" loading={submitting}>
						{mode === 'create' ? 'Create' : 'Save'}
					</Button>
				</div>
			</div>
		</form>
	{/if}
</Modal>

<style>
	.modal-loading,
	.modal-error {
		text-align: center;
		padding: 24px;
		color: var(--color-text-muted);
	}

	.modal-error {
		color: var(--color-danger);
	}

	.task-view {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.task-view__badges {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}

	.task-view__fields {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 14px 20px;
		margin: 0;
	}

	.task-view__field {
		display: flex;
		flex-direction: column;
		gap: 4px;
		min-width: 0;
	}

	.task-view__field--full {
		grid-column: 1 / -1;
	}

	.task-view__field dt {
		margin: 0;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.4px;
		color: var(--color-text-muted);
	}

	.task-view__field dd {
		margin: 0;
		font-size: 14px;
		color: var(--color-text);
		line-height: 1.5;
		word-break: break-word;
	}

	.task-view__field dd a {
		color: var(--color-primary);
		text-decoration: none;
	}

	.task-view__field dd a:hover {
		text-decoration: underline;
	}

	.task-view__empty {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.task-view__description {
		white-space: pre-wrap;
	}

	.task-view__meta {
		margin: 0;
		font-size: 11px;
		color: var(--color-text-light);
	}

	.task-view__actions {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		padding-top: 4px;
		border-top: 1px solid var(--color-border);
	}

	.task-view__actions-right {
		display: flex;
		gap: 8px;
		margin-left: auto;
	}

	.task-form {
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 12px;
	}

	.form-field {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.form-label {
		font-size: 13px;
		font-weight: 500;
		color: var(--color-text);
	}

	.form-textarea {
		padding: 9px 12px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 14px;
		font-family: inherit;
		color: var(--color-text);
		background: var(--color-surface);
		resize: vertical;
		outline: none;
		transition: border-color 0.15s;
	}

	.form-textarea:focus {
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
	}

	.form-error {
		margin: 0;
		padding: 10px 12px;
		background: var(--color-danger-light);
		border-radius: var(--radius-sm);
		color: var(--color-danger);
		font-size: 13px;
	}

	.form-meta {
		margin: 0;
		font-size: 11px;
		color: var(--color-text-light);
	}

	.form-actions {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 8px;
		margin-top: 4px;
	}

	.form-actions__right {
		display: flex;
		gap: 8px;
	}

	.confirm-delete {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 13px;
		color: var(--color-text-muted);
	}
</style>
