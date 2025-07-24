"""complete pipeline"""
from src.rds_to_s3_pipeline.extract import RDSDataGetter
from src.rds_to_s3_pipeline.transform import TransformRDSData


def run_pipeline():
    """runs the whole pipeline"""
    getter = RDSDataGetter()
    tables = getter.get_all_data()
    transformer = TransformRDSData(tables)
    transformed = transformer.transformed_data()
    # add load
