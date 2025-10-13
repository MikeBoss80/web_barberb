# Imagen base de Python ligera
FROM python:3.11-slim

# Evita buffering de logs
ENV PYTHONUNBUFFERED=1

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para mysqlclient, pillow, tesseract y pdfplumber
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libjpeg-dev \
    zlib1g-dev \
    libtesseract-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copia los requirements e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia el resto del proyecto
COPY . .

# Ejecuta collectstatic (esto prepara los archivos estáticos)
RUN python manage.py collectstatic --noinput
# Expone el puerto donde correrá Django
EXPOSE 8080

# Usa Gunicorn en lugar del servidor de desarrollo
CMD ["gunicorn", "barberb.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "120"]
