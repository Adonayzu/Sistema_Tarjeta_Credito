import pika
from flask import Flask, jsonify, request, abort
import mysql.connector
from mysql.connector import Error
import os
import random
import json
from decimal import Decimal

app = Flask(__name__)

# Conexión a la base de datos
conexion_bd = {
    'host': 'mysql-tarjeta',
    'database': 'bd-tarjeta',
    'user': 'proyecto',
    'password': '12345',
    'port': 3306
}

# Conexión de RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-tarjeta', port=5672)) # el puerto por defecto de RabbitMQ es 5672
    canal = connection.channel() # Crear un canal
    canal.queue_declare(queue='cola-tarjeta') # Declarar una cola
    print("Conexión a RabbitMQ exitosa")
except Exception as e:
    print("Error al conectar con RabbitMQ:", e)

# Ruta de inicio de prueba para verificar que el contenedor está funcionando
@app.route('/', methods=['GET'])
def home():
    id_contenedor = os.environ.get('HOSTNAME')
    return jsonify({'status': 'ok', 'container': id_contenedor}), 200


# para crear tarjeta de crédito se necesita nombre, apellido, edad, dirección, datos laborales, datos beneficiarios, dpi y límite de crédito
@app.route('/tarjeta-credito', methods=['POST'])
def crear_tarjeta():
    body = request.get_json()  # obtener el cuerpo del request como JSON que viene del postman y se guarda en la variable body

    if not body or not all(key in body for key in
       ['nombre', 'apellido', 'edad', 'direccion', 'datos_laborales', 'datos_beneficiarios', 'dpi', 'limite_credito', 'numero_telefono']):
        abort(400, "Datos faltantes en el request") # 400 es bad request quiere decir que el request no se puede procesar

    # Generar número de tarjeta de crédito aleatorio que empieza con 6800
    numero_tarjeta = '6800' + ''.join([str(random.randint(0, 9)) for _ in range(12)])
    limite_credito = body['limite_credito'] # Obtener el límite de crédito del cuerpo del request
    id_contenedor = os.environ.get('HOSTNAME') # Obtener el ID del contenedor donde se creó la tarjeta de crédito

    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        # Crear un cursor para ejecutar sentencias SQL
        cursor = conexion.cursor() #cursor es un objeto que permite interactuar con la base de datos

        # Verificar si el DPI ya tiene una tarjeta asociada
        cursor.execute("SELECT COUNT(*) FROM cliente WHERE dpi = %s", (body['dpi'],))  # Contar cuántos registros hay con el DPI
        if cursor.fetchone()[0] > 0:  # Si ya existe un cliente con el DPI
            abort(400, "El cliente ya tiene una tarjeta de crédito asignada") # 400 es bad request

        # Insertar nuevo cliente en la base de datos
        sql_cliente = "INSERT INTO cliente (nombre, apellido, edad, direccion, datos_laborales, datos_beneficiarios, dpi, numero_telefono) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        # Valores que se van a insertar en la tabla cliente que vienen del body o del postman
        valores_cliente = (body['nombre'], body['apellido'], body['edad'], body['direccion'], body['datos_laborales'], body['datos_beneficiarios'], body['dpi'], body['numero_telefono'])
        cursor.execute(sql_cliente, valores_cliente)  # Ejecutar la sentencia SQL
        conexion.commit()  # Asegurar que se guarden los datos en la base de datos

        cliente_id = cursor.lastrowid  # Obtener el ID del cliente insertado

        # Insertar la tarjeta de crédito asociada al cliente en la base de datos
        sql_tarjeta = "INSERT INTO tarjeta_credito (numero_tarjeta, limite_credito, saldo_actual, cliente_id, replica_id) VALUES (%s, %s, %s, %s, %s)"
        valores_tarjeta = (numero_tarjeta, limite_credito, 0.00, cliente_id, id_contenedor)  # Valores que se van a insertar en la tabla tarjeta_credito
        cursor.execute(sql_tarjeta, valores_tarjeta)  # Ejecutar la sentencia SQL
        conexion.commit()  # Asegurar que se guarden los datos en la base de datos

        # Devolver la información de la tarjeta creada y el ID del contenedor donde se creó la tarjeta de crédito
        return jsonify({
            'id': cliente_id,
            'numero_tarjeta': numero_tarjeta,
            'limite_credito': limite_credito,
            'replica_id': id_contenedor
        }), 201

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close()  # Cerrar el cursor
        conexion.close()  # Cerrar la conexión




# Ontener la información de todas las tarjetas de crédito registradas
@app.route('/tarjeta-credito', methods=['GET'])
def obtener_tarjetas_credito():
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        # Crear un cursor para ejecutar sentencias SQL
        cursor = conexion.cursor(dictionary=True)  # Devolver los resultados como un diccionario para que sea más fácil de manipular
        sql = "SELECT * FROM tarjeta_credito" # Sentencia SQL para obtener todas las tarjetas de crédito
        cursor.execute(sql)  # Ejecutar la sentencia SQL
        tarjetas_credito = cursor.fetchall()  # Traer todos los registros o todas las filas encontradas de tarjetas de credito y las devuelve en una lista

        # Retornar las tarjetas de crédito
        return jsonify(tarjetas_credito), 200  # 200 es OK, se ejecutó correctamente

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close()  # Cerrar el cursor
        conexion.close()  # Cerrar la conexión


# Obtener la información de una tarjeta de crédito específica mediante el pan
@app.route('/tarjeta-credito/<string:numero_tarjeta>', methods=['GET'])
def obtener_tarjeta_credito(numero_tarjeta):
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        cursor = conexion.cursor(dictionary=True)  # Devolver los resultados como un diccionario para que sea más fácil de manipular
        sql = "SELECT * FROM tarjeta_credito WHERE numero_tarjeta = %s" # Sentencia SQL para obtener una tarjeta de crédito específica
        cursor.execute(sql, (numero_tarjeta,))  # Ejecutar la sentencia SQL con el parámetro
        tarjeta_credito = cursor.fetchone()  # Traer un solo registro encontradoo fila de la tabla tarjeta_credito y la devuelve como un diccionario

        # Si no encuentra la tarjeta de crédito
        if not tarjeta_credito:
            abort(404, "Tarjeta de crédito no encontrada")

        # Retornar la tarjeta de crédito encontrada
        return jsonify(tarjeta_credito), 200  # 200 es OK, se ejecutó correctamente

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close()  # Cerrar el cursor
        conexion.close()  # Cerrar la conexión


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
        if cursor.rowcount == 0:  # Si no se actualizó ningún registro el rowcount es 0 porque no encontró la tarjeta de crédito y si es mayor a 0 es porque se actualizó
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

        return '', 204  # 204 es no content porque no hay contenido que retornar

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



# Realizar un cargo a la tarjeta de crédito
@app.route('/tarjeta-credito/procesamiento/<string:numero_tarjeta>', methods=['POST'])
def realizar_cargo(numero_tarjeta):
    data = request.get_json()
    monto = data.get('monto')

    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        cursor = conexion.cursor(dictionary=True)

        # Obtener el saldo actual de la tarjeta de crédito
        sql = "SELECT id, saldo_actual, cliente_id FROM tarjeta_credito WHERE numero_tarjeta = %s"
        cursor.execute(sql, (numero_tarjeta,)) # Ejecutar la sentencia SQL con el parámetro
        tarjeta_credito = cursor.fetchone() # Traer el primer registro encontrado para obtener el saldo actual

        if not tarjeta_credito:
            abort(404, "Tarjeta de crédito no encontrada")  # 404 es not found

        # Obtener el número de teléfono del cliente
        sql = "SELECT numero_telefono FROM cliente WHERE id = %s"
        cursor.execute(sql, (tarjeta_credito['cliente_id'],)) # Ejecutar la sentencia SQL con el parámetro
        numero_telefono = cursor.fetchone()['numero_telefono'] # Traer el primer registro encontrado para obtener el número de teléfono

        # Actualizar el saldo de la tarjeta de crédito
        nuevo_saldo = tarjeta_credito['saldo_actual'] + Decimal(monto) # Nuevo saldo es el saldo actual más el monto del cargo
        sql_update = "UPDATE tarjeta_credito SET saldo_actual = %s WHERE numero_tarjeta = %s"
        cursor.execute(sql_update, (nuevo_saldo, numero_tarjeta)) # Ejecutar la sentencia SQL con los parámetros
        conexion.commit() # Asegurar que se guarden los datos en la base de datos

        # Insertar la transacción en la tabla transaccion
        sql_transaccion = "INSERT INTO transaccion (tarjeta_id, tipo, monto) VALUES (%s, %s, %s)"
        cursor.execute(sql_transaccion, (tarjeta_credito['id'], 'CARGO', monto)) # Ejecutar la sentencia SQL con los parámetros
        conexion.commit()

        # Enviar mensaje a la cola de RabbitMQ
        mensaje = json.dumps({ # Convertir el mensaje a JSON
            'numero_tarjeta': numero_tarjeta,
            'monto': monto,
            'tipo': 'cargo',
            'numero_telefono': numero_telefono,
            'mensaje': f'Se ha realizado un cargo a su tarjeta {numero_tarjeta} por Q{monto:.2f}'
        })
        canal.basic_publish(exchange='', routing_key='cola-tarjeta', body=mensaje) # Publicar el mensaje en la cola de RabbitMQ

        return jsonify({'mensaje': 'Cargo realizado correctamente'}), 200 # 200 es OK, se ejecutó correctamente

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")

    finally:
        cursor.close() # Cerrar el cursor
        conexion.close() # Cerrar la conexión

# Realizar un abono a la tarjeta de crédito
@app.route('/tarjeta-credito/abono/<string:numero_tarjeta>', methods=['POST'])
def realizar_abono(numero_tarjeta):
    data = request.get_json() # Obtener el cuerpo del request como JSON
    monto = data.get('monto') # Obtener el monto del abono

    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(**conexion_bd)
        cursor = conexion.cursor(dictionary=True)

        # Obtener el saldo actual de la tarjeta de crédito
        sql = "SELECT id, saldo_actual, cliente_id FROM tarjeta_credito WHERE numero_tarjeta = %s" # Sentencia SQL para obtener el saldo actual
        cursor.execute(sql, (numero_tarjeta,)) # Ejecutar la sentencia SQL con el parámetro
        tarjeta_credito = cursor.fetchone() # Traer el primer registro encontrado para obtener el saldo actual

        if not tarjeta_credito:
            abort(404, "Tarjeta de crédito no encontrada")

        # Obtener el número de teléfono del cliente
        sql = "SELECT numero_telefono FROM cliente WHERE id = %s" # Sentencia SQL para obtener el número de teléfono
        cursor.execute(sql, (tarjeta_credito['cliente_id'],)) # Ejecutar la sentencia SQL con el parámetro para obtener el número de teléfono
        numero_telefono = cursor.fetchone()['numero_telefono'] # Traer el primer registro encontrado para obtener el número de teléfono

        # Actualizar el saldo de la tarjeta de crédito
        nuevo_saldo = tarjeta_credito['saldo_actual'] - Decimal(monto) # Nuevo saldo es el saldo actual menos el monto del abono
        sql_update = "UPDATE tarjeta_credito SET saldo_actual = %s WHERE numero_tarjeta = %s" # Sentencia SQL para actualizar el saldo
        cursor.execute(sql_update, (nuevo_saldo, numero_tarjeta))   # Ejecutar la sentencia SQL con los parámetros para actualizar el saldo
        conexion.commit() # Asegurar que se guarden los datos en la base de datos

        # Insertar la transacción en la tabla transaccion
        sql_transaccion = "INSERT INTO transaccion (tarjeta_id, tipo, monto) VALUES (%s, %s, %s)" # Sentencia
        cursor.execute(sql_transaccion, (tarjeta_credito['id'], 'ABONO', monto))    # Ejecutar la sentencia SQL con los parámetros para insertar la transacción
        conexion.commit() # Asegurar que se guarden los datos en la base de datos

        # Enviar mensaje a la cola de RabbitMQ
        mensaje = json.dumps({ # Convertir el mensaje a JSON
            'numero_tarjeta': numero_tarjeta,
            'monto': monto,
            'tipo': 'abono',
            'numero_telefono': numero_telefono,
            'mensaje': f'Se ha realizado un abono a su tarjeta {numero_tarjeta} por Q{monto:.2f}'
        })
        canal.basic_publish(exchange='', routing_key='cola-tarjeta', body=mensaje) # Publicar el mensaje en la cola de RabbitMQ

        return jsonify({'mensaje': 'Abono realizado correctamente'}), 200 # 200 es OK, se ejecutó correctamente

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        abort(500, "Error al conectar a la base de datos")


    finally:
        cursor.close() # Cerrar el cursor
        conexion.close() # Cerrar la conexión


if __name__ == '__main__': # Si se ejecuta este archivo
    app.run(host='0.0.0.0', port=5000, debug=True) # Ejecutar la aplicación en el puerto 5000