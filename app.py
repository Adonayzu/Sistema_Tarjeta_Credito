import pika
from flask import Flask, jsonify, request, abort  # importar librerias el jsonify es para convertir un diccionario a un json se retornan los datos
import mysql.connector  # importar libreria de mysql
from mysql.connector import Error  # importar libreria de errores de mysql por si da un error
# libreria os me permite acceder a las variables de entorno del sistema operativo
import os

#esta es la base para la api
app = Flask(__name__) # se inicializo flask y se le paso el nombre de la aplicacion



@app.route('/' , methods=['GET'])
def home():
    # variable de hambiente hostnmae
    id_contenedor = os.environ.get('HOSTNAME')
    return jsonify({'status': 'ok', 'container': id_contenedor}), 200


@app.route('/health', methods=['GET']) #el api rest es la ruta que se va a consumir y el metodo que se va a consumir
def obtener_health():
    #variable de hambiente hostnmae
    id_contenedor = os.environ.get('HOSTNAME')
    return jsonify({'status': 'ok', 'container': id_contenedor}), 200




# metodo principal sea el punto de entrada
if __name__ == '__main__':
    #se agrega el host y el puerto el puerto si no lo pongo el de flask lo agarra el 5000 por defecto
    app.run(host='0.0.0.0', port= 5000, debug= True)  # corre la aplicacion en modo debug y en el host