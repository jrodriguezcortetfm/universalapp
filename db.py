
from google.cloud.sql.connector import Connector
import sys
import os

project_id = os.environ.get('PROJECT_ID')
region = os.environ.get('REGION')
instance_name = os.environ.get('INSTANCE_NAME')
instance_connection_name = f"{project_id}:{region}:{instance_name}" 
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME')

# Inicializa Connector object
connector = Connector()

# Función que retorna el objeto de conexión a la base de datos
def getconn():
    print(region, file=sys.stderr)
    print(instance_name, file=sys.stderr)
    print(db_user, file=sys.stderr)
    conn = connector.connect(
        instance_connection_name,
        "pymysql",
        user=db_user,
        password=db_password,
        db=db_name
    )
    return conn
