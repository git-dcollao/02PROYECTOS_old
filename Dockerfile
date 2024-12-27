# Utiliza una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos y los instala
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# ENV FLASK_APP=app:create_app
# ENV FLASK_ENV=development

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]