const socket = io();
let localStream;
let peerConnection;
const configuration = { 'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]};
let myProfile = { username: 'Anónimo', avatar: '/static/img/black_crow.png' };

async function initChat() {
    try {
        const res = await fetch('/api/auth/me');
        if(res.ok) {
            const data = await res.json();
            myProfile.username = data.username;
            if(data.profile_pic) myProfile.avatar = data.profile_pic;
        }
    } catch(e) {}
}

// Mediapipe Hands Setup
const videoElement = document.getElementById('local-video');
const canvasElement = document.getElementById('output-canvas');
const canvasCtx = canvasElement.getContext('2d');
const letterBox = document.getElementById('detected-letter');

function distancia_euclidiana(p1, p2) {
    return Math.sqrt(Math.pow(p2[0] - p1[0], 2) + Math.pow(p2[1] - p1[1], 2));
}

function onResultsHands(results) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        for (const landmarks of results.multiHandLandmarks) {
            drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#ff6b00', lineWidth: 5});
            drawLandmarks(canvasCtx, landmarks, {color: '#ffd700', lineWidth: 2});
            
            // Replicar las coordenadas como si fuera un layout de 1920x1080, para mantener la fidelidad 
            // matemática estricta a los umbrales (< 45, < 65) creados originalmente en Python.
            const w = 1920; 
            const h = 1080;
            
            const index_tip = [landmarks[8].x * w, landmarks[8].y * h];
            const index_pip = [landmarks[6].x * w, landmarks[6].y * h];
            
            const thumb_tip = [landmarks[4].x * w, landmarks[4].y * h];
            const thumb_pip = [landmarks[2].x * w, landmarks[2].y * h];
            
            const middle_tip = [landmarks[12].x * w, landmarks[12].y * h];
            const middle_pip = [landmarks[10].x * w, landmarks[10].y * h];
            
            const ring_tip = [landmarks[16].x * w, landmarks[16].y * h];
            const ring_pip = [landmarks[14].x * w, landmarks[14].y * h];
            
            const pinky_tip = [landmarks[20].x * w, landmarks[20].y * h];
            const pinky_pip = [landmarks[18].x * w, landmarks[18].y * h];
            
            const ring_pip2 = [landmarks[5].x * w, landmarks[5].y * h];

            let detect = '-';
            
            // Letra A
            if (Math.abs(thumb_tip[1] - index_pip[1]) < 45 && Math.abs(thumb_tip[1] - middle_pip[1]) < 30 && 
                Math.abs(thumb_tip[1] - ring_pip[1]) < 30 && Math.abs(thumb_tip[1] - pinky_pip[1]) < 30) {
                detect = 'A';
            }
            // Letra B
            else if (index_pip[1] - index_tip[1] > 0 && pinky_pip[1] - pinky_tip[1] > 0 && 
                     middle_pip[1] - middle_tip[1] > 0 && ring_pip[1] - ring_tip[1] > 0 && 
                     middle_tip[1] - ring_tip[1] < 0 && Math.abs(thumb_tip[1] - ring_pip2[1]) < 50) {
                detect = 'B';
            }
            // Letra C
            else if (Math.abs(index_tip[1] - thumb_tip[1]) < 360 && 
                     index_tip[1] - middle_pip[1] < 0 && index_tip[1] - middle_tip[1] < 0 && 
                     index_tip[1] - index_pip[1] > 0) {
                detect = 'C';
            }
            // Letra D (Ajustado)
            else if (distancia_euclidiana(thumb_tip, middle_tip) < 90 && 
                     distancia_euclidiana(thumb_tip, ring_tip) < 90 && 
                     pinky_pip[1] - pinky_tip[1] < 30 && 
                     index_pip[1] - index_tip[1] > 0) {
                detect = 'D';
            }
            // Letra E
            else if (index_pip[1] - index_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0 && 
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0 && 
                     Math.abs(index_tip[1] - thumb_tip[1]) < 120 && 
                     thumb_tip[1] - index_tip[1] > 0 && thumb_tip[1] - middle_tip[1] > 0 && 
                     thumb_tip[1] - ring_tip[1] > 0 && thumb_tip[1] - pinky_tip[1] > 0) {
                detect = 'E';
            }
            // Letra F
            else if (pinky_pip[1] - pinky_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     ring_pip[1] - ring_tip[1] > 0 && index_pip[1] - index_tip[1] < 0 && 
                     Math.abs(thumb_pip[1] - thumb_tip[1]) > 0 && distancia_euclidiana(index_tip, thumb_tip) < 80) {
                detect = 'F';
            }
            // Letra G
            else if (distancia_euclidiana(thumb_tip, index_tip) < 60 && 
                     index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] < 0 && 
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0) {
                detect = 'G';
            }
            // Letra H
            else if (index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     Math.abs(index_tip[1] - middle_tip[1]) < 40 && ring_pip[1] - ring_tip[1] < 0 && 
                     pinky_pip[1] - pinky_tip[1] < 0 && thumb_tip[1] - index_tip[1] > 0) {
                detect = 'H';
            }
            // Letra I (Ajustado)
            else if (pinky_pip[1] - pinky_tip[1] > 0 && index_pip[1] - index_tip[1] < 0 && 
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0) {
                detect = 'I';
            }
            // Letra J
            else if (pinky_pip[1] - pinky_tip[1] > 0 && index_pip[1] - index_tip[1] < 0 && 
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0 && 
                     Math.abs(thumb_tip[1] - pinky_tip[1]) < 60) {
                detect = 'J';
            }
            // Letra K
            else if (index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     Math.abs(index_tip[1] - middle_tip[1]) > 20 && ring_pip[1] - ring_tip[1] < 0 && 
                     pinky_pip[1] - pinky_tip[1] < 0 && distancia_euclidiana(thumb_tip, middle_pip) < 80) {
                detect = 'K';
            }
            // Letra L: Indice arriba, pulgar estirado, lo demás abajo
            else if (index_pip[1] - index_tip[1] > 0 && 
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0 &&
                     Math.abs(thumb_tip[0] - index_pip[0]) > 60) {
                detect = 'L';
            }
            // Letra M: Indice, Medio, Anular hacia abajo suavemente cruzando pulgar
            else if (index_tip[1] - index_pip[1] > 0 && middle_tip[1] - middle_pip[1] > 0 && 
                     ring_tip[1] - ring_pip[1] > 0 && pinky_tip[1] - pinky_pip[1] < 0 &&
                     distancia_euclidiana(thumb_tip, pinky_pip) < 80) {
                detect = 'M';
            }
            // Letra N: Indice y Medio hacia abajo
            else if (index_tip[1] - index_pip[1] > 0 && middle_tip[1] - middle_pip[1] > 0 && 
                     ring_tip[1] - ring_pip[1] < 0 && pinky_tip[1] - pinky_pip[1] < 0 &&
                     distancia_euclidiana(thumb_tip, ring_pip) < 80) {
                detect = 'N';
            }
            // Letra O: Todos los dedos hacen circulo tocando pulgar
            else if (distancia_euclidiana(thumb_tip, index_tip) < 60 && 
                     distancia_euclidiana(thumb_tip, middle_tip) < 60 && 
                     distancia_euclidiana(thumb_tip, ring_tip) < 70) {
                detect = 'O';
            }
            // Letra P: Como K pero apuntando abajo
            else if (index_tip[1] - index_pip[1] > 0 && middle_tip[1] - middle_pip[1] > 0 && 
                     Math.abs(index_tip[1] - middle_tip[1]) > 20 && ring_pip[1] - ring_tip[1] < 0 && 
                     pinky_pip[1] - pinky_tip[1] < 0 && distancia_euclidiana(thumb_tip, index_pip) < 80) {
                detect = 'P';
            }
            // Letra Q: Como G pero apuntando abajo (índice y pulgar casi paralelos abajo)
            else if (distancia_euclidiana(thumb_tip, index_tip) < 60 && 
                     index_tip[1] - index_pip[1] > 0 && middle_pip[1] - middle_tip[1] < 0 && 
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0) {
                detect = 'Q';
            }
            // Letra R: Indice y medio cruzados
            else if (index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0 &&
                     Math.abs(index_tip[0] - middle_tip[0]) < 25 && index_tip[1] > middle_tip[1]) {
                detect = 'R';
            }
            // Letra S: Puño cerrado, pulgar sobre el indice/medio
            else if (index_pip[1] - index_tip[1] < 0 && middle_pip[1] - middle_tip[1] < 0 && 
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0 &&
                     distancia_euclidiana(thumb_tip, middle_pip) < 60 && thumb_tip[1] < middle_pip[1]) {
                detect = 'S';
            }
            // Letra T: Puño cerrado, pulgar metido entre índice y medio
            else if (index_pip[1] - index_tip[1] < 0 && middle_pip[1] - middle_tip[1] < 0 && 
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0 &&
                     distancia_euclidiana(thumb_tip, index_pip) < 60 && thumb_tip[1] > index_pip[1]) {
                detect = 'T';
            }
            // Letra U: Índice y Medio estirados juntos
            else if (index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     distancia_euclidiana(index_tip, middle_tip) < 40 &&
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0) {
                detect = 'U';
            }
            // Letra V: Índice y Medio separados (Signo de paz)
            else if (index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     distancia_euclidiana(index_tip, middle_tip) > 50 &&
                     ring_pip[1] - ring_tip[1] < 0 && pinky_pip[1] - pinky_tip[1] < 0) {
                detect = 'V';
            }
            // Letra W: Índice, Medio y Anular arriba
            else if (index_pip[1] - index_tip[1] > 0 && middle_pip[1] - middle_tip[1] > 0 && 
                     ring_pip[1] - ring_tip[1] > 0 && pinky_pip[1] - pinky_tip[1] < 0) {
                detect = 'W';
            }
            // Letra X: Índice en forma de gancho (doblado a la mitad)
            else if (index_pip[1] - index_tip[1] > 0 && Math.abs(index_tip[1] - index_pip[1]) < 60 &&
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0 && 
                     pinky_pip[1] - pinky_tip[1] < 0 && distancia_euclidiana(thumb_tip, middle_pip) < 70) {
                detect = 'X';
            }
            // Letra Y: Pulgar y meñique estirados (Aloha)
            else if (pinky_pip[1] - pinky_tip[1] > 0 && index_pip[1] - index_tip[1] < 0 && 
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0 &&
                     Math.abs(thumb_tip[0] - pinky_tip[0]) > 100) {
                detect = 'Y';
            }
            // Letra Z: Índice dibujando (solo índice levantado parecido a D pero sin tocar pulgar)
            else if (index_pip[1] - index_tip[1] > 0 &&
                     middle_pip[1] - middle_tip[1] < 0 && ring_pip[1] - ring_tip[1] < 0 && 
                     pinky_pip[1] - pinky_tip[1] < 0 && distancia_euclidiana(thumb_tip, middle_pip) < 80) {
                detect = 'Z';
            }

            // Aplicar deteccion
            letterBox.innerText = detect;
            if(detect !== '-') socket.emit('sign_detected', {letter: detect});
        }
    }
    canvasCtx.restore();
}

const hands = new Hands({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`});
hands.setOptions({ maxNumHands: 1, modelComplexity: 1, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
hands.onResults(onResultsHands);

const camera = new Camera(videoElement, {
    onFrame: async () => { await hands.send({image: videoElement}); },
    width: 640, height: 480
});

camera.start().then(() => {
    localStream = videoElement.srcObject;
}).catch(err => {
    document.getElementById('err-modal').classList.add('active');
});

// Chat React Logic
const EMOJIS = ['❤️', '😂', '😡', '😢', '😳'];
let messageStore = {}; // msgId -> {reactions: {'❤️': 2}}

document.getElementById('chat-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const txt = input.value.trim();
    if(txt) {
        const msgId = 'msg_' + Date.now() + Math.floor(Math.random()*1000);
        socket.emit('chat_message', { id: msgId, user: myProfile.username, text: txt, avatar: myProfile.avatar, isMe: true });
        input.value = '';
    }
});

function renderReactions(msgId) {
    const cont = document.getElementById(`react-badges-${msgId}`);
    if(!cont) return;
    cont.innerHTML = '';
    const reacts = messageStore[msgId]?.reactions || {};
    for (const [emoji, count] of Object.entries(reacts)) {
        if(count > 0) {
            cont.innerHTML += `<div class="reaction-badge">${emoji} ${count}</div>`;
        }
    }
}

window.triggerReaction = function(msgId, emoji) {
    socket.emit('chat_reaction', {msgId, emoji});
};

socket.on('chat_reaction', (data) => {
    if(!messageStore[data.msgId]) return;
    if(!messageStore[data.msgId].reactions[data.emoji]) messageStore[data.msgId].reactions[data.emoji] = 0;
    messageStore[data.msgId].reactions[data.emoji]++;
    renderReactions(data.msgId);
});

socket.on('chat_message', (data) => {
    const msgs = document.getElementById('chat-messages');
    
    // Determine layout
    const isSelf = data.user === myProfile.username;
    messageStore[data.id] = {reactions: {}}; // Init storage for this msg

    const reactionMenuHTML = EMOJIS.map(e => `<span class="react-emoji" onclick="triggerReaction('${data.id}', '${e}')">${e}</span>`).join('');

    const el = document.createElement('div');
    el.className = `msg-line ${isSelf ? 'self' : ''}`;
    el.innerHTML = `
        <img src="${data.avatar}" class="msg-avatar">
        <div class="msg-content-wrapper">
            <span class="msg-username">${data.user}</span>
            <div class="msg-bubble">
                ${data.text}
                <div class="reaction-menu">${reactionMenuHTML}</div>
            </div>
            <div class="reactions-badge-container" id="react-badges-${data.id}"></div>
        </div>
    `;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
});

// WebRTC logic
function startCall() {
    if(!localStream) { 
        document.getElementById('err-modal').classList.add('active'); return; 
    }
    peerConnection = new RTCPeerConnection(configuration);
    localStream.getTracks().forEach(track => { peerConnection.addTrack(track, localStream); });
    peerConnection.ontrack = (event) => { document.getElementById('remote-video').srcObject = event.streams[0]; };
    peerConnection.onicecandidate = (event) => { if(event.candidate) socket.emit('ice_candidate', event.candidate); };

    peerConnection.createOffer()
        .then(offer => peerConnection.setLocalDescription(offer))
        .then(() => { socket.emit('offer', peerConnection.localDescription); });
}

socket.on('offer', async (description) => {
    if(!peerConnection) {
        peerConnection = new RTCPeerConnection(configuration);
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
        peerConnection.ontrack = (event) => { document.getElementById('remote-video').srcObject = event.streams[0]; };
        peerConnection.onicecandidate = (event) => { if (event.candidate) socket.emit('ice_candidate', event.candidate); };
    }
    await peerConnection.setRemoteDescription(description);
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('answer', peerConnection.localDescription);
});

socket.on('answer', async (description) => { await peerConnection.setRemoteDescription(description); });
socket.on('ice_candidate', async (candidate) => {
    try { await peerConnection.addIceCandidate(candidate); } catch (e) { console.error('Error ICE', e); }
});

initChat();
