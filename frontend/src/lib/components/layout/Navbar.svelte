<script lang="ts">
	import UserMenu from './UserMenu.svelte';
</script>

<header class="navbar">
	<div class="navbar__brand">
		<span class="navbar__logo">◈</span>
		<span class="navbar__name">TaskBoard</span>
	</div>
	<nav class="navbar__right">
		<UserMenu />
	</nav>
</header>

<style>
	.navbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 56px;
		padding: 0 24px;
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
		position: sticky;
		top: 0;
		z-index: 50;
	}

	.navbar__brand {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: 700;
		font-size: 18px;
		color: var(--color-primary);
		user-select: none;
	}

	.navbar__logo {
		font-size: 22px;
	}

	.navbar__name {
		letter-spacing: -0.3px;
	}

	.navbar__right {
		display: flex;
		align-items: center;
		gap: 12px;
	}
</style>
