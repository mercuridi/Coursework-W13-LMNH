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

import dotenv
import pandas as pd
import pymssql

from transform import PlantDataTransformer

RDS_TABLES = {
    "country": ["country_name"],
    "city": ["city_name"],
    "origin": [],
    "botanist": [],
    "plant": [],
    "reading": [],
    "photo": []
}

# TODO if this makes it into a pull request remember to make fun of me
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

        self.country    = None
        self.city       = None
        self.origin     = None
        self.botanist   = None
        self.plant      = None
        self.reading    = None
        self.photo      = None

        self.update_tables()

    def get_table(self, table_name: str) -> pd.DataFrame:
        """Function to quickly get a table from the RDS as a dataframe"""
        if table_name not in RDS_TABLES:
            raise ValueError(f"Given table name {table_name} is not a known destination")
        cur = self.conn.cursor(as_dict=True)
        cur.execute(f"select * from {table_name};")
        data = pd.DataFrame(cur.fetchall())
        cur.close()
        return data

    def update_tables(self):
        """Function to quickly update all the local tables"""
        # TODO BIG target for optimisation!
        self.country    = self.get_table("country")
        self.city       = self.get_table("city")
        self.origin     = self.get_table("origin")
        self.botanist   = self.get_table("botanist")
        self.plant      = self.get_table("plant")
        self.reading    = self.get_table("reading")
        self.photo      = self.get_table("photo")

    def close_conn(self):
        """Closes the self-held database connection"""
        self.conn.close()

    def collect_queries(self):
        """Adds all the queries to run to the self.queries attribute dictionary"""
        pass

if __name__ == "__main__":

    # TODO remove this for PR
    transformer = PlantDataTransformer(EXAMPLE)
    transformer.create_dataframe()
    df = transformer.df
    # TODO removals end here

    dotenv.load_dotenv()
    loader = DataLoader(df)
    print()
