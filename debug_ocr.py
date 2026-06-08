import cv2
import easyocr
from src.model.detect_plate import PlateDetector

img = cv2.imread('test_placa.jpg')
crop = PlateDetector().detect(img)
cv2.imwrite('recorte_placa.jpg', crop)
print(f"Tamaño recorte: {crop.shape}")

# preprocesado igual al de read_plate.py
gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
gray4x = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
_, thresh = cv2.threshold(gray4x, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
cv2.imwrite('recorte_procesado.jpg', thresh)
print("Guardado recorte_procesado.jpg")

reader = easyocr.Reader(['es','en'], gpu=False)
print("Sobre recorte original:", reader.readtext(crop, detail=1))
print("Sobre preprocesado 4x:", reader.readtext(thresh, detail=1))
