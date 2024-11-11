#Imagen base para mi api
FROM python:3.9-slim

#Crea directorio de trabajo dentro de mi contenedor puede llevar cualquier nombre
WORKDIR /app

#copia mi API hacia directorio de trabajo
 COPY . /app/

#Se instala flask
RUN pip install flask

RUN pip install pika

RUN pip install mysql-connector-python

#Expone el puerto dentro de mi contenedor hacia mi sistema operativo
EXPOSE 5000

#Ejecucion del puerto de mi API
CMD ["python", "app.py"]