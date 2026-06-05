<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toastStore } from '$lib/stores/toasts.svelte';
	import ProfileModal from './ProfileModal.svelte';

	let open = $state(false);
	let showProfile = $state(false);

	const initial = $derived(authStore.user?.name?.charAt(0)?.toUpperCase() ?? '?');

	function toggle() {
		open = !open;
	}

	function close() {
		open = false;
	}

	function openProfile() {
		close();
		showProfile = true;
	}

	async function handleLogout() {
		close();
		try {
			await authStore.logout();
			goto('/login');
		} catch {
			toastStore.error('Failed to log out');
		}
	}
</script>

<div class="usermenu">
	<button class="usermenu__trigger" onclick={toggle} aria-label="User menu" aria-expanded={open}>
		<span class="usermenu__avatar">{initial}</span>
		<span class="usermenu__name">{authStore.user?.name ?? ''}</span>
		<span class="usermenu__chevron">{open ? '▴' : '▾'}</span>
	</button>

	{#if open}
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="usermenu__backdrop" onclick={close}></div>
		<div class="usermenu__dropdown" role="menu">
			<div class="usermenu__info">
				<span class="usermenu__info-name">{authStore.user?.name}</span>
				<span class="usermenu__info-email">{authStore.user?.email}</span>
			</div>
			<hr class="usermenu__divider" />
			<button class="usermenu__item" role="menuitem" onclick={openProfile}> ✎ Edit profile </button>
			<button class="usermenu__item usermenu__item--danger" role="menuitem" onclick={handleLogout}>
				Sign out
			</button>
		</div>
	{/if}
</div>

{#if showProfile}
	<ProfileModal onclose={() => (showProfile = false)} />
{/if}

<style>
	.usermenu {
		position: relative;
	}

	.usermenu__trigger {
		display: flex;
		align-items: center;
		gap: 8px;
		background: none;
		border: none;
		padding: 6px 10px;
		border-radius: var(--radius-md);
		cursor: pointer;
		color: var(--color-text);
		font-size: 14px;
		transition: background 0.15s;
	}

	.usermenu__trigger:hover {
		background: var(--color-surface-alt);
	}

	.usermenu__avatar {
		width: 30px;
		height: 30px;
		border-radius: 50%;
		background: var(--color-primary);
		color: #fff;
		font-size: 13px;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.usermenu__name {
		font-weight: 500;
		max-width: 120px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.usermenu__chevron {
		font-size: 10px;
		color: var(--color-text-muted);
	}

	.usermenu__backdrop {
		position: fixed;
		inset: 0;
		z-index: 49;
	}

	.usermenu__dropdown {
		position: absolute;
		top: calc(100% + 6px);
		right: 0;
		min-width: 200px;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		z-index: 50;
		overflow: hidden;
	}

	.usermenu__info {
		padding: 12px 16px;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.usermenu__info-name {
		font-weight: 600;
		font-size: 14px;
		color: var(--color-text);
	}

	.usermenu__info-email {
		font-size: 12px;
		color: var(--color-text-muted);
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.usermenu__divider {
		margin: 0;
		border: none;
		border-top: 1px solid var(--color-border);
	}

	.usermenu__item {
		display: block;
		width: 100%;
		padding: 10px 16px;
		text-align: left;
		background: none;
		border: none;
		font-size: 14px;
		cursor: pointer;
		color: var(--color-text);
		transition: background 0.1s;
	}

	.usermenu__item:hover {
		background: var(--color-surface-alt);
	}

	.usermenu__item--danger {
		color: var(--color-danger);
	}

	.usermenu__item--danger:hover {
		background: var(--color-danger-light);
	}
</style>
