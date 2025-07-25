import pymssql
import os
from dotenv import load_dotenv
import pandas as pd


def get_connection():
    load_dotenv()
    conn = pymssql.connect(
        os.environ["DB_HOST"],
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_NAME"]
    )
    return conn


def load_from_rds() -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT id, english_name
            FROM plant"""
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()
        conn.close()
    return df


data = load_from_rds()
print(data)
