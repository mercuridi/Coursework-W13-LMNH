'''runs full pipeline'''
from extract_script import PlantGetter, BASE_ENDPOINT, START_ID, MAX_404_ERRORS
from transform import PlantDataTransformer


def run_pipeline():
    """uses etl files to create full pipeline that loads endpoint data to RDS"""
    getter = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    plants = getter.loop_ids()
    transformer = PlantDataTransformer(plants)
    transformer.transform()


def handler(event, context):
    """handler function for lambda function"""
    try:
        run_pipeline()
        print(f"{event} : Lambda time remaining in MS:",
              context.get_remaining_time_in_millis())
        return {"statusCode": 200}
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}
