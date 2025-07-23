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

DF Columns:
plant_id
english_name
soil_temperature
latitude
longitude
city_name
country_name
botanist_name
botanist_email
botanist_phone
last_watered
soil_moisture
recording_taken
image_link
scientific_name
"""

import os 
import logging

import dotenv
import pandas as pd
import numpy as np
import pymssql

from transform import PlantDataTransformer

# dictionary which exposes the ERD as a dictionary
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

RDS_TABLES_WITHOUT_FK = {
    "country": [
        "country_name"
    ],
    "city": [
        "city_name"
    ],
    "origin": [
        "latitude",
        "longitude"
    ],
    "botanist": [
        "botanist_name",
        "botanist_email",
        "botanist_phone"
    ],
    "plant": [
        "english_name",
        "scientific_name"
    ],
    "reading": [
        "reading_taken",
        "last_watered",
        "soil_moisture",
        "soil_temperature"
    ],
    "photo": [
        "photo_link"
    ]
}

# TODO if this EXAMPLE global variable makes it into a pull request remember to make fun of me
EXAMPLE = [{"plant_id": 8, "name": "Bird of paradise", "temperature": 16.29981566929083,
           "origin_location": {"latitude": 54.1635, "longitude": 8.6662, "city": "Edwardfurt", "country": "Liberia"},
            "botanist": {"name": "Bradford Mitchell DVM", "email": "bradford.mitchell.dvm@lnhm.co.uk", "phone": "(230) 859-2277 x3537"},
            "last_watered": "2025-07-21T13:33:20.000Z", "soil_moisture": 32.568384615384616, "recording_taken": "2025-07-22T09:31:22.102Z",
            "images": {"license": 451, "license_name": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
                       "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                       "original_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                       "regular_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                       "medium_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                       "small_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                       "thumbnail": "https://perenual.com/storage/image/upgrade_access.jpg"},
            "scientific_name": ["Heliconia schiedeana 'Fire and Ice'"]}]


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
        logging.info("Updating local record of table %s", table_name)
        self.check_table_name_valid(table_name)
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
        self.api_data["reading_id"] = self.api_data.apply(lambda x: self.add_row(x, "reading"), axis=1)
        logging.info("Added all rows")

    def add_row(self, row: pd.DataFrame, table_name: str, level=0) -> int:
        """what is kai even smoking"""
        # logging.info("Getting IDs for row %s", row)
        logging.info("\n\n!!! RECURSION LEVEL: %s", level)
        logging.info("Now searching table %s", table_name)
        table_columns = RDS_TABLES_WITH_FK[table_name]
        for dependency in TABLE_DEPENDENCIES[table_name]:
            logging.info("Dependency for table %s found: %s", table_name, dependency)
            row[f"{dependency}_id"] = self.add_row(row, dependency, level=level+1)
            logging.info("Recursion level exited\n")

        val = self.fetch_id(row, table_name, table_columns)
        if not isinstance(val, np.int64):
            logging.info("No value found, adding to table to fetch foreign key ID")
            cur = self.conn.cursor()
            query = f"insert into {table_name} ({', '.join(table_columns)}) values ('{'\', \''.join([str(row[k]) for k in table_columns])}');"
            logging.info("Query constructed: \n%s", query)
            cur.execute(query)
            self.conn.commit()
            logging.info("Query executed")
            self.update_table(table_name)
            val = self.fetch_id(row, table_name, table_columns)
            logging.info("Returning newly inserted ID: %s", val)
    
        logging.info("Returning %s ID", table_name)
        logging.info("Value type: %s", type(val))
        return val


    def fetch_id(self, row, table_name, table_columns):
        """Wrapper to neatly fetch an ID"""
        logging.info("Attempting to grab %s ID", table_name)
        table = self.remote_tables[table_name]
        try:
            val = table.loc[table[table_columns[0]] == row[table_columns[0]]]["id"].iloc[0]
        except IndexError:
            val = table.loc[table[table_columns[0]] == row[table_columns[0]]]["id"]
        logging.info("ID for %s: %s", table_name, val)
        return val
    

    def check_table_name_valid(self, table_name: str):
        logging.info("Checking table name %s is valid", table_name)
        if table_name not in RDS_TABLES_WITH_FK:
            raise ValueError(f"Given table name {table_name} is not a known destination")
        logging.info("Table name OK")



    def close_conn(self):
        """Closes the self-held database connection"""
        logging.info("Closing RDS connection")
        self.conn.close()
        logging.info("RDS connection closed")


if __name__ == "__main__":
    logging.basicConfig(
        filename="logs/load.log",
        filemode="w",
        encoding="utf8",
        level=logging.INFO
    )

    # TODO remove this for PR
    transformer = PlantDataTransformer(EXAMPLE)
    transformer.create_dataframe()
    ex = transformer.df
    # TODO removals end here

    logging.info("Loading .env")
    dotenv.load_dotenv()

    logging.info("Initialising loader object")
    loader = DataLoader(ex)

    logging.info("Calling upload driver")
    loader.upload_tables_to_rds()
