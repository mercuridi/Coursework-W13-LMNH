"""Transforms a list of dictionaries containing plant data into a clean dataframe,
ensuring essential data is there and validating types and values"""
import pandas as pd


class PlantDataTransformer:
    """Has properties plant_data: raw input, and df: transformed output"""

    def __init__(self, plant_data: list[dict]):
        self.plant_data = plant_data
        self.df = pd.DataFrame()

    def create_dataframe(self):
        """Create dataframe with correct column names from a list of nested dictionaries
        Skips plant if it's missing an ID, temp, moisture, or recording timestamp"""
        unnested_data = []
        for plant in self.plant_data:
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
                    "image_link": image.get("original_url") if isinstance(image, dict) else None,
                    "scientific_name": plant.get("scientific_name")
                })
            except KeyError:
                # Skip if any required fields are missing
                continue
        self.df = pd.DataFrame(unnested_data)

    def clean_data(self):
        """Clean the dataframe (e.g. handle nulls, ensure correct data types)"""

        # Ensure timestamps are datetime objects, coercing errors to NaN
        for col in ['last_watered', 'reading_taken']:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        # Ensure readings are floats
        for col in ['soil_temperature', 'soil_moisture']:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # If scientific_name is always in a list on its own
        if 'scientific_name' in self.df.columns:
            self.df['scientific_name'] = self.df['scientific_name'].apply(
                lambda x: x[0] if isinstance(x, list) and x else x)

        # Replace negative moisture with null
        self.df['soil_moisture'] = self.df['soil_moisture'].mask(
            self.df['soil_moisture'] < 0)

        # Replace temperatures outside of valid range with null
        self.df['soil_temperature'] = self.df['soil_temperature'].mask(
            (self.df['soil_temperature'] < -10) | (self.df['soil_temperature'] > 60))

    def transform(self) -> pd.DataFrame:
        """Full transformation process and returns the datafram"""
        self.create_dataframe()
        self.clean_data()
        return self.df
