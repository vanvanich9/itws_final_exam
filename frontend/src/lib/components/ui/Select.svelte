<script lang="ts">
	interface Option {
		value: string;
		label: string;
	}

	interface Props {
		id?: string;
		label?: string;
		value?: string;
		options: Option[];
		error?: string;
		required?: boolean;
		disabled?: boolean;
		onchange?: (e: Event) => void;
	}

	let {
		id,
		label,
		value = $bindable(''),
		options,
		error,
		required = false,
		disabled = false,
		onchange
	}: Props = $props();
</script>

<div class="field">
	{#if label}
		<label class="field__label" for={id}>
			{label}{#if required}<span class="field__required">*</span>{/if}
		</label>
	{/if}
	<select
		{id}
		bind:value
		{required}
		{disabled}
		class="field__select"
		class:field__select--error={!!error}
		{onchange}
	>
		{#each options as opt (opt.value)}
			<option value={opt.value}>{opt.label}</option>
		{/each}
	</select>
	{#if error}
		<p class="field__error">{error}</p>
	{/if}
</div>

<style>
	.field {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.field__label {
		font-size: 13px;
		font-weight: 500;
		color: var(--color-text);
	}

	.field__required {
		color: var(--color-danger);
		margin-left: 2px;
	}

	.field__select {
		padding: 9px 12px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 14px;
		color: var(--color-text);
		background: var(--color-surface);
		outline: none;
		cursor: pointer;
		appearance: none;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23718096' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 12px center;
		padding-right: 32px;
		transition: border-color 0.15s;
	}

	.field__select:focus {
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
	}

	.field__select--error {
		border-color: var(--color-danger);
	}

	.field__error {
		margin: 0;
		font-size: 12px;
		color: var(--color-danger);
	}
</style>
