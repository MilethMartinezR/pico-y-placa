FROM python:3.11-slim

WORKDIR /app

# dependencias del sistema para OpenCV y EasyOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgomp1 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# descarga best.pt desde Google Drive
RUN pip install --no-cache-dir gdown && \
    mkdir -p models/detector/weights && \
    gdown --id 17tdGSZz2mnreyHDNGhmnz20VxMyp64jF -O models/detector/weights/best.pt

# precarga los modelos EasyOCR en la imagen para evitar descarga en runtime
RUN python -c "import easyocr; easyocr.Reader(['es','en'], gpu=False)"

EXPOSE 10000

CMD ["python", "-m", "gunicorn", "-w", "1", "-b", "0.0.0.0:10000", "src.api.app:create_app()"]
