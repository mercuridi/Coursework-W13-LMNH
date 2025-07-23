"""Script to load cleaned data into the SQL Server RDS"""
import os 
import logging

import dotenv
import pandas as pd
import numpy as np
import pymssql

from transform import PlantDataTransformer

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
        self.conn = pymssql.connect(
            os.environ["DB_HOST"],
            os.environ["DB_USER"],
            os.environ["DB_PASSWORD"],
            os.environ["DB_NAME"]
        )

        self.remote_tables: dict[pd.DataFrame] = {}
        self.update_tables()
        logging.info("Loader constructed")
        logging.info(self)


    def update_table(self, table_name: str) -> pd.DataFrame:
        """Function to quickly update a specific local table using RDS data"""
        self.check_table_name_valid(table_name)
        logging.info("Updating local record of table %s", table_name)
        cur = self.conn.cursor(as_dict=True)
        cur.execute(f"select * from {table_name};")
        data = pd.DataFrame(cur.fetchall())
        cur.close()
        self.remote_tables[table_name] = data
        logging.info("Table record updated")


    def update_tables(self):
        """Function to quickly update & overwrite all the local tables"""
        logging.info("Updating all local records of the remote RDS table")
        for key in RDS_TABLES_WITH_FK:
            self.update_table(key)


    def upload_tables_to_rds(self):
        """Inserts fresh data into the RDS; skips addition if exact row already exists"""
        logging.info("Adding all rows to the RDS")

        logging.info("Adding rows for reading table")
        self.api_data.apply(lambda x: self.add_row(x, "reading"), axis=1)

        logging.info("Adding rows for photo table")
        self.api_data.apply(lambda x: self.add_row(x, "photo"), axis=1)

        logging.info("Added all rows")


    def add_row(self, row: pd.DataFrame, table_name: str, level=0) -> int:
        """Adds a single row of data to a remote table"""
        # logging.info("Getting IDs for row %s", row)
        logging.info("\n\n!!! RECURSION LEVEL: %s", level)
        logging.info("Now searching table %s", table_name)
        table_columns = RDS_TABLES_WITH_FK[table_name]
        for dependency in TABLE_DEPENDENCIES[table_name]:
            logging.info("Dependency for table %s found: %s", table_name, dependency)
            row[f"{dependency}_id"] = self.add_row(row, dependency, level=level+1)

        val = self.fetch_id(row, table_name, table_columns)
        if not isinstance(val, np.int64):
            logging.info("No value found, adding to table to fetch foreign key ID")

            logging.info("Constructing query")
            simulated_query = f"insert into {table_name} ({', '.join(table_columns)}) values ('{'\', \''.join([str(row[k]) for k in table_columns])}');"
            logging.info("Query constructed: \n%s", simulated_query)
            logging.info("NOTE: The above query is not what is being executed.")
            logging.info("NOTE: The executed query is properly sanitised with query parameters.")

            cur = self.conn.cursor()
            cur.execute(
                "insert into %s (%s) values ('%s');",
                [
                    table_name,
                    ', '.join(table_columns),
                    '\', \''.join([str(row[k]) for k in table_columns])
                ]
            )
            self.conn.commit()
            logging.info("Query executed")

            self.update_table(table_name)
            val = self.fetch_id(row, table_name, table_columns)
            logging.info("Returning newly inserted ID: %s", val)
    
        logging.info("Returning %s ID", table_name)
        logging.info("Value type: %s", type(val))
        logging.info("End of recursion level %s\n", level)

        return val


    def fetch_id(self, row, table_name, table_columns):
        """Wrapper to neatly fetch an ID"""
        logging.info("Attempting to grab %s ID", table_name)
        table = self.remote_tables[table_name]
        try:
            # "Expected" behaviour
            val = table.loc[table[table_columns[0]] == row[table_columns[0]]]["id"].iloc[0]
        except IndexError:
            # I think happens when the target is an integer?
            val = table.loc[table[table_columns[0]] == row[table_columns[0]]]["id"]
            logging.info("Error handled: value is not in a series OR column is empty")
        except KeyError:
            # happens when the database is completely empty
            val = 0
            logging.info("Error handled: database table is empty AND/OR column does not exist")


        logging.info("ID for %s: %s", table_name, val)
        return val
    

    def check_table_name_valid(self, table_name: str):
        """Check if a table name is in the list of known tables before we try to query it"""
        logging.info("Checking table name %s is valid", table_name)
        if table_name not in RDS_TABLES_WITH_FK:
            raise ValueError(f"Given table name {table_name} is not a known destination")
        logging.info("Table name OK")


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
