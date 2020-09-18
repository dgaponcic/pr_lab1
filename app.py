import requests
import threading
import json
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from parser import Parser
from server import TCPServer
from data_aggregator import DataAggregator


def get_url(path):
  return f"http://localhost:5000{path}"


def make_initial_request():
  initial_request = json.loads(requests.get("http://localhost:5000/register").text)
  access_token, path = initial_request["access_token"], initial_request["link"]
  url = path
  return access_token, url


def retrieve_data_from_request(result):
  data = None
  data_type = None

  if "data" in result.keys():
    data = result["data"]
    if "mime_type" in result.keys():
      data_type = result["mime_type"]
    else:
      data_type = "application/json"
  return {"text": data, "data_type": data_type}


def make_request(access_token, q_in, q_out):
  try:
    while True:
      path = q_in.get(timeout=7)
      url = get_url(path)
      result = json.loads(requests.get(url, headers={"X-Access-Token": access_token}).text)
      q_out.put(result)

      if "link" in result.keys():
        links = result["link"].values()
        for link in links:
          q_in.put(link)
      q_in.task_done()

  except Empty:
    pass


def get_data(jobs):
  all_data = []
  for future in jobs:
    data = future.result()
    if data["text"]:
      all_data.append(future.result())
  return all_data


def parse_data(q_out):
  all_data = []
  try:
    while True:
      res = q_out.get(timeout=10)
      data = retrieve_data_from_request(res)
      if data["text"]:
        all_data.append(data)
  except Empty:
    pass
  return all_data


def main():
  executor = ThreadPoolExecutor(max_workers=10)
  access_token, url = make_initial_request()
  q_out = Queue()
  q_in = Queue()
  q_in.put(url)
  for _ in range(6):
    executor.submit(make_request, access_token, q_in, q_out)
  all_data = parse_data(q_out)
  aggregator = DataAggregator()
  data = aggregator.parse_data(all_data)
  server = TCPServer()
  server.start(data)


if __name__ == "__main__":
  main()
