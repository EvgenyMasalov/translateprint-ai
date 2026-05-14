// assets/js/auth.js
import { apiFetch } from './api.js';
import { isAuthPage } from './ui-utils.js';

export function saveToken(token) {
    localStorage.setItem('lyricai_token', token);
}

export function getToken() {
    const token = localStorage.getItem('lyricai_token');
    if (!token || token === 'null' || token === 'undefined') return null;
    return token;
}

export function logout() {
    localStorage.removeItem('lyricai_token');
    window.location.href = 'registration.html';
}

export async function checkSession() {
    const authPage = isAuthPage();
    
    if (!getToken()) {
        if (!authPage) {
            window.location.href = 'registration.html';
        }
        return null;
    }
    
    try {
        const response = await apiFetch('/me');
        if (!response.ok) throw new Error("Session invalid");
        return await response.json();
    } catch (error) {
        // Only logout and redirect if we're not already on the auth page
        if (!authPage) {
            logout();
        } else {
            localStorage.removeItem('lyricai_token');
        }
        return null;
    }
}
