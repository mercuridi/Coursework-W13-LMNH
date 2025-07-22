"""Script to load cleaned data into the SQL Server RDS"""

"""
(DONE) Takes in a dataframe of all the data we need
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
(DONE) Closes connections gracefully
"""

import os 

import dotenv
import pandas as pd
import pymssql

class DataLoader:
    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Input to load stage must be a dataframe; received {type(df)}")
        if len(df) == 0:
            raise ValueError("Dataframe must contain data.")

        self.data = df
        self.conn = pymssql.connect(
            os.environ["DB_HOST"],
            os.environ["DB_USER"],
            os.environ["DB_PASSWORD"],
            os.environ["DB_NAME"]
        )

        self.queries = {}
    
    def close_conn(self):
        self.conn.close()
    
    def collect_queries(self):
        cur = self.conn.cursor()
        cur.execute("select * from country;")
        vals = cur.fetchall()
        print(vals)

if __name__ == "__main__":
    dotenv.load_dotenv()
    df = pd.DataFrame()
    loader = DataLoader(df)
    loader.collect_queries()
