import boto3
import pymysql
import random
import string
import os

def generar_password(longitud=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(longitud))

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    environments = ['dev', 'test', 'prod']
    
    # Obtener host y password de admin
    host = ssm.get_parameter(Name='/rds_mysql_alumnos/punto_enlace', WithDecryption=True)['Parameter']['Value']
    admin_pass = ssm.get_parameter(Name='/rds_mysql_alumnos/admin/password', WithDecryption=True)['Parameter']['Value']
    admin_user = 'admin'
    
    # Conexión como admin
    conn = pymysql.connect(
        host=host,
        user=admin_user,
        password=admin_pass,
        db='mysql',  # db mínima para loguearse
        connect_timeout=5
    )

    try:
        with conn.cursor() as cursor:
            for env in environments:
                user = f"user_{env}"
                param_name = f"/rds_mysql_alumnos/{user}/password"

                # Generar nueva contraseña
                nueva_clave = generar_password()
                print(f"Rotando {user} -> {nueva_clave}")

                # Cambiar en MySQL
                cursor.execute(f"ALTER USER '{user}'@'%' IDENTIFIED BY '{nueva_clave}';")
                conn.commit()

                # Actualizar en Parameter Store
                ssm.put_parameter(
                    Name=param_name,
                    Value=nueva_clave,
                    Type='SecureString',
                    Overwrite=True
                )

        return {"statusCode": 200, "body": "Contraseñas rotadas exitosamente."}
    
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}
    
    finally:
        conn.close()
