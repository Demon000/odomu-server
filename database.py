from mongoengine import connect

from config import DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT


def connect_database_from_config():
    connect(
        db=DB_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
