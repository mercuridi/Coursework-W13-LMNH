'''Receiving dictionary with keys containing table names, 
and values containing dataframes of the tables' data'''
import pandas as pd
import boto3
import awswrangler as wr

BUCKET = ""
METADATA_TABLE_NAMES = ['plant', 'botanist', 'photo',
                        'origin', 'city', 'country']


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


def load(bucket: str, df_dict: dict[str, pd.DataFrame]):
    session = boto3.Session()
    creds = session.get_credentials()
    if creds is None:
        return {"statusCode": 500, "body": "AWS credentials not found."}

    for key in METADATA_TABLE_NAMES:
        upload_metadata(bucket, key, df_dict[key], session)

    upload_reading_data(bucket, df_dict['reading'], session)
    upload_summary_data(bucket, df_dict['summary'], session)
