"""Extract plant data from endpoints"""
import requests
import logging
from multiprocessing import Pool

BASE_ENDPOINT = "https://sigma-labs-bot.herokuapp.com/api/plants/"
START_ID = 1
MAX_404_ERRORS = 5
MAX_ID = 50
MAX_THREADS = 5

class PlantGetter:
    """Gets plant data from different endpoints"""

    def __init__(self, url: str, start: int, max_404: int):
        logging.info("Constructing getter class")
        self.url = url
        self.id = start
        self.max_404 = max_404
        self.consecutive_404 = 0
        self.plant_data = []
        self.endpoints = [i for i in range(START_ID, MAX_ID)]
        logging.info("Getter constructed")
        logging.info("Max consecutive 404s: %s", self.max_404)

    def get_plant(self, id: int) -> dict:
        """Returns data for specific id endpoint, or a dictionary detailing the error
        if it was not a successful request"""
        logging.debug("Constructing endpoint")
        endpoint = f'{self.url}{id}'
        logging.debug("Getting plant ID %s from endpoint: %s", id, endpoint)
        try:
            response = requests.get(endpoint, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data
            logging.error("Endpoint 404 error at ID %s", id)
            return {"error": "404 Not Found", "id": id}
        except requests.exceptions.RequestException:
            logging.error("Endpoint request exception")
            return {"error": "Request Exception", "id": id}

    def loop_ids_single_threaded(self) -> list[dict]:
        """Loops through endpoints, stopping after a certain number of failed requests"""
        logging.info("Looping over IDs - single-thread")
        while self.consecutive_404 < self.max_404:
            data = self.get_plant(self.id)
            logging.debug("Obtained data: %s", data)
            if "error" not in data:
                logging.debug("No error detected in data")
                self.plant_data.append(data)
                self.consecutive_404 = 0
            else:
                self.consecutive_404 += 1
                logging.error("Consecutive 404s: %s", self.consecutive_404)
            self.id += 1
            logging.debug("Next endpoint ID: %s", self.id)
        logging.info("Finished looping IDs")
        return self.plant_data
    
    def loop_ids_multi_threaded(self) -> list[dict]:
        """Loops through endpoints with a multithreaded approach"""
        logging.info("Looping over IDs - multi-threaded")
        with Pool(MAX_THREADS) as p:
            result = p.map(self.get_plant, self.endpoints)
        logging.info("Finished looping IDs")
        self.plant_data = result
        return self.plant_data

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename="logs/extract.log",
        filemode="w",
        encoding="utf8"
    )
    getter = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    plants = getter.loop_ids_multi_threaded()
