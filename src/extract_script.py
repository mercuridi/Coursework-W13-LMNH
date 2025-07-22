"""Extract plant data from endpoints"""
import requests
BASE_ENDPOINT = "https://sigma-labs-bot.herokuapp.com/api/plants/"
START_ID = 1
MAX_404_ERRORS = 5


class PlantGetter:
    """Gets plant data from different endpoints"""

    def __init__(self, url: str, start: int, max_404: int):
        self.url = url
        self.id = start
        self.max_404 = max_404
        self.consecutive_404 = 0
        self.plant_data = []

    def get_plant(self, id: int) -> dict:
        """Returns data for specific id endpoint, or none if not a successful request"""
        endpoint = f'{self.url}{id}'
        try:
            response = requests.get(endpoint, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data
            return {"error": "404 Not Found", "id": id}
        except requests.exceptions.RequestException:
            return {"error": "Request Exception", "id": id}

    def loop_ids(self) -> list[dict]:
        """Loops through endpoints, stopping after a certain number of failed requests"""
        while self.consecutive_404 < self.max_404:
            data = self.get_plant(self.id)
            if "error" not in data:
                self.plant_data.append(data)
                self.consecutive_404 = 0
            else:
                self.consecutive_404 += 1
            self.id += 1
        return self.plant_data


if __name__ == "__main__":
    getter = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    plants = getter.loop_ids()
