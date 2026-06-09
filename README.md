# Pico y Placa — Validador Inteligente

Sistema web que detecta automáticamente la placa de un vehículo a partir de una fotografía (o ingresándola manualmente) y determina en tiempo real si tiene restricción de circulación por Pico y Placa en las principales ciudades de Colombia.

---

## Características

- **Detección automática de placas** usando un modelo YOLOv8 entrenado a medida.
- **Lectura OCR** del texto de la placa con EasyOCR, incluyendo preprocesado de imagen para mayor precisión.
- **Motor de reglas** configurable por ciudad: horarios pico, días activos, dígitos restringidos y festivos.
- **Entrada manual** de placa como alternativa a la fotografía.
- **Ciudades soportadas:** Bogotá, Medellín y Cali.
- **API REST** con Flask lista para integrarse en otros servicios.
- **Despliegue con Docker** y configuración incluida para Render.

---

## Arquitectura

```
pico-y-placa/
├── src/
│   ├── api/                # Aplicación Flask (rutas, templates, assets)
│   │   ├── routes/
│   │   │   ├── health.py   # GET /health
│   │   │   └── validate.py # POST /validate
│   │   ├── templates/      # Vistas HTML (index, validador, normas)
│   │   └── static/         # CSS y JS (cámara)
│   ├── model/
│   │   ├── detect_plate.py # Detección YOLOv8 → recorte de placa
│   │   ├── read_plate.py   # OCR EasyOCR → texto de placa
│   │   └── train_detector.py
│   ├── rules/
│   │   ├── pico_placa_engine.py  # Lógica de restricción
│   │   ├── restrictions.json     # Reglas por ciudad
│   │   └── holidays.py           # Festivos colombianos
│   ├── data/               # Scripts de dataset y conversión YOLO
│   └── pipeline.py         # Orquestador: detección → OCR → reglas
├── models/detector/weights/ # Pesos del modelo (best.pt)
├── tests/                  # Pruebas con pytest
├── Dockerfile
├── render.yaml
└── requirements.txt
```

El flujo completo para una consulta con imagen es:

```
Imagen (JPEG/PNG/WebP)
        │
        ▼
  PlateDetector (YOLOv8)  ──► recorte de la placa
        │
        ▼
  read_plate (EasyOCR)    ──► texto "ABC123"
        │
        ▼
  pico_placa_engine       ──► RestricciónResult {restricted, reason, ...}
```

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Framework web | Flask 3.0 |
| Detección de placa | YOLOv8 (Ultralytics 8.4) |
| OCR | EasyOCR 1.7 |
| Procesamiento de imagen | OpenCV 4.10, Pillow |
| Festivos colombianos | `holidays` 0.52 |
| Servidor de producción | Gunicorn |
| Contenedor | Docker (python:3.11-slim) |

---

## Instalación y ejecución local

### Prerrequisitos

- Python 3.11+
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/MilethMartinezR/pico-y-placa.git
cd pico-y-placa
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Descargar los pesos del modelo

Los pesos `best.pt` se descargan automáticamente desde Google Drive. Si prefieres hacerlo manualmente:

```bash
pip install gdown
mkdir -p models/detector/weights
gdown --id 17tdGSZz2mnreyHDNGhmnz20VxMyp64jF -O models/detector/weights/best.pt
```

### 4. Iniciar la aplicación

```bash
python -m src.api.app
```

La aplicación queda disponible en `http://localhost:5000`.

---

## Ejecución con Docker

```bash
# Construir la imagen (descarga pesos y modelos EasyOCR automáticamente)
docker build -t pico-y-placa .

# Ejecutar
docker run -p 7860:7860 pico-y-placa
```

Accede en `http://localhost:7860`.

---

## API REST

### `GET /health`

Verifica que el servicio está activo.

**Respuesta:**
```json
{ "status": "ok" }
```

---

### `POST /validate`

Valida si una placa tiene restricción.

**Parámetros (form-data):**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `city` | string | No (default: `bogota`) | Ciudad: `bogota`, `medellin`, `cali` |
| `image` | file | Sí o `plate_text` | Imagen de la placa (JPEG/PNG/WebP, máx 5 MB) |
| `plate_text` | string | Sí o `image` | Texto de la placa, ej. `ABC123` |

**Respuesta exitosa:**
```json
{
  "plate": "ABC123",
  "city": "Bogotá D.C.",
  "restricted": true,
  "reason": "Dígito 3 restringido los Tuesday en horario pico",
  "checked_at": "2025-03-04 07:30:00 COT"
}
```
**Errores comunes:**

| Código | Descripción |
|---|---|
| `400` | No se envió imagen ni placa |
| `413` | Imagen mayor a 5 MB |
| `415` | Formato de imagen no soportado |
| `422` | Placa no detectada, ilegible o ciudad no soportada |

---

## Reglas de restricción

Las reglas se configuran en `src/rules/restrictions.json`. Actualmente:

### Bogotá D.C.
| Día | Dígitos restringidos | Horario pico |
|---|---|---|
| Lunes | 1, 2 | 6:00–8:30 / 15:00–19:30 |
| Martes | 3, 4 | 6:00–8:30 / 15:00–19:30 |
| Miércoles | 5, 6 | 6:00–8:30 / 15:00–19:30 |
| Jueves | 7, 8 | 6:00–8:30 / 15:00–19:30 |
| Viernes | 9, 0 | 6:00–8:30 / 15:00–19:30 |

### Medellín
| Día | Dígitos restringidos | Horario pico |
|---|---|---|
| Lunes | 1, 6 | 7:00–9:00 / 17:00–20:00 |
| Martes | 2, 7 | 7:00–9:00 / 17:00–20:00 |
| Miércoles | 3, 8 | 7:00–9:00 / 17:00–20:00 |
| Jueves | 4, 9 | 7:00–9:00 / 17:00–20:00 |
| Viernes | 5, 0 | 7:00–9:00 / 17:00–20:00 |

### Cali
| Día | Dígitos restringidos | Horario pico |
|---|---|---|
| Lunes | 1, 2 | 7:00–9:00 / 17:00–19:00 |
| Martes | 3, 4 | 7:00–9:00 / 17:00–19:00 |
| Miércoles | 5, 6 | 7:00–9:00 / 17:00–19:00 |
| Jueves | 7, 8 | 7:00–9:00 / 17:00–19:00 |
| Viernes | 9, 0 | 7:00–9:00 / 17:00–19:00 |

> En ninguna ciudad aplica restricción los fines de semana ni en días festivos.

---

## Tests

```bash
pytest tests/ -v
```

Las pruebas del motor de reglas (`tests/test_engine.py`) cubren:

- Restricción en horario pico con dígito correcto
- Sin restricción por dígito no restringido
- Sin restricción fuera de horario pico
- Sin restricción en fin de semana
- Sin restricción en festivo (1 de enero)
- Error al consultar ciudad no soportada

Las pruebas de OCR (`tests/test_ocr.py`) y conversión de datos (`tests/test_convert.py`) también están incluidas.

---

## Despliegue en Hugging Face Spaces
 
La aplicación está desplegada como un **Space en Hugging Face** usando el SDK de Docker.
 
### Configuración del Space
 
El `Dockerfile` ya está listo para Hugging Face Spaces. Solo asegúrate de que el puerto expuesto sea el **7860** (requerido por la plataforma), lo cual ya está configurado:
 
```dockerfile
EXPOSE 7860
CMD ["python", "-m", "gunicorn", "-w", "1", "-b", "0.0.0.0:7860", "src.api.app:create_app()"]
```
 
### Pasos para desplegar
 
1. Crea una cuenta en [huggingface.co](https://huggingface.co) si no tienes una.
2. Ve a **New Space** → elige el SDK **Docker**.
3. Clona el repositorio del Space y copia el contenido de este proyecto:
   ```bash
   git clone https://huggingface.co/spaces/TU_USUARIO/pico-y-placa
   ```
4. Sube los archivos y haz push:
   ```bash
   git add .
   git commit -m "Initial deploy"
   git push
   ```
5. Hugging Face construirá la imagen automáticamente con el `Dockerfile` del proyecto.
> **Nota:** Los pesos del modelo (`best.pt`) se descargan desde Google Drive durante el build gracias al paso `gdown` en el `Dockerfile`. Los modelos de EasyOCR también se precargan en la imagen para evitar descargas en tiempo de ejecución.

## Formatos de placa soportados

El OCR valida los siguientes patrones oficiales colombianos:

| Formato | Ejemplo | Descripción |
|---|---|---|
| `ABC123` | `TRM456` | Formato estándar (3 letras + 3 dígitos) |

---

## Licencia

Este proyecto es de uso académico y educativo.
