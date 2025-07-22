"""Script to load cleaned data into the SQL Server RDS"""
import os 

import dotenv
import boto3
import pymssql

def main():
    """
    (WORK) Takes in a dataframe of all the data we need
    (WORK) Construct insertion queries from the dataframe in a dict
    (WORK)    Country insertions
    (WORK)    City insertions
    (WORK)    Origin insertions
    (WORK)    Plant insertions
    (WORK)    Photo insertions
    (WORK)    Botanist insertions
    (WORK)    Reading insertions
    (DONE) Makes a connection to the RDS
    (WORK) Runs insertions
    (WORK) Closes connections gracefully
    """
    conn = get_rds_conn()
    cur = conn.cursor()
    cur.execute("select * from country;")
    vals = cur.fetchall()
    print(vals)


def get_rds_conn():
    """
    Function to easily get an RDS connection
    Requires the .env to be loaded
    """
    return pymssql.connect(
        os.environ["DB_HOST"],
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_NAME"]
    )

if __name__ == "__main__":
    dotenv.load_dotenv()
    main()