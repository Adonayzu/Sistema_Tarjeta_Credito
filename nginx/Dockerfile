# Utilizar como base la imagen de Nginx estable y ligera (alpine)
#especifica la imgen nginx en su versión estable, basada en alpine Linux, es una distribucion ligera y eficiente
#hace que el contenedor sea mas pequeño y rápido
FROM nginx:stable-alpine

# Copiar el archivo de configuración de Nginx desde el directorio actual
# ./nginx.conf-> Especifica el archivo de configuración de Nginx en tu directorio actual donde se encuentra tu Dockerfile
#/etc/nginx/conf.d/default.conf-> Especifica el destino dentro del contenedor donde se copiará el archivo
#En este caso, es el directorio de configuración de Nginx.
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 80 para que el contenedor pueda aceptar conexiones HTTP
EXPOSE 80

# Ejecutar Nginx en modo no daemon para que el contenedor
# no se detenga. La opción -g permite pasar directivas globales a Nginx.
CMD ["nginx", "-g", "daemon off;"]
