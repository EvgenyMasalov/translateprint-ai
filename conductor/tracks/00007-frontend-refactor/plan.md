# Frontend Modularization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract duplicated JavaScript logic (API fetching, authentication) from HTML files into reusable ES modules to prepare the frontend for incremental scaling.

**Architecture:** We will create an `assets/js` directory. We'll introduce `api.js` (for central HTTP requests with JWT injection) and `auth.js` (for token management and login/logout flows). We will then update `registration.html` to use these modules instead of inline scripts.

**Tech Stack:** HTML5, ES6 Modules (Vanilla JS).

---

### Task 1: Create Core API Utility (`assets/js/api.js`)

**Files:**
- Create: `assets/js/api.js`

- [x] **Step 1: Write the API utility implementation**

```javascript
// assets/js/api.js
const API_BASE = 'http://127.0.0.1:5678';

export async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('lyricai_token');
    const headers = {
        ...(options.headers || {})
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Handle unauthorized globally
        localStorage.removeItem('lyricai_token');
        if (!window.location.pathname.includes('registration.html')) {
            window.location.href = 'registration.html';
        }
        throw new Error("Unauthorized. Please log in again.");
    }

    return response;
}
```

- [x] **Step 2: Commit**

```bash
git add assets/js/api.js
git commit -m "feat(ui): add core api utility"
```

---

### Task 2: Create Auth Utility (`assets/js/auth.js`)

**Files:**
- Create: `assets/js/auth.js`

- [x] **Step 1: Write the Auth utility implementation**

```javascript
// assets/js/auth.js
import { apiFetch } from './api.js';

export function saveToken(token) {
    localStorage.setItem('lyricai_token', token);
}

export function getToken() {
    return localStorage.getItem('lyricai_token');
}

export function logout() {
    localStorage.removeItem('lyricai_token');
    window.location.href = 'registration.html';
}

export async function checkSession() {
    if (!getToken()) {
        if (!window.location.pathname.includes('registration.html')) {
            window.location.href = 'registration.html';
        }
        return null;
    }
    
    try {
        const response = await apiFetch('/me');
        if (!response.ok) throw new Error("Session invalid");
        return await response.json();
    } catch (error) {
        logout();
        return null;
    }
}
```

- [x] **Step 2: Commit**

```bash
git add assets/js/auth.js
git commit -m "feat(ui): add auth utility module"
```

---

### Task 3: Refactor `registration.html`

**Files:**
- Modify: `registration.html` (Script section)

- [x] **Step 1: Replace inline API logic with module imports**

Locate the `<script>` tag at the bottom of `registration.html`. Add `type="module"` and replace the `apiFetch` and form submission logic to use the new modules.

```html
<script type="module">
    import { apiFetch } from './assets/js/api.js';
    import { saveToken } from './assets/js/auth.js';

    // ... Keep the tab switching logic (switchTab) ...
    // Note: Make switchTab global if it's called from HTML attributes (onclick="switchTab(...)")
    window.switchTab = function(tabName) {
        document.getElementById('register-form').classList.add('hidden');
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('tab-register').classList.remove('text-indigo-600', 'border-b-2', 'border-indigo-600');
        document.getElementById('tab-register').classList.add('text-slate-500');
        document.getElementById('tab-login').classList.remove('text-indigo-600', 'border-b-2', 'border-indigo-600');
        document.getElementById('tab-login').classList.add('text-slate-500');

        if (tabName === 'register') {
            document.getElementById('register-form').classList.remove('hidden');
            document.getElementById('tab-register').classList.add('text-indigo-600', 'border-b-2', 'border-indigo-600');
            document.getElementById('tab-register').classList.remove('text-slate-500');
        } else {
            document.getElementById('login-form').classList.remove('hidden');
            document.getElementById('tab-login').classList.add('text-indigo-600', 'border-b-2', 'border-indigo-600');
            document.getElementById('tab-login').classList.remove('text-slate-500');
        }
    };

    // Google Auth
    window.initiateGoogleAuth = function() {
        window.location.href = "http://127.0.0.1:5678/auth/google";
    };

    // Handle Form Submissions
    document.getElementById('submit-btn').addEventListener('click', async () => {
        const isRegister = !document.getElementById('register-form').classList.contains('hidden');
        
        try {
            let response;
            if (isRegister) {
                const data = {
                    first_name: document.getElementById('first_name').value,
                    last_name: document.getElementById('last_name').value,
                    email: document.getElementById('email').value
                };
                response = await apiFetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } else {
                const data = { email: document.getElementById('email').value };
                response = await apiFetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            }

            if (response.ok) {
                const resData = await response.json();
                saveToken(resData.access_token);
                window.location.href = 'index.html';
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Authentication failed");
            }
        } catch (error) {
            alert("Network error: " + error.message);
        }
    });

    // Check Fragment for Google Token
    const hash = window.location.hash;
    if (hash && hash.includes('token=')) {
        const token = hash.split('token=')[1];
        saveToken(token);
        window.location.href = 'index.html';
    }
</script>
```

- [ ] **Step 2: Run E2E Tests to verify**

Run: `npm test --prefix tests-e2e`
Expected: Auth tests pass successfully.

- [ ] **Step 3: Commit**

```bash
git add registration.html
git commit -m "refactor(ui): modularize registration page logic"
```
