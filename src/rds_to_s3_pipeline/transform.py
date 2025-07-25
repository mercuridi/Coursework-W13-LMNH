"""adds summary data to dict"""
import logging
import pandas as pd


class TransformRDSData:
    """class to transform data to include summary"""

    def __init__(self, df_dict: dict[str, pd.DataFrame]):
        self.df_dict = df_dict
        self.readings = df_dict.get('reading')
        logging.info("Constructed transformer")

    def create_summary(self):
        """create summary dataframe"""
        self.readings['reading_taken'] = pd.to_datetime(
            self.readings['reading_taken'])

        self.readings['last_watered'] = pd.to_datetime(
            self.readings['last_watered'])

        self.readings['reading_date'] = self.readings['reading_taken'].dt.date
        self.readings['watered_date'] = self.readings['last_watered'].dt.date

        means = self.readings.groupby('plant_id')[
            ['soil_moisture', 'soil_temperature']].mean().rename(
                columns={
                    'soil_moisture': 'mean_soil_moisture',
                    'soil_temperature': 'mean_soil_temperature'
                })

        date = self.readings.groupby('plant_id')['reading_taken'].first(
        ).reset_index().rename(columns={'reading_taken': 'date'})

        watered_on_the_day = self.readings[self.readings['watered_date']
                                           == self.readings['reading_date']]

        watering_count = watered_on_the_day.groupby(
            'plant_id')['last_watered'].nunique()

        watering_count = watering_count.reset_index().rename(
            columns={'last_watered': 'watering_count'})

        most_recent = self.readings.groupby('plant_id')['last_watered'].max(
        ).reset_index().rename(columns={'last_watered': 'most_recent'})

        summary = means.merge(date, on='plant_id', how='left').merge(
            watering_count, on='plant_id', how='left').merge(most_recent, on='plant_id', how='left')

        summary['watering_count'] = summary['watering_count'].fillna(
            0).astype(int)
        logging.info("Summary created")
        return summary

    def transformed_data(self):
        """returns the entire dataset with summary"""
        summary = self.create_summary()
        self.df_dict['summary'] = summary
        logging.info("Summary added to dictionary")
        return self.df_dict
