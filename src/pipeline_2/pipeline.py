"""complete pipeline"""
from extract_from_rds import RDSDataGetter
from transform_rds_data import TransformRDSData


def run_pipeline():
    """runs the whole pipeline"""
    getter = RDSDataGetter()
    tables = getter.get_all_data()
    transformer = TransformRDSData(tables)
    transformed = transformer.transformed_data()
    # add load
