# pylint: skip-file

import pandas as pd
import pytest

from src.rds_to_s3_pipeline.transform import TransformRDSData

@pytest.fixture
def sample_df_dict():

    data = [
        {
            "reading_taken": "2025-07-22 08:00:00",
            "last_watered": "2025-07-22 06:00:00",
            "soil_moisture": 0.3,
            "soil_temperature": 22.5,
            "plant_id": 1,
            "botanist_id": 101
        },
        {
            "reading_taken": "2025-07-22 10:00:00",
            "last_watered": "2025-07-22 08:30:00",
            "soil_moisture": 0.4,
            "soil_temperature": 23.0,
            "plant_id": 1,
            "botanist_id": 101
        },
        {
            "reading_taken": "2025-07-22 09:00:00",
            "last_watered": "2025-07-21 20:00:00",
            "soil_moisture": 0.5,
            "soil_temperature": 21.0,
            "plant_id": 2,
            "botanist_id": 102
        }
    ]
    df = pd.DataFrame(data)
    return {"reading": df, 'botanist': 'neil', 'plant': 'cabbage', 'photo': '.jpg', 'city': 'porto', 'origin': 'europe', 'country': 'portugal'}


def test_summary_output_shape(sample_df_dict):
    transformer = TransformRDSData(sample_df_dict)
    summary = transformer.create_summary()
    assert isinstance(summary, pd.DataFrame)
    assert set(summary.columns) == {
        'plant_id', 'mean_soil_moisture', 'mean_soil_temperature',
        'date', 'watering_count', 'most_recent'
    }
    assert summary.shape[0] == 2


def test_mean_soil_values(sample_df_dict):
    transformer = TransformRDSData(sample_df_dict)
    summary = transformer.create_summary()
    plant_1 = summary[summary['plant_id'] == 1].iloc[0]
    assert plant_1['mean_soil_moisture'] == 0.35
    assert plant_1['mean_soil_temperature'] == 22.75


def test_watering_count(sample_df_dict):
    transformer = TransformRDSData(sample_df_dict)
    summary = transformer.create_summary()
    assert summary.loc[summary['plant_id'] == 1, 'watering_count'].item() == 2
    assert summary.loc[summary['plant_id'] == 2, 'watering_count'].item() == 0


def test_most_recent_watering(sample_df_dict):
    transformer = TransformRDSData(sample_df_dict)
    summary = transformer.create_summary()
    recent = pd.to_datetime("2025-07-22 08:30:00")
    assert pd.to_datetime(
        summary.loc[summary['plant_id'] == 1, 'most_recent'].item()) == recent


def test_final_dict_has_summary(sample_df_dict):
    transformer = TransformRDSData(sample_df_dict)
    transformed_dict = transformer.transformed_data()
    keys = {'reading', 'plant', 'photo', 'origin',
            'city', 'country', 'botanist', 'summary'}
    assert set(transformed_dict.keys()) == keys
