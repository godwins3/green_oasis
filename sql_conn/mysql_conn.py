import mysql.connector
from sql_conn.python_mysql_dbconfig import read_db_config


def create(database="tamu"):
    dbconfig = read_db_config()
    conn = mysql.connector.connect(user=dbconfig["user"], password=dbconfig["password"],
                                   host=dbconfig["host"], database=database, autocommit=True)

    return conn
