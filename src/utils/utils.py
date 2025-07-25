"""File for code used in multiple different files"""

import os
import dotenv

import pymssql

def get_conn():
    """Gets a connection to the RDS with local .env"""
    dotenv.load_dotenv()
    return pymssql.connect(
            os.environ["DB_HOST"],
            os.environ["DB_USER"],
            os.environ["DB_PASSWORD"],
            os.environ["DB_NAME"]
        )
