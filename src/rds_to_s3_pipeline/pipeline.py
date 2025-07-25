"""complete pipeline"""
from extract import RDSDataGetter
from transform import TransformRDSData


def run_pipeline():
    """runs the whole pipeline"""
    getter = RDSDataGetter()
    tables = getter.get_all_data()
    transformer = TransformRDSData(tables)
    _ = transformer.transformed_data()
    # add load
