import type { Handle } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL ?? 'http://localhost:8000';

/**
 * Proxy all /api/* requests to the backend.
 * This makes every API call same-origin from the browser's perspective,
 * eliminating CORS preflight and SameSite cookie issues entirely.
 */
export const handle: Handle = async ({ event, resolve }) => {
	if (!event.url.pathname.startsWith('/api/')) {
		return resolve(event);
	}

	const target = `${BACKEND_URL}${event.url.pathname}${event.url.search}`;

	const reqHeaders = new Headers(event.request.headers);
	reqHeaders.delete('host');
	reqHeaders.delete('connection');

	const init: RequestInit & { duplex?: string } = {
		method: event.request.method,
		headers: reqHeaders
	};

	if (event.request.method !== 'GET' && event.request.method !== 'HEAD') {
		init.body = event.request.body;
		init.duplex = 'half';
	}

	const upstream = await fetch(target, init);

	const resHeaders = new Headers(upstream.headers);
	// Strip backend CORS headers — client talks to the same origin now
	for (const h of [
		'access-control-allow-origin',
		'access-control-allow-credentials',
		'access-control-allow-methods',
		'access-control-allow-headers',
		'access-control-max-age'
	]) {
		resHeaders.delete(h);
	}

	return new Response(upstream.body, {
		status: upstream.status,
		statusText: upstream.statusText,
		headers: resHeaders
	});
};
