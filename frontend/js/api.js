const API_BASE = '/api/v1';

const API = {
    getToken() {
        return localStorage.getItem('access_token');
    },

    async request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const opts = { method, headers };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(`${API_BASE}${path}`, opts);

        if (res.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/static/login.html';
            throw new Error('Sesión expirada');
        }

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const contentType = res.headers.get('content-type');
        if (contentType && contentType.includes('text/csv')) {
            return await res.text();
        }
        return await res.json();
    },

    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    put(path, body) { return this.request('PUT', path, body); },
    delete(path) { return this.request('DELETE', path); },
};

function checkAuth() {
    if (!API.getToken()) {
        window.location.href = '/static/login.html';
        return false;
    }
    return true;
}

document.getElementById('btn-logout')?.addEventListener('click', async () => {
    try {
        const refresh = localStorage.getItem('refresh_token');
        if (refresh) {
            await API.post('/auth/logout', { refresh_token: refresh }).catch(() => {});
        }
    } finally {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/static/login.html';
    }
});

checkAuth();
