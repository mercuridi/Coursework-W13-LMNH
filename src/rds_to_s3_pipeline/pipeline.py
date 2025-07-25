"""complete pipeline"""
from extract import RDSDataGetter
from transform import TransformRDSData
from load import DataLoader, BUCKET, METADATA_TABLE_NAMES, DATABASE


def run_pipeline():
    """runs the whole pipeline"""
    getter = RDSDataGetter()
    tables = getter.get_all_data()
    transformer = TransformRDSData(tables)
    transformed = transformer.transformed_data()
    loader = DataLoader(transformed, BUCKET, DATABASE)
    loader.load()
