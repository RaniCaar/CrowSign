function toggleForms(e) {
    if(e) e.preventDefault();
    document.getElementById('login-form').classList.toggle('d-none');
    document.getElementById('register-form').classList.toggle('d-none');
}

// REGISTER
document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-user').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;
    const errDiv = document.getElementById('reg-error');
    const succDiv = document.getElementById('reg-success');
    
    errDiv.classList.add('d-none');
    succDiv.classList.add('d-none');

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, email, password})
        });
        const data = await res.json();
        if(res.ok) {
            succDiv.textContent = data.message;
            succDiv.classList.remove('d-none');
            setTimeout(() => toggleForms(), 2000);
        } else {
            errDiv.textContent = data.error;
            errDiv.classList.remove('d-none');
        }
    } catch (e) {
        errDiv.textContent = "Error de red";
        errDiv.classList.remove('d-none');
    }
});

// LOGIN
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-pass').value;
    const errDiv = document.getElementById('login-error');
    
    errDiv.classList.add('d-none');

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await res.json();
        if(res.ok) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('username', data.user.username);
            window.location.href = '/perfil';
        } else {
            errDiv.textContent = data.error;
            errDiv.classList.remove('d-none');
        }
    } catch (e) {
        errDiv.textContent = "Error de red";
        errDiv.classList.remove('d-none');
    }
});
