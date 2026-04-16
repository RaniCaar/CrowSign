from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import mediapipe as mp
import os

# Determinar la ruta absoluta al frontend
FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_FOLDER)
CORS(app)

def distancia_euclidiana(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

def draw_bounding_box(image, hand_landmarks):
    image_height, image_width, _ = image.shape
    x_min, y_min = image_width, image_height
    x_max, y_max = 0, 0
    
    for landmark in hand_landmarks.landmark:
        x, y = int(landmark.x * image_width), int(landmark.y * image_height)
        if x < x_min: x_min = x
        if y < y_min: y_min = y
        if x > x_max: x_max = x
        if y > y_max: y_max = y
    
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

# Inicializar Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def gen_frames():  
    # Intentar abrir la cámara
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=1) as hands:
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
                
            image = cv2.flip(image, 1)
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image_height, image_width, _ = image.shape

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    
                    draw_bounding_box(image, hand_landmarks)

                    # Coordenadas
                    index_finger_tip = (int(hand_landmarks.landmark[8].x * image_width), int(hand_landmarks.landmark[8].y * image_height))
                    index_finger_pip = (int(hand_landmarks.landmark[6].x * image_width), int(hand_landmarks.landmark[6].y * image_height))
                    thumb_tip = (int(hand_landmarks.landmark[4].x * image_width), int(hand_landmarks.landmark[4].y * image_height))
                    thumb_pip = (int(hand_landmarks.landmark[2].x * image_width), int(hand_landmarks.landmark[2].y * image_height))
                    middle_finger_tip = (int(hand_landmarks.landmark[12].x * image_width), int(hand_landmarks.landmark[12].y * image_height))
                    middle_finger_pip = (int(hand_landmarks.landmark[10].x * image_width), int(hand_landmarks.landmark[10].y * image_height))
                    ring_finger_tip = (int(hand_landmarks.landmark[16].x * image_width), int(hand_landmarks.landmark[16].y * image_height))
                    ring_finger_pip = (int(hand_landmarks.landmark[14].x * image_width), int(hand_landmarks.landmark[14].y * image_height))
                    pinky_tip = (int(hand_landmarks.landmark[20].x * image_width), int(hand_landmarks.landmark[20].y * image_height))
                    pinky_pip = (int(hand_landmarks.landmark[18].x * image_width), int(hand_landmarks.landmark[18].y * image_height))
                    ring_finger_pip2 = (int(hand_landmarks.landmark[5].x * image_width), int(hand_landmarks.landmark[5].y * image_height))

                    # Logica de deteccion (Lógica original extraída)
                    if abs(thumb_tip[1] - index_finger_pip[1]) <45 and abs(thumb_tip[1] - middle_finger_pip[1]) < 30 and abs(thumb_tip[1] - ring_finger_pip[1]) < 30 and abs(thumb_tip[1] - pinky_pip[1]) < 30:
                        cv2.putText(image, 'A', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif index_finger_pip[1] - index_finger_tip[1]>0 and pinky_pip[1] - pinky_tip[1] > 0 and middle_finger_pip[1] - middle_finger_tip[1] >0 and ring_finger_pip[1] - ring_finger_tip[1] >0 and middle_finger_tip[1] - ring_finger_tip[1] <0 and abs(thumb_tip[1] - ring_finger_pip2[1])<40:
                        cv2.putText(image, 'B', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif abs(index_finger_tip[1] - thumb_tip[1]) < 360 and index_finger_tip[1] - middle_finger_pip[1]<0 and index_finger_tip[1] - middle_finger_tip[1] < 0 and index_finger_tip[1] - index_finger_pip[1] > 0:
                        cv2.putText(image, 'C', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif distancia_euclidiana(thumb_tip, middle_finger_tip) < 65 and distancia_euclidiana(thumb_tip, ring_finger_tip) < 65 and  pinky_pip[1] - pinky_tip[1]<0 and index_finger_pip[1] - index_finger_tip[1]>0:
                        cv2.putText(image, 'D', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif index_finger_pip[1] - index_finger_tip[1] < 0 and pinky_pip[1] - pinky_tip[1] < 0 and middle_finger_pip[1] - middle_finger_tip[1] < 0 and ring_finger_pip[1] - ring_finger_tip[1] < 0 and abs(index_finger_tip[1] - thumb_tip[1]) < 100 and thumb_tip[1] - index_finger_tip[1] > 0 and thumb_tip[1] - middle_finger_tip[1] > 0 and thumb_tip[1] - ring_finger_tip[1] > 0 and thumb_tip[1] - pinky_tip[1] > 0:
                        cv2.putText(image, 'E', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif pinky_pip[1] - pinky_tip[1] > 0 and middle_finger_pip[1] - middle_finger_tip[1] > 0 and ring_finger_pip[1] - ring_finger_tip[1] > 0 and index_finger_pip[1] - index_finger_tip[1] < 0 and abs(thumb_pip[1] - thumb_tip[1]) > 0 and distancia_euclidiana(index_finger_tip, thumb_tip) <65:
                        cv2.putText(image, 'F', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif distancia_euclidiana(thumb_tip, index_finger_tip) < 50 and index_finger_pip[1] - index_finger_tip[1] > 0 and middle_finger_pip[1] - middle_finger_tip[1] < 0 and ring_finger_pip[1] - ring_finger_tip[1] < 0 and pinky_pip[1] - pinky_tip[1] < 0:
                        cv2.putText(image, 'G', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif index_finger_pip[1] - index_finger_tip[1] > 0 and middle_finger_pip[1] - middle_finger_tip[1] > 0 and abs(index_finger_tip[1] - middle_finger_tip[1]) < 30 and ring_finger_pip[1] - ring_finger_tip[1] < 0 and pinky_pip[1] - pinky_tip[1] < 0 and thumb_tip[1] - index_finger_tip[1] > 0:
                        cv2.putText(image, 'H', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif pinky_pip[1] - pinky_tip[1] > 0 and index_finger_pip[1] - index_finger_tip[1] < 0 and middle_finger_pip[1] - middle_finger_tip[1] < 0 and ring_finger_pip[1] - ring_finger_tip[1] < 0 and thumb_pip[1] - thumb_tip[1] < 0:
                        cv2.putText(image, 'I', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif pinky_pip[1] - pinky_tip[1] > 0 and index_finger_pip[1] - index_finger_tip[1] < 0 and middle_finger_pip[1] - middle_finger_tip[1] < 0 and ring_finger_pip[1] - ring_finger_tip[1] < 0 and abs(thumb_tip[1] - pinky_tip[1]) < 50:
                        cv2.putText(image, 'J', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
                    elif index_finger_pip[1] - index_finger_tip[1] > 0 and middle_finger_pip[1] - middle_finger_tip[1] > 0 and abs(index_finger_tip[1] - middle_finger_tip[1]) > 20 and ring_finger_pip[1] - ring_finger_tip[1] < 0 and pinky_pip[1] - pinky_tip[1] < 0 and distancia_euclidiana(thumb_tip, middle_finger_pip) < 50:
                        cv2.putText(image, 'K', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)

            ret, buffer = cv2.imencode('.jpg', image)
            image_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Ruta para acceder al stream de la cámara analizado"""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Sirve el index.html principal (Login)"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Sirve cualquier otro archivo del frontend (lector.html, js, css, etc)"""
    return send_from_directory(app.static_folder, path)

@app.route('/status')
def status():
    return jsonify({"status": "Backend running", "camera": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
