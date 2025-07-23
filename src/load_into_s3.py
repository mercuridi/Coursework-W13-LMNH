'''Receiving dictionary with keys containing table names, 
and values containing dataframes of the tables' data'''
from datetime import datetime
import pandas as pd
import boto3
import awswrangler as wr
import pymssql
import os

BUCKET = ""
METADATA_TABLE_NAMES = ['plant', 'botanist', 'photo',
                        'origin', 'city', 'country']
DATABASE = ""


def upload_metadata(bucket: str, table_name: str, df: pd.DataFrame, session: boto3.Session):
    '''Uploads metadata to ensure S3 bucket is all up-to-date
    Metadata includes: plant, botanist, photo, origin, city, country'''
    path = f"s3://{bucket}/input/{table_name}/{table_name}.parquet"

    wr.s3.to_parquet(df, path=path, dataset=False, index=False,
                     boto3_session=session)

    print(f'{df} uploaded to {bucket} bucket!')


def upload_reading_data(bucket: str, df: pd.DataFrame, session: boto3.Session):
    '''Uploads all the reading data '''
    df['year'] = df['recording_taken'].dt.year
    df['month'] = df['recording_taken'].dt.month
    df['day'] = df['recording_taken'].dt.day

    wr.s3.to_parquet(df, path=f's3://{bucket}/input/reading',
                     dataset=True, partition_cols=['year', 'month', 'day'],
                     mode='append', boto3_session=session)

    print(f'Readings uploaded to {bucket}, bucket!')


def upload_summary_data(bucket: str, df: pd.DataFrame, session: boto3.Session):
    '''Uploads small summary dataframe to S3 bucket
    Partitions by day, using the date column in the summary: YYYYMMDD'''
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day

    wr.s3.to_parquet(df, path=f's3://{bucket}/input/summary',
                     dataset=True, partition_cols=['year', 'month', 'day'],
                     mode='append', boto3_session=session)

    print(f'Summaries uploaded to {bucket}, bucket!')


def get_latest_reading_taken(bucket: str, database: str, session: boto3.Session) -> str:
    query = f"SELECT MAX(reading_taken) AS latest FROM reading"

    df = wr.athena.read_sql_query(
        sql=query,
        database=database,
        ctas_approach=False,  # just need the result
        s3_output=f's3://{bucket}/output',
        boto3_session=session
    )

    latest = df.loc[0, 'latest']

    # ensuring the correct format is returned as a string
    if isinstance(latest, pd.Timestamp):
        return latest.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(latest)


def get_connection():
    """connects to db"""
    conn = pymssql.connect(
        os.environ["DB_HOST"],
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_NAME"]
    )
    return conn


def delete_old_readings(connection, latest_reading_taken):
    timestamp = datetime.strptime(latest_reading_taken, "%Y-%m-%d %H:%M:%S")

    cursor = connection.cursor()

    delete_query = """DELETE FROM reading
                    WHERE reading_taken < %s"""

    cursor.execute(delete_query, (timestamp,))
    deleted_count = cursor.rowcount

    connection.commit()
    cursor.close()

    return deleted_count


def load(bucket: str, df_dict: dict[str, pd.DataFrame]):
    session = boto3.Session()
    creds = session.get_credentials()
    if creds is None:
        return {"statusCode": 500, "body": "AWS credentials not found."}

    for key in METADATA_TABLE_NAMES:
        upload_metadata(bucket, key, df_dict[key], session)

    upload_reading_data(bucket, df_dict['reading'], session)
    upload_summary_data(bucket, df_dict['summary'], session)

    # clean up
    latest = get_latest_reading_taken(BUCKET, DATABASE, session)
    print(f"Latest reading_taken in S3: {latest}")

    connection = get_connection()
    deleted = delete_old_readings(connection, latest)
    connection.close()
    print(f"Deleted {deleted} rows from RDS older than {latest}")
