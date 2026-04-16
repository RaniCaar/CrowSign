let currentEditField = null;
let viewProfileId = null; 

// Params setup
const urlParams = new URLSearchParams(window.location.search);
viewProfileId = urlParams.get('id') || 'me';

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function openModal(field, title) {
    currentEditField = field;
    document.getElementById('modal-title').textContent = title;
    let currentVal = document.getElementById(`profile-${field}`).textContent;
    if(currentVal === 'No especificado' || currentVal === 'No especificada' || currentVal === 'Sin descripción') currentVal = '';
    const input = document.getElementById('modal-input');
    input.value = currentVal;
    input.type = field === 'age' ? 'number' : 'text';
    document.getElementById('edit-modal').classList.add('active');
    input.focus();
}

function closeModal() {
    document.getElementById('edit-modal').classList.remove('active');
    currentEditField = null;
}

async function saveModalEdit() {
    if(!currentEditField) return;
    let value = document.getElementById('modal-input').value.trim();
    if(currentEditField === 'age') value = parseInt(value) || null;
    try {
        const res = await fetch('/api/profile', { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({[currentEditField]: value}) });
        if(res.ok) { closeModal(); showToast('Perfil actualizado'); loadProfile(); } 
        else showToast('Error al actualizar', 'error');
    } catch (e) { showToast('Error de conexión', 'error'); }
}

async function uploadImage(event, type) {
    const file = event.target.files[0];
    if(!file) return;
    const formData = new FormData(); formData.append('file', file); formData.append('type', type);
    try {
        const res = await fetch('/api/upload_image', { method: 'POST', body: formData });
        const data = await res.json();
        if(res.ok) {
            showToast(data.message, 'success');
            if(type==='avatar') document.getElementById('profile-avatar').src = data.url;
            else document.getElementById('banner-img').style.backgroundImage = `url('${data.url}')`;
        } else showToast(data.error, 'error');
    } catch (e) { showToast('Fallo al subir imagen', 'error'); }
}

async function searchUsers() {
    const q = document.getElementById('search-input').value;
    const resBox = document.getElementById('search-results');
    if(q.length < 1) { resBox.style.display = 'none'; return; }
    
    try {
        const res = await fetch(`/api/users/search?q=${q}`);
        const data = await res.json();
        resBox.innerHTML = '';
        if(data.length > 0) {
            data.forEach(u => {
                resBox.innerHTML += `<div class="search-item" onclick="window.location.href='/perfil?id=${u.id}'">
                    <img src="${u.profile_pic || '/static/img/black_crow.png'}"> <span>${u.username}</span>
                </div>`;
            });
            resBox.style.display = 'block';
        } else {
            resBox.style.display = 'none';
        }
    } catch (e) { }
}

async function loadProfile() {
    try {
        let fetchUrl = viewProfileId === 'me' ? '/api/auth/me' : `/api/profile/${viewProfileId}/details`;
        const res = await fetch(fetchUrl);
        if(!res.ok && viewProfileId === 'me') { window.location.href = '/'; return; }
        if(!res.ok) { showToast('Perfil no encontrado', 'error'); return; }
        
        const data = await res.json();
        viewProfileId = data.id; // Confirm ID
        
        document.getElementById('profile-name').textContent = data.username || 'Usuario';
        document.getElementById('profile-identity').textContent = data.identity || 'No especificado';
        document.getElementById('profile-age').textContent = data.age || 'No especificada';
        document.getElementById('profile-bio').textContent = data.bio || 'Sin descripción';
        document.getElementById('profile-country').textContent = data.country || 'No especificado';
        document.getElementById('followers-count').textContent = data.followers || 0;
        document.getElementById('following-count').textContent = data.following || 0;
        
        if(data.profile_pic && data.profile_pic !== 'default_avatar.png') document.getElementById('profile-avatar').src = data.profile_pic;
        if(data.banner_pic && data.banner_pic !== 'default_banner.png') document.getElementById('banner-img').style.backgroundImage = `url('${data.banner_pic}')`;
        
        // Visibility Logic (Is Me vs Visitor)
        const isMe = data.is_me !== undefined ? data.is_me : true; // /me returns no is_me, so default true
        
        if(!isMe) {
            document.querySelectorAll('.control-me').forEach(e => e.style.display = 'none');
            document.getElementById('avatar-edit-wrapper').style.display = 'none';
            document.getElementById('banner-edit-wrapper').style.display = 'none';
            
            document.getElementById('follow-container').style.display = 'block';
            const btn = document.getElementById('follow-action-btn');
            if(data.is_following) {
                btn.textContent = 'Siguiendo'; btn.classList.remove('btn-primary'); btn.classList.add('btn-outline');
            } else {
                btn.textContent = 'Seguir'; btn.classList.add('btn-primary'); btn.classList.remove('btn-outline');
            }
            
            document.getElementById('comment-form-container').style.display = 'block';
        } else {
            // Is me
            document.querySelectorAll('.control-me').forEach(e => e.style.display = 'inline-block');
            document.getElementById('follow-container').style.display = 'none';
            document.getElementById('comment-form-container').style.display = 'none'; // Own wall
        }
        
        loadComments(data.id);
    } catch (e) { console.error("Error al cargar", e); }
}

async function toggleFollow() {
    try {
        const res = await fetch(`/api/profile/${viewProfileId}/follow`, { method: 'POST' });
        if(res.ok) loadProfile(); // Reload follow count + button state
    } catch (e) { showToast('Error al seguir', 'error'); }
}

async function loadComments(profileId) {
    const list = document.getElementById('comments-list');
    list.innerHTML = 'Cargando...';
    try {
        const res = await fetch(`/api/profile/${profileId}/comments`);
        const comments = await res.json();
        if(comments.length === 0) { list.innerHTML = '<p style="color: #888; text-align: center;">No hay comentarios o_o</p>'; return; }
        
        list.innerHTML = '';
        comments.forEach(c => {
            const date = new Date(c.created_at).toLocaleString();
            const heartIcon = c.user_reacted ? '❤️' : '🤍';
            list.innerHTML += `
                <div class="comment-box">
                    <div class="comment-header">
                        <span class="comment-author" onclick="window.location.href='/perfil?id=${c.author_id}'" style="cursor:pointer">${c.author}</span>
                        <span>${date}</span>
                    </div>
                    <div class="comment-body" style="margin-bottom:10px;">${c.content}</div>
                    <div>
                        <button class="react-btn ${c.user_reacted?'reacted':''}" onclick="reactComment(${c.id})">
                           ${heartIcon} <span style="font-size:0.9rem; color:#333; margin-left:3px">${c.reactions}</span>
                        </button>
                    </div>
                </div>`;
        });
    } catch (e) { list.innerHTML = 'Error al cargar'; }
}

async function postComment() {
    const content = document.getElementById('new-comment').value;
    if(!content.trim()) return;
    try {
        const res = await fetch(`/api/profile/${viewProfileId}/comments`, {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({content})
        });
        if(res.ok) { document.getElementById('new-comment').value = ''; showToast('Comentario publicado', 'success'); loadComments(viewProfileId); } 
        else { const d = await res.json(); showToast(d.error, 'error'); }
    } catch (e) { showToast('Falla en la red', 'error'); }
}

async function reactComment(cid) {
    try {
        const res = await fetch(`/api/comments/${cid}/react`, {method: 'POST'});
        if(res.ok) loadComments(viewProfileId);
    } catch (e) { showToast('Error red', 'error'); }
}

async function logout() {
    await fetch('/api/auth/logout', {method: 'POST'});
    localStorage.clear(); window.location.href = '/';
}

// Close search if clicked outside
document.addEventListener('click', (e) => {
    if(!e.target.closest('.search-bar')) document.getElementById('search-results').style.display='none';
});

window.onload = loadProfile;
