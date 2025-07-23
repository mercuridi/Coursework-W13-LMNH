'''runs full pipeline'''
import logging
import datetime
from dotenv import load_dotenv

from extract import PlantGetter, BASE_ENDPOINT, START_ID, MAX_404_ERRORS
from transform import PlantDataTransformer
from load import DataLoader


def run_pipeline():
    """uses etl files to create full pipeline that loads endpoint data to RDS"""
    start = datetime.datetime.now()
    logging.basicConfig(
        filename="logs/pipeline.log",
        filemode="w",
        encoding="utf8",
        level=logging.INFO
    )
    logging.info("Started execution of pipeline at %s", start)
    load_dotenv()
    getter = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    plants = getter.loop_ids()
    transformer = PlantDataTransformer(plants)
    transformer.transform()
    loader = DataLoader(transformer.df)
    loader.upload_tables_to_rds()
    end = datetime.datetime.now()
    logging.info("Finished execution of pipeline at %s", start)
    logging.info("Script timer: %s", end-start)



def handler(event, context):
    """handler function for lambda function"""
    try:
        run_pipeline()
        print(f"{event} : Lambda time remaining in MS:",
              context.get_remaining_time_in_millis())
        return {"statusCode": 200}
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

run_pipeline()