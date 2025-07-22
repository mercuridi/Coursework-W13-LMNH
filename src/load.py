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

        self.remote_tables = {}
        self.update_tables()

    def update_table(self, table_name: str) -> pd.DataFrame:
        """Function to quickly update a local table using RDS data"""
        if table_name not in RDS_TABLES:
            raise ValueError(f"Given table name {table_name} is not a known destination")
        cur = self.conn.cursor(as_dict=True)
        cur.execute(f"select * from {table_name};")
        data = pd.DataFrame(cur.fetchall())
        cur.close()
        return data


    def update_cities(self, table_name: str) -> None:
        """Function to update remote city data"""
        unique_cities_api = set(self.api_data["city_name"])
        query = f"""
        BEGIN
            IF NOT EXISTS (SELECT * FROM {table_name}
                        WHERE De = @_DE
                        AND Assunto = @_ASSUNTO
                        AND Data = @_DATA)
                BEGIN
                    INSERT INTO {table_name} ({", ".join(RDS_TABLES[table_name])})
                    VALUES (@_DE, @_ASSUNTO, @_DATA)
                END
            END
        """


    def update_tables(self):
        """Function to quickly update all the local tables"""
        for key in RDS_TABLES:
            self.remote_tables[key] = self.update_table(key)


    def close_conn(self):
        """Closes the self-held database connection"""
        self.conn.close()


if __name__ == "__main__":

    # TODO remove this for PR
    transformer = PlantDataTransformer(EXAMPLE)
    transformer.create_dataframe()
    ex = transformer.df
    # TODO removals end here

    dotenv.load_dotenv()
    loader = DataLoader(ex)
    loader.update_cities()