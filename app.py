import requests
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from parser import Parser
# from server import start_server
from server import TCPServer
from data_aggregator import DataAggregator


def get_url(path):
    return f'http://localhost:5000{path}'


def make_initial_request():
    initial_request = json.loads(
        requests.get("http://localhost:5000/register").text)
    access_token, path = initial_request["access_token"], initial_request[
        "link"]
    url = get_url(path)
    return access_token, url


def make_recursive_requests(links, access_token, jobs, executor):
    for link in links:
        future = executor.submit(make_request, get_url(link), access_token,
                                 jobs, executor)
        jobs.append(future)


def retrieve_data_from_request(result):
    data = None
    data_type = None

    if "data" in result.keys():
        data = result["data"]
        if "mime_type" in result.keys():
            data_type = result["mime_type"]
        else:
            data_type = 'application/json'

    return {"text": data, "data_type": data_type}


def make_request(url, access_token, jobs, executor):
    result = json.loads(
        requests.get(url, headers={
            "X-Access-Token": access_token
        }).text)

    if "link" in result.keys():
        links = result["link"].values()
        make_recursive_requests(links, access_token, jobs, executor)
    return retrieve_data_from_request(result)


def get_data(jobs):
    all_data = []
    for future in jobs:
        data = future.result()
        if data["text"]:
            all_data.append(future.result())
    return all_data


def main():
    executor = ThreadPoolExecutor(max_workers=10)
    access_token, url = make_initial_request()
    jobs = []
    jobs.append(
        executor.submit(make_request, url, access_token, jobs, executor))
    data = get_data(jobs)
    aggregator = DataAggregator()
    server = TCPServer()
    server.start(aggregator.parse_data(data))


if __name__ == '__main__':
    main()
