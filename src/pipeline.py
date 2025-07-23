'''runs full pipeline'''
import logging
import datetime
from dotenv import load_dotenv

from extract import PlantGetter, BASE_ENDPOINT, START_ID, MAX_404_ERRORS
from transform import PlantDataTransformer
from load import DataLoader


def run_pipeline(terminal_output=False):
    """uses etl files to create full pipeline that loads endpoint data to RDS"""
    start = datetime.datetime.now()

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
    logging.info("Started execution of pipeline at %s", start)
    load_dotenv()

    # extract
    getter = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    plants = getter.loop_ids()

    # transform
    transformer = PlantDataTransformer(plants)
    transformer.transform()

    # load
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