import pandas as pd

example = {"plant_id": 8, "name": "Bird of paradise", "temperature": 16.29981566929083,
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
           "scientific_name": ["Heliconia schiedeana 'Fire and Ice'"]}


class PlantDataTransformer:
    def __init__(self, plant_data: list[dict]):
        self.plant_data = plant_data

    def create_dataframe(self):
        """Create dataframe with correct column names from a list of nested dictionaries
        Skips plant if it's missing an ID, temp, moisture, or recording timestamp"""
        unnested_data = []
        for plant in self.plant_data:
            try:
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
                    "recording_taken": plant["recording_taken"],  # required
                    "image_link": plant.get("images", {}).get("original_url"),
                    "scientific_name": plant.get("scientific_name")
                })
            except KeyError:
                # Skip if any required fields are missing
                continue
        self.df = pd.DataFrame(unnested_data)

    def clean_data(self):
        """Clean the dataframe (e.g. handle nulls, ensure correct data types)"""

        # Ensure timestamps are datetime objects, coercing errors to NaN
        for col in ['last_watered', 'recording_taken']:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        # Ensure readings are floats
        for col in ['soil_temperature', 'soil_moisture']:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # If scientific_name is always in a list on its own
        if 'scientific_name' in self.df.columns:
            self.df['scientific_name'] = self.df['scientific_name'][0]

        # Ensure positive moisture
        self.df.loc[self.df['soil_moisture'] < 0, 'soil_moisture'] = 0

    def transform(self) -> pd.DataFrame:
        self.create_dataframe()
        self.clean_data()
        return self.df
