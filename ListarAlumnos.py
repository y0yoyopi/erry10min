import boto3
import pymysql
import os

def lambda_handler(event, context):
    # Parámetros de conexión (puedes usar Parameter Store o Secrets Manager para mayor seguridad)
    SSM_host = os.environ['DB_HOST']
    user = os.environ['DB_USER']
    SSM_password = os.environ['DB_PASSWORD']
    database = os.environ['DB_NAME']

    # Recuperar los secretos
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=SSM_host,
        WithDecryption=True  # Si es un parámetro seguro
    )
    host = response['Parameter']['Value']
    response = ssm.get_parameter(
        Name=SSM_password,
        WithDecryption=True  # Si es un parámetro seguro
    )
    password = response['Parameter']['Value']

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")  # Ajusta el nombre de la tabla según tu caso
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()