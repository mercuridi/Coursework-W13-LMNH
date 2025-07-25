"""Script to load cleaned data into the SQL Server RDS"""
import os
import logging

import pandas as pd
import numpy as np
import pymssql

from src.utils.utils import get_conn

# expose the ERD as a dictionary
RDS_TABLES_WITH_FK = {
    "country": [
        "country_name"
    ],
    "city": [
        "city_name",
        "country_id"
    ],
    "origin": [
        "latitude",
        "longitude",
        "city_id"
    ],
    "botanist": [
        "botanist_name",
        "botanist_email",
        "botanist_phone"
    ],
    "plant": [
        "english_name",
        "scientific_name",
        "origin_id"
    ],
    "reading": [
        "reading_taken",
        "last_watered",
        "soil_moisture",
        "soil_temperature",
        "plant_id",
        "botanist_id"
    ],
    "photo": [
        "plant_id",
        "photo_link"
    ]
}

# Mapping of the foreign keys each table has
# Used to "plan" recursion paths
TABLE_DEPENDENCIES = {
    "country": [],
    "city": [
        "country"
    ],
    "origin": [
        "city"
    ],
    "botanist": [],
    "plant": [
        "origin"
    ],
    "reading": [
        "plant",
        "botanist"
    ],
    "photo": [
        "plant",
    ]
}


class DataLoader:
    """Class which handles the loading of a clean dataframe to the RDS"""

    def __init__(self, df: pd.DataFrame):
        """Constructor for class"""
        logging.info("Constructing loader class")
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Input to load stage must be a dataframe; received {type(df)}")
        if len(df) == 0:
            raise ValueError("Dataframe must contain data.")

        self.api_data = df
        self.conn = get_conn()

        self.remote_tables: dict[pd.DataFrame] = {}
        self.update_tables()
        logging.info("Loader constructed")
        logging.debug(self)


    def update_table(self, table_name: str) -> pd.DataFrame:
        """Function to quickly update a specific local table using RDS data"""
        self.check_table_name_valid(table_name)
        logging.debug("Updating local record of table %s", table_name)
        cur = self.conn.cursor(as_dict=True)
        cur.execute(f"select * from {table_name};")
        data = pd.DataFrame(cur.fetchall())
        cur.close()
        self.remote_tables[table_name] = data
        logging.debug("Table record updated")


    def update_tables(self):
        """Function to quickly update & overwrite all the local tables"""
        logging.info("Updating all local records of the remote RDS table")
        for key in RDS_TABLES_WITH_FK:
            self.update_table(key)


    def upload_tables_to_rds(self):
        """Inserts fresh data into the RDS; skips addition if exact row already exists"""
        logging.info("Adding all rows to the RDS")

        logging.debug("Adding rows for reading table")
        self.api_data.apply(lambda x: self.add_row(x, "reading"), axis=1)

        logging.debug("Adding rows for photo table")
        self.api_data.apply(lambda x: self.add_row(x, "photo"), axis=1)

        logging.info("Added all rows")

        self.close_conn()


    def add_row(self, row: pd.DataFrame, table_name: str, level=0) -> int:
        """Adds a single row of data to a remote table"""
        # logging.debug("Getting IDs for row %s", row)
        logging.debug("!!! RECURSION LEVEL: %s", level)
        logging.debug("Now searching table %s", table_name)
        table_columns = RDS_TABLES_WITH_FK[table_name]
        for dependency in TABLE_DEPENDENCIES[table_name]:
            logging.debug("Dependency for table %s found: %s", table_name, dependency)
            row[f"{dependency}_id"] = self.add_row(row, dependency, level=level+1)

        val = self.fetch_id(row, table_name, table_columns)
        if not isinstance(val, np.int64):
            logging.debug("No value found, adding to table to fetch foreign key ID")

            logging.debug("Constructing query")
            query_string = f"insert into {table_name} ({', '.join(table_columns)}) values ({', '.join(['%s' for _ in range(len(table_columns))])});"
            logging.debug("Query string:")
            logging.debug(query_string)

            logging.debug("Constructing params")
            query_params = [str(row[k]) if str(row[k]) != "nan" else "NULL" for k in table_columns]
            logging.debug("Params for query:")
            logging.debug(query_params)

            logging.debug("Executing query")
            cur = self.conn.cursor()
            cur.execute(
                operation=query_string,
                params=query_params
            )
            self.conn.commit()
            logging.debug("Query executed")

            self.update_table(table_name)
            val = self.fetch_id(row, table_name, table_columns)
            logging.debug("Returning newly inserted ID: %s", val)

        logging.debug("Returning %s ID", table_name)
        logging.debug("Value type: %s", type(val))
        logging.debug("End of recursion level %s", level)

        return val


    def fetch_id(self, row: pd.DataFrame, table_name: str, table_columns: list[str]) -> int:
        """Wrapper to neatly fetch an ID"""
        logging.debug("Attempting to grab %s ID", table_name)
        table = self.remote_tables[table_name]
        try:
            # "Expected" behaviour
            val = table.loc[table[table_columns[0]] == row[table_columns[0]]]["id"].iloc[0]
        except IndexError:
            # I think happens when the target is an integer?
            val = table.loc[table[table_columns[0]] == row[table_columns[0]]]["id"]
            logging.debug("Error handled: value is not in a series OR column is empty")
        except KeyError:
            # happens when the database is completely empty
            val = 0
            logging.debug("Error handled: database table is empty AND/OR column does not exist")

        if isinstance(val, pd.Series):
            val = 0
            logging.debug("Value found is a series; returning 0")

        logging.debug("ID for %s: %s", table_name, val)
        return val
    

    def check_table_name_valid(self, table_name: str):
        """Check if a table name is in the list of known tables before we try to query it"""
        logging.debug("Checking table name %s is valid", table_name)
        if table_name not in RDS_TABLES_WITH_FK:
            raise ValueError(f"Given table name {table_name} is not a known destination")
        logging.debug("Table name OK")


    def close_conn(self):
        """Closes the self-held database connection"""
        logging.info("Closing RDS connection")
        self.conn.close()
        logging.info("RDS connection closed")


# Example usage

# Load .env
# dotenv.load_dotenv()

# Initialise loader object
# loader = DataLoader(df)

# Call upload driver
# loader.upload_tables_to_rds()
