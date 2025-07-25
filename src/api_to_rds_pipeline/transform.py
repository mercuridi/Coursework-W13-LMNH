"""Transforms a list of dictionaries containing plant data into a clean dataframe,
ensuring essential data is there and validating types and values"""
import logging

import pandas as pd


class PlantDataTransformer:
    """Has properties plant_data: raw input, and df: transformed output"""

    def __init__(self, plant_data: list[dict]):
        logging.info("Constructing transformer class")
        self.plant_data = plant_data
        self.df = pd.DataFrame()
        logging.info("Transformer constructed")
        logging.debug("Received data:")
        logging.debug(self.plant_data)

    def create_dataframe(self):
        """Create dataframe with correct column names from a list of nested dictionaries
        Skips plant if it's missing an ID, temp, moisture, or recording timestamp"""
        logging.info("Creating cleaned dataframe")
        unnested_data = []
        for plant in self.plant_data:
            logging.debug("Current row: %s", plant)
            try:
                image = plant.get("images", {})
                unnested_data.append({
                    "plant_id": plant["plant_id"],  # required
                    "english_name": plant.get("name"),
                    "soil_temperature": plant["temperature"],  # required
                    "latitude": plant.get("origin_location", {}).get("latitude"),
                    "longitude": plant.get("origin_location", {}).get("longitude"),
                    "city_name": plant.get("origin_location", {}).get("city"),
                    "country_name": plant.get("origin_location", {}).get("country"),
                    "botanist_name": plant.get("botanist", {}).get("name"),
                    "botanist_email": plant.get("botanist", {}).get("email"),
                    "botanist_phone": plant.get("botanist", {}).get("phone"),
                    "last_watered": plant.get("last_watered"),
                    "soil_moisture": plant["soil_moisture"],  # required
                    "reading_taken": plant["recording_taken"],  # required
                    "photo_link": image.get("original_url") if isinstance(image, dict) else None,
                    "scientific_name": plant.get("scientific_name")
                })
                logging.debug("Added plant to unnested data list")
            except KeyError as e:
                # Skip if any required fields are missing
                logging.error("Skipping row on missing field: %s", e)
                continue
        logging.info("Converting data list to dataframe")
        self.df = pd.DataFrame(unnested_data)
        logging.info("Conversion complete")
        logging.debug("Converted dataframe:")
        logging.debug(self.df)

    def clean_data(self):
        """Clean the dataframe (e.g. handle nulls, ensure correct data types)"""
        logging.info("Cleaning dataframe")
        start_length = len(self.df)
        logging.info("Dataframe length: %s", start_length)

        # Ensure timestamps are datetime objects, coercing errors to NaN
        for col in ['last_watered', 'reading_taken']:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        logging.info("Converted timestamps to datetime")

        # Ensure readings are floats
        for col in ['soil_temperature', 'soil_moisture']:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        logging.info("Converted readings to numerics")


        # If scientific_name is always in a list on its own
        if 'scientific_name' in self.df.columns:
            self.df['scientific_name'] = self.df['scientific_name'].apply(
                lambda x: x[0].replace("'", '"') if isinstance(x, list) and x else x)
        logging.info("Extracted scientific names from length-1 list")


        # Replace negative moisture with null
        self.df['soil_moisture'] = self.df['soil_moisture'].mask(
            self.df['soil_moisture'] < 0)
        logging.info("Replaced negative moisture values with null")

        # Replace temperatures outside of valid range with null
        self.df['soil_temperature'] = self.df['soil_temperature'].mask(
            (self.df['soil_temperature'] < -10) | (self.df['soil_temperature'] > 60))
        logging.info("Replaced unusual temperature values with null")


        # Drop rows which have a null value for moisture or temperature
        self.df = self.df.dropna(subset=['soil_temperature', 'soil_moisture'])
        logging.info("Dropped rows with a NaN in float columns")
        logging.info("%s rows dropped", start_length - len(self.df))

        logging.info("Data cleaning complete")

    def transform(self) -> pd.DataFrame:
        """Full transformation process and returns the datafram"""
        self.create_dataframe()
        self.clean_data()
        return self.df
