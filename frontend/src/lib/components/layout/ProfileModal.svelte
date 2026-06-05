<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { updateUser } from '$lib/api/users';
	import { FetchError } from '$lib/api/client';
	import { toastStore } from '$lib/stores/toasts.svelte';
	import { isValidEmail, isValidPassword } from '$lib/validation/auth';
	import type { FormErrors } from '$lib/validation/auth';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onclose: () => void;
	}

	let { onclose }: Props = $props();

	let name = $state(authStore.user?.name ?? '');
	let email = $state(authStore.user?.email ?? '');
	let password = $state('');
	let confirmPassword = $state('');
	let errors = $state<FormErrors>({});
	let loading = $state(false);

	function validate(): FormErrors {
		const e: FormErrors = {};
		if (!name.trim()) e.name = 'Name is required';
		if (!email.trim()) e.email = 'Email is required';
		else if (!isValidEmail(email)) e.email = 'Enter a valid email address';
		if (password) {
			if (!isValidPassword(password))
				e.password =
					'Password must be 8–20 chars with uppercase, lowercase, digit, and special character';
			else if (password !== confirmPassword) e.confirmPassword = 'Passwords do not match';
		}
		return e;
	}

	async function handleSubmit() {
		errors = {};
		const errs = validate();
		if (Object.keys(errs).length) {
			errors = errs;
			return;
		}

		const user = authStore.user;
		if (!user) return;

		const patch: { name?: string; email?: string; password?: string } = {};
		if (name.trim() !== user.name) patch.name = name.trim();
		if (email.trim() !== user.email) patch.email = email.trim();
		if (password) patch.password = password;

		if (!Object.keys(patch).length) {
			onclose();
			return;
		}

		loading = true;
		try {
			const updated = await updateUser(user.id, patch);
			authStore.setUser(updated);
			toastStore.success('Profile updated');
			onclose();
		} catch (e) {
			if (e instanceof FetchError) {
				if (e.apiError.fieldErrors) {
					errors = e.apiError.fieldErrors;
				} else {
					errors = { _form: e.message };
				}
			} else {
				errors = { _form: 'Update failed. Please try again.' };
			}
		} finally {
			loading = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onclose();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div class="modal-backdrop" onclick={onclose}></div>

<div class="modal" role="dialog" aria-modal="true" aria-labelledby="profile-title">
	<div class="modal__header">
		<h2 class="modal__title" id="profile-title">Edit profile</h2>
		<button class="modal__close" onclick={onclose} aria-label="Close">✕</button>
	</div>

	<form
		class="modal__body"
		onsubmit={(e) => {
			e.preventDefault();
			handleSubmit();
		}}
	>
		{#if errors._form}
			<div class="form-error" role="alert">{errors._form}</div>
		{/if}

		<Input
			id="profile-name"
			label="Name"
			bind:value={name}
			placeholder="Jane Doe"
			autocomplete="name"
			required
			error={errors.name}
		/>

		<Input
			id="profile-email"
			label="Email"
			type="email"
			bind:value={email}
			placeholder="you@example.com"
			autocomplete="email"
			required
			error={errors.email}
		/>

		<div class="section-divider">
			<span>Change password</span>
			<span class="section-divider__hint">Leave blank to keep current</span>
		</div>

		<Input
			id="profile-password"
			label="New password"
			type="password"
			bind:value={password}
			placeholder="Min 8 chars, upper+lower+digit+special"
			autocomplete="new-password"
			error={errors.password}
		/>

		<Input
			id="profile-confirm"
			label="Confirm new password"
			type="password"
			bind:value={confirmPassword}
			placeholder="Repeat new password"
			autocomplete="new-password"
			error={errors.confirmPassword}
		/>

		<div class="modal__actions">
			<Button type="button" variant="ghost" onclick={onclose}>Cancel</Button>
			<Button type="submit" {loading}>Save changes</Button>
		</div>
	</form>
</div>

<style>
	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.4);
		z-index: 100;
	}

	.modal {
		position: fixed;
		top: 50%;
		left: 50%;
		translate: -50% -50%;
		width: 100%;
		max-width: 440px;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		z-index: 101;
		display: flex;
		flex-direction: column;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 18px 24px 14px;
		border-bottom: 1px solid var(--color-border);
	}

	.modal__title {
		margin: 0;
		font-size: 16px;
		font-weight: 700;
		color: var(--color-text);
	}

	.modal__close {
		background: none;
		border: none;
		font-size: 14px;
		cursor: pointer;
		color: var(--color-text-muted);
		padding: 4px 8px;
		border-radius: var(--radius-sm);
	}

	.modal__close:hover {
		background: var(--color-surface-alt);
		color: var(--color-text);
	}

	.modal__body {
		padding: 20px 24px;
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	.form-error {
		padding: 10px 14px;
		background: var(--color-danger-light);
		border-radius: var(--radius-md);
		color: var(--color-danger);
		font-size: 13px;
	}

	.section-divider {
		display: flex;
		align-items: baseline;
		gap: 8px;
		font-size: 12px;
		font-weight: 600;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.5px;
		padding-top: 4px;
		border-top: 1px solid var(--color-border);
		margin-top: 4px;
	}

	.section-divider__hint {
		font-weight: 400;
		text-transform: none;
		letter-spacing: 0;
		color: var(--color-text-muted);
		opacity: 0.7;
	}

	.modal__actions {
		display: flex;
		justify-content: flex-end;
		gap: 8px;
		padding-top: 4px;
	}
</style>
