import pika
from flask import Flask, jsonify, request, abort
import mysql.connector
from mysql.connector import Error
import os
import random
import json
import uuid
# Realizar un cargo a la tarjeta de crédito
from decimal import Decimal

app = Flask(__name__)

# Conexión a la base de datos
conexion_bd = {
    'host': 'mysql-tarjeta-credito',
    'database': 'sistema_tarjeta_credito',
    'user': 'adonay',
    'password': '12345',
    'port': 3306
}

# Conexión de RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-tarjeta', port=5672))
    canal = connection.channel()
    canal.queue_declare(queue='cola-tarjeta')
    print("Conexión a RabbitMQ exitosa")
except Exception as e:
    print("Error al conectar con RabbitMQ:", e)


@app.route('/', methods=['GET'])
def home():
    id_contenedor = os.environ.get('HOSTNAME')
    return jsonify({'status': 'ok', 'container': id_contenedor}), 200


@app.route('/health', methods=['GET'])
def obtener_health():
    id_contenedor = os.environ.get('HOSTNAME')
    return jsonify({'status': 'ok', 'container': id_contenedor}), 200


# Actualizar la información de una tarjeta de crédito específica mediante el pan
@app.route('/tarjeta-credito/<string:numero_tarjeta>', methods=['PUT'])
def actualizar_tarjeta_credito(numero_tarjeta):
    body = request.get_json()  # Obtener el cuerpo del request como JSON

    if not body or 'limite_credito' not in body or 'saldo_actual' not in body:
        abort(400, "Datos faltantes en el request")  # 400 es bad request

    try:
        conexion = mysql.connector.connect(**conexion_bd)
        cursor = conexion.cursor()
        sql = "UPDATE tarjeta_credito SET limite_credito = %s, saldo_actual = %s WHERE numero_tarjeta = %s"  # Sentencia SQL para actualizar
        valores = (body['limite_credito'], body['saldo_actual'], numero_tarjeta)  # Valores que se van a actualizar
        cursor.execute(sql, valores)  # Ejecutar la sentencia SQL
        conexion.commit()  # Asegurar que se guarden los datos en la base de datos

        # Si no encuentra la tarjeta de crédito
        if cursor.rowcount == 0:  # Si no se actualizó ningún registro
            abort(404, "Tarjeta de crédito no encontrada")  # 404 es not found

        # Retornar la tarjeta de crédito actualizada con el número de tarjeta y los nuevos valores en el postman
        return jsonify({
            'numero_tarjeta': numero_tarjeta,
            'limite_credito': body['limite_credito'],
            'saldo_actual': body['saldo_actual']
        }), 200  # 200 es OK, se ejecutó correctamente

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close() # Cerrar el cursor
        conexion.close() # Cerrar la conexión


# Eliminar una tarjeta de crédito específica mediante el pan
@app.route('/tarjeta-credito/<string:numero_tarjeta>', methods=['DELETE'])
def eliminar_tarjeta_credito(numero_tarjeta):
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        cursor = conexion.cursor(dictionary=True)  # Devolver los resultados como un diccionario para que sea más fácil de manipular
        # Verificar si la tarjeta de crédito existe y obtener su saldo actual
        sql_select = "SELECT saldo_actual FROM tarjeta_credito WHERE numero_tarjeta = %s" # Sentencia SQL para obtener el saldo actual
        cursor.execute(sql_select, (numero_tarjeta,)) # Ejecutar la sentencia SQL con el parámetro
        tarjeta_credito = cursor.fetchone() # Trae el primer registro encontrado para obtener el saldo actual
        # Si no encuentra la tarjeta de crédito
        if not tarjeta_credito:
            abort(404, "Tarjeta de crédito no encontrada")  # 404 es not found

        # Verificar si el saldo actual es cero
        if tarjeta_credito['saldo_actual'] != 0:
            abort(400, "No se puede eliminar la tarjeta de crédito con saldo pendiente")  # 400 es bad request

        # Eliminar la tarjeta de crédito
        sql_delete = "DELETE FROM tarjeta_credito WHERE numero_tarjeta = %s"
        cursor.execute(sql_delete, (numero_tarjeta,)) # Ejecutar la sentencia SQL con el parámetro
        conexion.commit()  # Asegurar que se guarden los datos en la base de datos

        return '', 204  # 204 es no content

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close()  # Cerrar el cursor
        conexion.close()  # Cerrar la conexión


# Obtener el balance de una tarjeta de crédito mediante el PAN. Debe de
# mostrar el límite, saldo actual y saldo disponible.
@app.route('/tarjeta-credito/balance/<string:numero_tarjeta>', methods=['GET'])
def obtener_balance_tarjeta(numero_tarjeta):
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        cursor = conexion.cursor(dictionary=True)  # Devolver los resultados como un diccionario para que sea más fácil de manipular los datos
        # Obtener el límite de crédito y el saldo actual de la tarjeta de crédito
        sql = "SELECT limite_credito, saldo_actual FROM tarjeta_credito WHERE numero_tarjeta = %s" # Sentencia SQL para obtener el límite de crédito y el saldo actual
        cursor.execute(sql, (numero_tarjeta,)) # Ejecutar la sentencia SQL con el parámetro
        tarjeta_credito = cursor.fetchone() # Traer el primer registro encontrado para obtener el límite de crédito y el saldo actual
        # Si no encuentra la tarjeta de crédito
        if not tarjeta_credito:
            abort(404, "Tarjeta de crédito no encontrada")  # 404 es not found

        # Calcular el saldo disponible
        saldo_disponible = tarjeta_credito['limite_credito'] - tarjeta_credito['saldo_actual'] # Saldo disponible es el límite de crédito menos el saldo actual

        # Retornar el balance de la tarjeta de crédito con el número de tarjeta, el límite de crédito, el saldo actual y el saldo disponible
        return jsonify({
            'numero_tarjeta': numero_tarjeta,
            'limite_credito': tarjeta_credito['limite_credito'],
            'saldo_actual': tarjeta_credito['saldo_actual'],
            'saldo_disponible': saldo_disponible
        }), 200  # 200 es OK, se ejecutó correctamente

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close()  # Cerrar el cursor
        conexion.close()  # Cerrar la conexión





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)