FROM python:3.11-slim

# Evitar buffering para ver logs en tiempo real
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt ./

# Instalar paquetes del sistema necesarios para compilación si hacen falta
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar la aplicación
COPY Foundry_AI.py ./

# Ejecutar el script por defecto
CMD ["python", "Foundry_AI.py"]
