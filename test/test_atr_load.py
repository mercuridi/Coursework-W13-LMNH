# pylint: skip-file

import pandas as pd
import pytest

from src.api_to_rds_pipeline.transform import PlantDataTransformer
from src.api_to_rds_pipeline.load import RDS_TABLES_WITH_FK, DataLoader
from test_atr_transform import EXAMPLE

@pytest.fixture
def dataloader():
    transformer = PlantDataTransformer(EXAMPLE)
    return DataLoader(transformer.transform())

def test_check_table_name_valid_bad_input(dataloader):
    with pytest.raises(ValueError):
        dataloader.check_table_name_valid("bad")
    with pytest.raises(ValueError):
        dataloader.check_table_name_valid(1)
    with pytest.raises(ValueError):
        dataloader.check_table_name_valid("")
    with pytest.raises(ValueError):
        dataloader.check_table_name_valid(None)
    with pytest.raises(ValueError):
        dataloader.check_table_name_valid(True)
    with pytest.raises(ValueError):
        dataloader.check_table_name_valid(False)

def test_check_table_name_valid_good_input(dataloader):
    assert dataloader.check_table_name_valid("country")
    assert dataloader.check_table_name_valid("city")
    assert dataloader.check_table_name_valid("origin")
    assert dataloader.check_table_name_valid("botanist")
    assert dataloader.check_table_name_valid("plant")
    assert dataloader.check_table_name_valid("reading")
    assert dataloader.check_table_name_valid("photo")

