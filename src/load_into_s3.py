'''Receiving dictionary with keys containing table names, 
and values containing dataframes of the tables' data'''
import os
from datetime import datetime
import pandas as pd
import boto3
import awswrangler as wr
import pymssql

BUCKET = ""
METADATA_TABLE_NAMES = ['plant', 'botanist', 'photo',
                        'origin', 'city', 'country']
DATABASE = ""


class DataLoader:
    """Class which handles the loading of dataframes into the S3 bucket"""

    def __init__(self, df_dict: dict[str, pd.DataFrame], bucket: str, database: str):

        self.df_dict = df_dict
        self.bucket = bucket
        self.database = database

        self.session = boto3.Session()
        creds = self.session.get_credentials()
        if creds is None:
            print("Error: AWS credentials not found.")

        self.conn = pymssql.connect(
            os.environ["DB_HOST"],
            os.environ["DB_USER"],
            os.environ["DB_PASSWORD"],
            os.environ["DB_NAME"]
        )

    def upload_metadata(self, table_name: str, df: pd.DataFrame):
        '''Uploads metadata to ensure S3 bucket is all up-to-date
        Metadata includes: plant, botanist, photo, origin, city, country'''
        path = f"s3://{self.bucket}/input/{table_name}/{table_name}.parquet"

        wr.s3.to_parquet(df, path=path, dataset=False, index=False,
                         boto3_session=self.session)

        print(f'{df} uploaded to {self.bucket} bucket!')

    def upload_reading_data(self, df: pd.DataFrame):
        '''Uploads all the reading data '''
        df['year'] = df['recording_taken'].dt.year
        df['month'] = df['recording_taken'].dt.month
        df['day'] = df['recording_taken'].dt.day

        wr.s3.to_parquet(df, path=f's3://{self.bucket}/input/reading',
                         dataset=True, partition_cols=['year', 'month', 'day'],
                         mode='append', boto3_session=self.session)

        print(f'Readings uploaded to {self.bucket}, bucket!')

    def upload_summary_data(self, df: pd.DataFrame):
        '''Uploads small summary dataframe to S3 bucket
        Partitions by day, using the date column in the summary: YYYYMMDD'''
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day

        wr.s3.to_parquet(df, path=f's3://{self.bucket}/input/summary',
                         dataset=True, partition_cols=['year', 'month', 'day'],
                         mode='append', boto3_session=self.session)

        print(f'Summaries uploaded to {self.bucket}, bucket!')

    def get_latest_reading_taken(self) -> str:
        '''Query S3 bucket for timestamp of latest reading'''
        query = "SELECT MAX(reading_taken) AS latest FROM reading"

        df = wr.athena.read_sql_query(
            sql=query,
            database=self.database,
            ctas_approach=False,  # just need the result
            s3_output=f's3://{self.bucket}/output',
            boto3_session=self.session
        )

        latest = df.loc[0, 'latest']

        # ensuring the correct format is returned as a string
        if isinstance(latest, pd.Timestamp):
            return latest.strftime('%Y-%m-%d %H:%M:%S')
        return str(latest)

    def delete_old_readings(self, latest_reading_taken):
        '''Using the latest reading in S3, deleted all older readings from RDS'''
        timestamp = datetime.strptime(
            latest_reading_taken, "%Y-%m-%d %H:%M:%S")

        cursor = self.conn.cursor()

        delete_query = """DELETE FROM reading
                        WHERE reading_taken < %s"""

        cursor.execute(delete_query, (timestamp,))
        deleted_count = cursor.rowcount

        self.conn.commit()
        cursor.close()

        return deleted_count

    def load(self):
        '''Uploads metadata, yesterday's summary and reading data to the S3 bucket
        Then deletes all old data from RDS'''
        for key in METADATA_TABLE_NAMES:
            self.upload_metadata(key, self.df_dict[key])

        self.upload_reading_data(self.df_dict['reading'])
        self.upload_summary_data(self.df_dict['summary'])

        # clean up
        latest = self.get_latest_reading_taken()
        print(f"Latest reading_taken in S3: {latest}")

        deleted = self.delete_old_readings(latest)
        self.conn.close()
        print(f"Deleted {deleted} rows from RDS older than {latest}")


# loader = DataLoader(df_dict, BUCKET, DATABASE)
# loader.load()
