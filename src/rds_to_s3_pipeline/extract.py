"""Extracts all metadata from """
import os
import logging
import pandas as pd
from dotenv import load_dotenv

from src.utils.utils import get_conn


class RDSDataGetter:
    """gets data from RDS"""
    METADATA_TABLES = ['botanist', 'country',
                       'city', 'origin', 'photo', 'plant']

    def __init__(self):
        load_dotenv()
        self.conn = pymssql.connect(
            os.environ["DB_HOST"],
            os.environ["DB_USER"],
            os.environ["DB_PASSWORD"],
            os.environ["DB_NAME"]
        )

        logging.info("Connected to RDS")

    def get_metadata(self) -> dict[str, pd.DataFrame]:
        """gets all metadata tables"""
        conn = self.conn
        cursor = conn.cursor()
        df_dict = {}
        try:
            for table in self.METADATA_TABLES:
                logging.info(f"Querying {table} table")
                query = f"SELECT * FROM {table};"
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                df_dict[table] = df
        finally:
            cursor.close()
            logging.info("Cursor closed")
        return df_dict

    def get_readings(self) -> dict[str, pd.DataFrame]:
        """gets reading table from yesterday and closes connection"""
        conn = self.conn
        cursor = conn.cursor()
        df_dict = {}
        try:
            logging.info(f"Querying readings table")
            query = """
            SELECT * FROM reading
            WHERE reading_taken >= CAST(DATEADD(DAY, -1, CAST(GETDATE() AS DATE)) AS DATETIME)
            AND reading_taken < CAST(GETDATE() AS DATE);
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            df_dict['reading'] = df
        finally:
            cursor.close()
            logging.info("Cursor closed")
            conn.close()
            logging.info("Connection closed")
        return df_dict

    def get_all_data(self) -> dict[str, pd.DataFrame]:
        """gets all data """
        meta = self.get_metadata()
        readings = self.get_readings()
        meta.update(readings)
        logging.info("Extracted all data")
        return meta


if __name__ == "__main__":
    get = RDSDataGetter()
    TAB = get.get_all_data()
    print(TAB)
