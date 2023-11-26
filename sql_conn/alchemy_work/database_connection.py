import sqlalchemy as db
from sql_conn import python_mysql_dbconfig
import urllib.parse


def connection(database='tamu'):
    key = python_mysql_dbconfig.read_db_config()
    database_password = urllib.parse.quote_plus(key['password'])
    engine = db.create_engine(f"mysql+mysqlconnector://{key['user']}:{database_password}@{key['host']}/{database}")

    conn = engine.connect()
    metadata = db.MetaData()  # extracting the metadata

    return engine, metadata
