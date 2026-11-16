# ============================================================
#  Dockerfile: la "receta" para construir la imagen del juego.
#  Docker lee estas instrucciones de arriba hacia abajo.
# ============================================================

# 1. Partimos de una imagen que ya trae Python 3.12 instalado
#    (sobre un Linux mínimo; "slim" = versión liviana)
FROM python:3.12-slim

# 2. Dentro del contenedor, trabajamos en la carpeta /app
WORKDIR /app

# 3. Copiamos primero SOLO la lista de librerías y las instalamos.
#    (Así, si solo cambia el código, Docker reutiliza este paso ya hecho
#     y la construcción es más rápida.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos el resto del proyecto (app.py, logica.py, static/...)
COPY . .

# 5. Documentamos que el servidor escucha en el puerto 5000
EXPOSE 5000

# 6. El comando que se ejecuta cuando el contenedor arranca
CMD ["python", "app.py"]
