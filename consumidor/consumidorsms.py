import sys
import pika
import mysql.connector
from mysql.connector import Error
import json

def main():
    # Conexión a la base de datos
    conexion_bd = {
        'host': 'mysql-tarjeta',
        'database': 'bd-tarjeta',
        'user': 'proyecto',
        'password': '12345',
        'port': 3306
    }

    # Conexión a RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-tarjeta', port=5672))
        canal = connection.channel()
        canal.queue_declare(queue='cola-tarjeta')
        print("Conexión a RabbitMQ exitosa")
    except Exception as e:
        print("Error al conectar con RabbitMQ:", e)
        exit(1)

    def callback(ch, method, properties, body):
        mensaje = body.decode('utf-8') # Decodificar el mensaje para obtener el texto en formato JSON

        # Extraer datos del mensaje
        datos_mensaje = json.loads(mensaje) # Convertir el texto JSON a un diccionario de Python
        mensaje_sms = datos_mensaje['mensaje']  # Solo obtener el campo 'mensaje' del diccionario
        numero_telefono = datos_mensaje['numero_telefono'] # Solo obtener el campo 'numero_telefono' del diccionario
        tipo_mensaje = datos_mensaje['tipo'] # Solo obtener el campo 'tipo' del diccionario
        identificador_cola = method.delivery_tag # Obtener el identificador que tiene la cola de mensajes de RabbitMQ para el mensaje actual

        try:
            # Conexión a la base de datos
            conexion = mysql.connector.connect(**conexion_bd)
            cursor = conexion.cursor()

            # Insertar el mensaje en la tabla mensaje_sms
            sql_insert = "INSERT INTO mensaje_sms (numero_telefono, mensaje, estado, identificador_cola, tipo_mensaje) VALUES (%s, %s, %s, %s, %s)"
            # Solo insertar el mensaje extraído
            cursor.execute(sql_insert, (numero_telefono, mensaje_sms, 'pendiente', identificador_cola, tipo_mensaje))
            conexion.commit()
            print("Mensaje insertado en la base de datos")

        except Error as e:
            print(f"Error al conectar a MySQL: {e}")

        finally:
            cursor.close()
            conexion.close()

    canal.basic_consume(queue='cola-tarjeta', on_message_callback=callback, auto_ack=True)

    print('Esperando mensajes. Para salir presiona CTRL+C')
    canal.start_consuming()

if __name__ == '__main__':
    # Llamar al método principal y luego dar control c y salir
    try:
        main()
    except KeyboardInterrupt:
        print('Interrumpido')
        try:
            sys.exit(0)  # Salir con código de éxito
        except SystemExit:
            sys.exit(0)