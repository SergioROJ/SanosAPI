# Usar la imagen oficial de Python como imagen base
FROM python:3.12

RUN useradd -ms /bin/sh -u 1001 app

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos necesarios al directorio de trabajo
COPY ./requirements.txt /app/requirements.txt

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto al directorio de trabajo
COPY . /app

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
