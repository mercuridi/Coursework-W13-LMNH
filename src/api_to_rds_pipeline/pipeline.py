'''runs full pipeline'''
import logging
import datetime
from dotenv import load_dotenv

from extract import PlantGetter, BASE_ENDPOINT, START_ID, MAX_404_ERRORS
from transform import PlantDataTransformer
from load import DataLoader


def run_pipeline(terminal_output=False):
    """uses etl files to create full pipeline that loads endpoint data to RDS"""
    pipeline_start = datetime.datetime.now()

    # logging handler setup
    logging_handlers = [
        logging.FileHandler(
            filename="logs/pipeline.log",
            mode="w",
            encoding="utf8",
        )
    ]

    # enables terminal output
    # turn on for CloudWatch
    if terminal_output:
        logging_handlers.append(logging.StreamHandler())

    # set up logging
    logging.basicConfig(
        level=logging.INFO,
        handlers= logging_handlers
    )

    # now we're in business
    logging.info("Started execution of pipeline at %s", pipeline_start)
    load_dotenv()


    # extract
    extract_start = datetime.datetime.now()
    getter = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    plants = getter.loop_ids_multi_threaded()
    extract_end = datetime.datetime.now()
    logging.info("Finished execution of extract at %s", extract_end)
    logging.info("Extract timer: %s", extract_end-extract_start)


    # transform
    transform_start = datetime.datetime.now()
    transformer = PlantDataTransformer(plants)
    transformer.transform()
    transform_end = datetime.datetime.now()
    logging.info("Finished execution of transform at %s", transform_end)
    logging.info("Transform timer: %s", transform_end-transform_start)


    # load
    load_start = datetime.datetime.now()
    loader = DataLoader(transformer.df)
    loader.upload_tables_to_rds()
    load_end = datetime.datetime.now()
    logging.info("Finished execution of load at %s", load_end)
    logging.info("Load timer: %s", load_end-load_start)


    pipeline_end = datetime.datetime.now()
    logging.info("Finished execution of pipeline at %s", pipeline_end)
    logging.info("Pipeline timer: %s", pipeline_end-pipeline_start)


def handler(event, context):
    """handler function for lambda function"""
    try:
        run_pipeline()
        print(f"{event} : Lambda time remaining in MS:",
              context.get_remaining_time_in_millis())
        return {"statusCode": 200}
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

if __name__ == "__main__":
    run_pipeline()
