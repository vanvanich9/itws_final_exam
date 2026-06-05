export type ToastKind = 'success' | 'error' | 'info';

export interface Toast {
	id: string;
	kind: ToastKind;
	message: string;
}

class ToastStore {
	toasts = $state<Toast[]>([]);

	private add(kind: ToastKind, message: string, durationMs = 4000): void {
		const id = crypto.randomUUID();
		this.toasts = [...this.toasts, { id, kind, message }];
		setTimeout(() => this.remove(id), durationMs);
	}

	remove(id: string): void {
		this.toasts = this.toasts.filter((t) => t.id !== id);
	}

	success(message: string): void {
		this.add('success', message);
	}

	error(message: string): void {
		this.add('error', message, 6000);
	}

	info(message: string): void {
		this.add('info', message);
	}
}

export const toastStore = new ToastStore();
