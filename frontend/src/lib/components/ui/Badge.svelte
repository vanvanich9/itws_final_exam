<script lang="ts">
	type BadgeKind = 'priority' | 'type' | 'status';

	interface Props {
		kind: BadgeKind;
		value: string;
		label: string;
	}

	let { kind, value, label }: Props = $props();
</script>

<span class="badge badge--{kind} badge--{kind}-{value}">{label}</span>

<style>
	.badge {
		display: inline-block;
		padding: 2px 7px;
		border-radius: 4px;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.4px;
	}

	/* Status */
	.badge--status-backlog,
	.badge--status-to_do {
		background: #f3f4f6;
		color: #4b5563;
	}
	.badge--status-in_progress {
		background: #dbeafe;
		color: #1d4ed8;
	}
	.badge--status-on_review {
		background: #ede9fe;
		color: #6d28d9;
	}
	.badge--status-done {
		background: #dcfce7;
		color: #15803d;
	}
	.badge--status-cancelled {
		background: #fee2e2;
		color: #b91c1c;
	}

	/* Priority */
	.badge--priority-low {
		background: #f3f4f6;
		color: var(--priority-low);
	}
	.badge--priority-medium {
		background: #dbeafe;
		color: #1d4ed8;
	}
	.badge--priority-high {
		background: #fef3c7;
		color: #b45309;
	}
	.badge--priority-critical {
		background: #fee2e2;
		color: #b91c1c;
	}

	/* Type */
	.badge--type-feature {
		background: #ede9fe;
		color: #6d28d9;
	}
	.badge--type-bug {
		background: #fee2e2;
		color: #b91c1c;
	}
	.badge--type-documentation {
		background: #cffafe;
		color: #0e7490;
	}
	.badge--type-other {
		background: #f3f4f6;
		color: #4b5563;
	}
</style>
