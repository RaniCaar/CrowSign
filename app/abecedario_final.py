import cv2
import mediapipe as mp

def distancia_euclidiana(p1, p2):
    d = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return d

def draw_bounding_box(image, hand_landmarks):
    image_height, image_width, _ = image.shape
    x_min, y_min = image_width, image_height
    x_max, y_max = 0, 0
    
    # Iterate through the landmarks to find the bounding box coordinates
    for landmark in hand_landmarks.landmark:
        x, y = int(landmark.x * image_width), int(landmark.y * image_height)
        if x < x_min: x_min = x
        if y < y_min: y_min = y
        if x > x_max: x_max = x
        if y > y_max: y_max = y
    
    # Draw the bounding box
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Configuración de la cámara
# Si tienes múltiples cámaras, cambia el 0 por 1, 2, etc.
CAMERA_INDEX = 0

cap = cv2.VideoCapture(CAMERA_INDEX)

# Verificar que la cámara se abrió correctamente
if not cap.isOpened():
    print(f"Error: No se pudo abrir la cámara {CAMERA_INDEX}")
    print("Intenta cambiar CAMERA_INDEX a 1, 2, etc. si tienes múltiples cámaras")
    exit()

# Configurar resolución (opcional - algunas cámaras pueden no soportar estas resoluciones)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Obtener la resolución real de la cámara
actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Cámara abierta correctamente. Resolución: {actual_width}x{actual_height}")

with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Advertencia: No se pudo leer el frame de la cámara")
      continue

    # Voltear la imagen horizontalmente para efecto espejo (más intuitivo)
    image = cv2.flip(image, 1)
    
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    image_height, image_width, _ = image.shape
    if results.multi_hand_landmarks:
        if len(results.multi_hand_landmarks):
            for num, hand_landmarks in enumerate(results.multi_hand_landmarks):
                
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Draw bounding box
                draw_bounding_box(image, hand_landmarks)

                index_finger_tip = (int(hand_landmarks.landmark[8].x * image_width),
                                int(hand_landmarks.landmark[8].y * image_height))
                index_finger_pip = (int(hand_landmarks.landmark[6].x * image_width),
                                int(hand_landmarks.landmark[6].y * image_height))
                
                thumb_tip = (int(hand_landmarks.landmark[4].x * image_width),
                                int(hand_landmarks.landmark[4].y * image_height))
                thumb_pip = (int(hand_landmarks.landmark[2].x * image_width),
                                int(hand_landmarks.landmark[2].y * image_height))
                
                middle_finger_tip = (int(hand_landmarks.landmark[12].x * image_width),
                                int(hand_landmarks.landmark[12].y * image_height))
                
                middle_finger_pip = (int(hand_landmarks.landmark[10].x * image_width),
                                int(hand_landmarks.landmark[10].y * image_height))
                
                ring_finger_tip = (int(hand_landmarks.landmark[16].x * image_width),
                                int(hand_landmarks.landmark[16].y * image_height))
                ring_finger_pip = (int(hand_landmarks.landmark[14].x * image_width),
                                int(hand_landmarks.landmark[14].y * image_height))
                
                pinky_tip = (int(hand_landmarks.landmark[20].x * image_width),
                                int(hand_landmarks.landmark[20].y * image_height))
                pinky_pip = (int(hand_landmarks.landmark[18].x * image_width),
                                int(hand_landmarks.landmark[18].y * image_height))
                
                wrist = (int(hand_landmarks.landmark[0].x * image_width),
                                int(hand_landmarks.landmark[0].y * image_height))
                
                ring_finger_pip2 = (int(hand_landmarks.landmark[5].x * image_width),
                                int(hand_landmarks.landmark[5].y * image_height))
                
                if abs(thumb_tip[1] - index_finger_pip[1]) <45 \
                    and abs(thumb_tip[1] - middle_finger_pip[1]) < 30 and abs(thumb_tip[1] - ring_finger_pip[1]) < 30\
                    and abs(thumb_tip[1] - pinky_pip[1]) < 30:
                    cv2.putText(image, 'A', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                    
                   
                elif index_finger_pip[1] - index_finger_tip[1]>0 and pinky_pip[1] - pinky_tip[1] > 0 and \
                    middle_finger_pip[1] - middle_finger_tip[1] >0 and ring_finger_pip[1] - ring_finger_tip[1] >0 and \
                        middle_finger_tip[1] - ring_finger_tip[1] <0 and abs(thumb_tip[1] - ring_finger_pip2[1])<40:
                    cv2.putText(image, 'B', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                    
                elif abs(index_finger_tip[1] - thumb_tip[1]) < 360 and \
                    index_finger_tip[1] - middle_finger_pip[1]<0 and index_finger_tip[1] - middle_finger_tip[1] < 0 and \
                        index_finger_tip[1] - index_finger_pip[1] > 0:
                   cv2.putText(image, 'C', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                
                elif distancia_euclidiana(thumb_tip, middle_finger_tip) < 65 \
                    and distancia_euclidiana(thumb_tip, ring_finger_tip) < 65 \
                    and  pinky_pip[1] - pinky_tip[1]<0\
                    and index_finger_pip[1] - index_finger_tip[1]>0:
                    cv2.putText(image, 'D', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                   
                elif index_finger_pip[1] - index_finger_tip[1] < 0 and pinky_pip[1] - pinky_tip[1] < 0 and \
                    middle_finger_pip[1] - middle_finger_tip[1] < 0 and ring_finger_pip[1] - ring_finger_tip[1] < 0 \
                        and abs(index_finger_tip[1] - thumb_tip[1]) < 100 and \
                            thumb_tip[1] - index_finger_tip[1] > 0 \
                            and thumb_tip[1] - middle_finger_tip[1] > 0 \
                            and thumb_tip[1] - ring_finger_tip[1] > 0 \
                            and thumb_tip[1] - pinky_tip[1] > 0:

                    cv2.putText(image, 'E', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                    
                elif  pinky_pip[1] - pinky_tip[1] > 0 and middle_finger_pip[1] - middle_finger_tip[1] > 0 and \
                    ring_finger_pip[1] - ring_finger_tip[1] > 0 and index_finger_pip[1] - index_finger_tip[1] < 0 \
                        and abs(thumb_pip[1] - thumb_tip[1]) > 0 and distancia_euclidiana(index_finger_tip, thumb_tip) <65:

                    cv2.putText(image, 'F', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                    
                
                # Letra G: Pulgar e índice forman círculo, otros dedos extendidos
                elif distancia_euclidiana(thumb_tip, index_finger_tip) < 50 \
                    and index_finger_pip[1] - index_finger_tip[1] > 0 \
                    and middle_finger_pip[1] - middle_finger_tip[1] < 0 \
                    and ring_finger_pip[1] - ring_finger_tip[1] < 0 \
                    and pinky_pip[1] - pinky_tip[1] < 0:
                    cv2.putText(image, 'G', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                
                # Letra H: Índice y medio extendidos juntos, otros dedos cerrados
                elif index_finger_pip[1] - index_finger_tip[1] > 0 \
                    and middle_finger_pip[1] - middle_finger_tip[1] > 0 \
                    and abs(index_finger_tip[1] - middle_finger_tip[1]) < 30 \
                    and ring_finger_pip[1] - ring_finger_tip[1] < 0 \
                    and pinky_pip[1] - pinky_tip[1] < 0 \
                    and thumb_tip[1] - index_finger_tip[1] > 0:
                    cv2.putText(image, 'H', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                
                # Letra I: Meñique extendido, otros dedos cerrados (incluyendo pulgar)
                elif pinky_pip[1] - pinky_tip[1] > 0 \
                    and index_finger_pip[1] - index_finger_tip[1] < 0 \
                    and middle_finger_pip[1] - middle_finger_tip[1] < 0 \
                    and ring_finger_pip[1] - ring_finger_tip[1] < 0 \
                    and thumb_pip[1] - thumb_tip[1] < 0:
                    cv2.putText(image, 'I', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                
                # Letra J: Similar a I pero con pulgar cerca del meñique
                elif pinky_pip[1] - pinky_tip[1] > 0 \
                    and index_finger_pip[1] - index_finger_tip[1] < 0 \
                    and middle_finger_pip[1] - middle_finger_tip[1] < 0 \
                    and ring_finger_pip[1] - ring_finger_tip[1] < 0 \
                    and abs(thumb_tip[1] - pinky_tip[1]) < 50:
                    cv2.putText(image, 'J', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                
                # Letra K: Índice y medio extendidos en V, pulgar tocando base del medio
                elif index_finger_pip[1] - index_finger_tip[1] > 0 \
                    and middle_finger_pip[1] - middle_finger_tip[1] > 0 \
                    and abs(index_finger_tip[1] - middle_finger_tip[1]) > 20 \
                    and ring_finger_pip[1] - ring_finger_tip[1] < 0 \
                    and pinky_pip[1] - pinky_tip[1] < 0 \
                    and distancia_euclidiana(thumb_tip, middle_finger_pip) < 50:
                    cv2.putText(image, 'K', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)
                    
                print("pulgar", thumb_tip[1])
                print("dedo indice",index_finger_tip[1])
                
    cv2.imshow('MediaPipe Hands - Presiona ESC para salir', image)
    if cv2.waitKey(5) & 0xFF == 27:  # Presiona ESC para salir
      break

print("Cerrando cámara...")
cap.release()
cv2.destroyAllWindows()
print("Programa finalizado")