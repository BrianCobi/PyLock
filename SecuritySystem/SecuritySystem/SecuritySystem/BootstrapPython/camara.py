import cv2
import numpy as np
from datetime import datetime
import os

def capture_photo():

    savedirectory = "./app/static/images"
    camera = cv2.VideoCapture(0)  # Usa la cámara 0 (cámara predeterminada)
    if camera.isOpened():
        ret, frame = camera.read()  # Captura una imagen
        if ret:
            frame = adjust_brightness_contrast(frame, alpha=1.5, beta=100)
            frame = sharpen_image(frame)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Attempt_{timestamp}.jpg"
            filepath = os.path.join(savedirectory, filename)
            cv2.imwrite(filepath, frame)
            print(f"Imagen capturada y guardada como {filename}")
        else:
            print("No se pudo capturar la imagen")
    camera.release()  # Liberar la cámara

def adjust_brightness_contrast(image, alpha=1.3, beta=40):
    """
    Ajusta el brillo y el contraste de una imagen.
    - alpha: Ganancia de contraste (1.0 = sin cambio)
    - beta: Valor de brillo (0 = sin cambio)
    """
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted

def sharpen_image(image):
    """Aplica un filtro de sharpening a la imagen para mejorar los detalles."""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(image, -1, kernel)
    return sharpened

if __name__ == "__main__":
    capture_photo()
