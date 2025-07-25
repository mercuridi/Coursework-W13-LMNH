# pylint: skip-file

import pandas as pd
import pytest
import dotenv

from src.api_to_rds_pipeline.transform import PlantDataTransformer
from src.api_to_rds_pipeline.load import RDS_TABLES_WITH_FK, check_table_name_valid
from test_atr_transform import EXAMPLE

def test_check_table_name_valid_bad_input():
    with pytest.raises(ValueError):
        check_table_name_valid("bad")
    with pytest.raises(ValueError):
        check_table_name_valid(1)
    with pytest.raises(ValueError):
        check_table_name_valid("")
    with pytest.raises(ValueError):
        check_table_name_valid(None)
    with pytest.raises(ValueError):
        check_table_name_valid(True)
    with pytest.raises(ValueError):
        check_table_name_valid(False)

def test_check_table_name_valid_good_input():
    assert check_table_name_valid("country")
    assert check_table_name_valid("city")
    assert check_table_name_valid("origin")
    assert check_table_name_valid("botanist")
    assert check_table_name_valid("plant")
    assert check_table_name_valid("reading")
    assert check_table_name_valid("photo")

