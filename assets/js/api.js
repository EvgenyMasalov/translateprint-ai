// assets/js/api.js
import { isAuthPage } from './ui-utils.js';

const API_BASE = `http://${window.location.hostname}:5678`;

export async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('lyricai_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    
    if (token && token !== 'null' && token !== 'undefined') {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Safe logging
    let bodyLog = '';
    if (options.body) {
        try {
            bodyLog = JSON.parse(options.body);
        } catch (e) {
            bodyLog = options.body;
        }
    }
    console.log(`[API] ${options.method || 'GET'} ${endpoint}`, bodyLog);

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        console.log(`[API] Response: ${response.status}`);

        if (response.status === 401) {
            localStorage.removeItem('lyricai_token');
            const authPage = isAuthPage();
            if (!authPage) {
                window.location.href = 'registration.html';
            }
            // Don't throw for 401 on auth page
            if (authPage) return response;
            throw new Error("Unauthorized");
        }

        return response;
    } catch (err) {
        console.error(`[API] Fetch Error:`, err);
        throw err;
    }
}
