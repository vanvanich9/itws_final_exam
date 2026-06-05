<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';
	import { getMe } from '$lib/api/users';
	import { FetchError } from '$lib/api/client';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { validateLogin } from '$lib/validation/auth';

	let email = $state('');
	let password = $state('');
	let errors = $state<Record<string, string>>({});
	let loading = $state(false);

	async function handleSubmit() {
		errors = {};
		const errs = validateLogin(email, password);
		if (Object.keys(errs).length > 0) {
			errors = errs;
			return;
		}

		loading = true;
		try {
			await authStore.login({ email, password });
			const user = await getMe();
			authStore.setUser(user);
			goto('/board');
		} catch (e) {
			if (e instanceof FetchError) {
				errors = { _form: e.message };
			} else {
				const msg = e instanceof Error ? `${e.constructor.name}: ${e.message}` : String(e);
				errors = { _form: `Login failed — ${msg}` };
				console.error('[login] non-FetchError caught:', e);
			}
		} finally {
			loading = false;
		}
	}
</script>

<div class="auth-page">
	<div class="auth-card">
		<div class="auth-card__header">
			<span class="auth-card__logo">◈</span>
			<h1 class="auth-card__title">TaskBoard</h1>
			<p class="auth-card__sub">Sign in to your account</p>
		</div>

		<form
			class="auth-form"
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
		>
			{#if errors._form}
				<div class="auth-form__error" role="alert">{errors._form}</div>
			{/if}

			<Input
				id="email"
				label="Email"
				type="email"
				bind:value={email}
				placeholder="you@example.com"
				autocomplete="email"
				required
				error={errors.email}
			/>

			<Input
				id="password"
				label="Password"
				type="password"
				bind:value={password}
				placeholder="••••••••"
				autocomplete="current-password"
				required
				error={errors.password}
			/>

			<Button type="submit" {loading} class="auth-form__submit">Sign in</Button>
		</form>

		<p class="auth-card__footer">
			Don't have an account? <a href="/register">Sign up</a>
		</p>
	</div>
</div>

<style>
	.auth-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
		padding: 24px;
	}

	.auth-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 40px;
		width: 100%;
		max-width: 400px;
		box-shadow: var(--shadow-sm);
	}

	.auth-card__header {
		text-align: center;
		margin-bottom: 28px;
	}

	.auth-card__logo {
		font-size: 36px;
		color: var(--color-primary);
		display: block;
		margin-bottom: 8px;
	}

	.auth-card__title {
		margin: 0 0 6px;
		font-size: 22px;
		font-weight: 700;
		color: var(--color-text);
	}

	.auth-card__sub {
		margin: 0;
		font-size: 14px;
		color: var(--color-text-muted);
	}

	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.auth-form__error {
		padding: 10px 14px;
		background: var(--color-danger-light);
		border-radius: var(--radius-md);
		color: var(--color-danger);
		font-size: 13px;
	}

	:global(.auth-form__submit) {
		width: 100%;
		justify-content: center;
	}

	.auth-card__footer {
		margin: 20px 0 0;
		text-align: center;
		font-size: 13px;
		color: var(--color-text-muted);
	}
</style>
