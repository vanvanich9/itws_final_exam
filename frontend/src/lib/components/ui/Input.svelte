<script lang="ts">
	interface Props {
		id?: string;
		label?: string;
		type?: string;
		value?: string;
		placeholder?: string;
		error?: string;
		required?: boolean;
		disabled?: boolean;
		autocomplete?: import('svelte/elements').HTMLInputAttributes['autocomplete'];
		onchange?: (e: Event) => void;
		oninput?: (e: Event) => void;
	}

	let {
		id,
		label,
		type = 'text',
		value = $bindable(''),
		placeholder,
		error,
		required = false,
		disabled = false,
		autocomplete,
		onchange,
		oninput
	}: Props = $props();
</script>

<div class="field">
	{#if label}
		<label class="field__label" for={id}>
			{label}{#if required}<span class="field__required">*</span>{/if}
		</label>
	{/if}
	<input
		{id}
		{type}
		bind:value
		{placeholder}
		{required}
		{disabled}
		{autocomplete}
		class="field__input"
		class:field__input--error={!!error}
		{onchange}
		{oninput}
	/>
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

	.field__input {
		padding: 9px 12px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 14px;
		color: var(--color-text);
		background: var(--color-surface);
		outline: none;
		transition:
			border-color 0.15s,
			box-shadow 0.15s;
	}

	.field__input:focus {
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
	}

	.field__input--error {
		border-color: var(--color-danger);
	}

	.field__input--error:focus {
		box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
	}

	.field__input:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.field__error {
		margin: 0;
		font-size: 12px;
		color: var(--color-danger);
	}
</style>
