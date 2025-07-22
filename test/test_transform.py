# pylint: skip-file
from src.transform import PlantDataTransformer
import pytest

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


def test_column_names():
    transformer = PlantDataTransformer(EXAMPLE)
    transformer.create_dataframe()
    df = transformer.df
    column_names = list(df.columns)
    assert column_names == ['plant_id', 'english_name', 'soil_temperature',
                            'latitude', 'longitude', 'city_name', 'country_name',
                            'botanist_name', 'botanist_email', 'botanist_phone',
                            'last_watered', 'soil_moisture', 'recording_taken', 'image_link', 'scientific_name']
