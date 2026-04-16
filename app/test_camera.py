"""
Script de prueba para verificar que tu cámara funciona correctamente.
Ejecuta este script primero para asegurarte de que tu cámara está funcionando.
"""

import cv2

print("Buscando cámaras disponibles...")
print("Presiona 'q' para salir de cada prueba\n")

# Probar diferentes índices de cámara
for camera_index in range(3):
    print(f"Probando cámara {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    
    if cap.isOpened():
        print(f"✓ Cámara {camera_index} está disponible")
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"  Resolución: {width}x{height}")
        
        # Mostrar un frame de prueba
        ret, frame = cap.read()
        if ret:
            print(f"  ✓ Puede capturar imágenes")
            cv2.imshow(f'Cámara {camera_index} - Presiona Q para continuar', frame)
            print("  Presiona 'q' en la ventana para continuar...")
            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()
        else:
            print(f"  ✗ No puede capturar imágenes")
        
        cap.release()
    else:
        print(f"✗ Cámara {camera_index} no está disponible")
    print()

print("\nPrueba completada.")
print("Usa el índice de la cámara que funcionó en abecedario_final.py (variable CAMERA_INDEX)")
