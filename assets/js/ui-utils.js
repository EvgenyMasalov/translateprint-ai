// assets/js/ui-utils.js

export function applyTheme() {
    const isDark = localStorage.getItem('lyricai_theme') === 'dark';
    document.documentElement.classList.toggle('dark', isDark);
}

export function toggleTheme() {
    const current = localStorage.getItem('lyricai_theme');
    localStorage.setItem('lyricai_theme', current === 'dark' ? 'light' : 'dark');
    applyTheme();
}

export function isAuthPage() {
    const path = window.location.pathname.toLowerCase();
    return path.includes('registration.html') || 
           path.endsWith('/registration') || 
           path.endsWith('/registration/');
}

export function showToast(message, type = 'info') {
    // Basic alert fallback for now, could be replaced with a nice UI toast
    console.log(`[${type.toUpperCase()}] ${message}`);
    if (type === 'error') {
        alert(`Error: ${message}`);
    } else {
        alert(message);
    }
}
