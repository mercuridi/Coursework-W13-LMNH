# pylint: skip-file
from src.extract_script import PlantGetter, BASE_ENDPOINT, START_ID, MAX_404_ERRORS
import requests


def test_successful_request(requests_mock):
    """checks successful requests are returned"""
    requests_mock.get(f"{BASE_ENDPOINT}1",
                      status_code=200, json={'id': 1, 'name': 'daffodil'})
    pg = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    data = pg.get_plant(1)

    assert data['name'] == "daffodil"
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_unsuccessful_request(requests_mock):
    """checks none is returned for a 404 error"""
    requests_mock.get(f"{BASE_ENDPOINT}1",
                      status_code=404, json={'id': 54, 'error': 'not found'})
    pg = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    data = pg.get_plant(1)

    assert data is None
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_loop_stops_after_5_404s(requests_mock):
    """checks loop returns correct data after stopping"""
    for i in range(1, 4):
        requests_mock.get(f"{BASE_ENDPOINT}{i}", status_code=200, json={
                          'id': f"{i}", "name": "plant"})
    for i in range(4, 4+MAX_404_ERRORS):
        requests_mock.get(f"{BASE_ENDPOINT}{i}", status_code=404, json={
                          'id': f"{i}", "error": "not found"})
    pg = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    data = pg.loop_ids()
    ids = [plant['id'] for plant in data]
    assert len(data) == 3
    assert ids == ['1', '2', '3']
    assert requests_mock.call_count == 8


def test_loop_continues_after_1_404(requests_mock):
    """checks loop carries on searching for endpoints after hitting a 404"""
    for i in range(1, 4):
        requests_mock.get(f"{BASE_ENDPOINT}{i}", status_code=200, json={
                          'id': f"{i}", "name": "plant"})

    requests_mock.get(f"{BASE_ENDPOINT}{4}", status_code=404, json={
        'id': f"{i}", "error": "not found"})
    for i in range(5, 7):
        requests_mock.get(f"{BASE_ENDPOINT}{i}", status_code=200, json={
                          'id': f"{i}", "name": "plant"})
    for i in range(7, 7+MAX_404_ERRORS):
        requests_mock.get(f"{BASE_ENDPOINT}{i}", status_code=404, json={
                          'id': f"{i}", "error": "not found"})
    pg = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    data = pg.loop_ids()
    ids = [plant['id'] for plant in data]
    assert len(data) == 5
    assert ids == ['1', '2', '3', '5', '6']
    assert requests_mock.call_count == 11


def test_exception_returns_none(requests_mock):
    """checks that exceptions return none"""
    requests_mock.get(f"{BASE_ENDPOINT}1",
                      exc=requests.exceptions.ConnectionError)
    pg = PlantGetter(BASE_ENDPOINT, START_ID, MAX_404_ERRORS)
    data = pg.get_plant(1)
    assert data is None
    assert requests_mock.call_count == 1
