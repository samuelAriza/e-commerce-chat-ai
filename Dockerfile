# Usa la imagen base de Python 3.11 en su versión "slim"
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor en /app
# Todo lo que se ejecute o copie a partir de aquí se hará desde esta ruta
WORKDIR /app

# Copia primero el archivo de dependencias (requirements.txt) al contenedor
COPY requirements.txt .

# Instala las dependencias de Python especificadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al contenedor
COPY . .

# Expone el puerto 8000
EXPOSE 8000

# Define el comando que se ejecutará cuando el contenedor inicie
# Aquí se lanza el servidor Uvicorn, especificando:
# - El módulo y aplicación: src.infrastructure.api.main:app
# - Que escuche en todas las interfaces (0.0.0.0)
# - En el puerto 8000
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
