import requests
import threading
import time
import json
from contextlib import suppress
from queue import Empty
from concurrent.futures import ThreadPoolExecutor
from my_queue import Queue
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


def add_links(result, q_in):
  if "link" in result.keys():
    links = result["link"].values()
    for link in links:
      q_in.put(link)

def request(q_in, access_token):
  path = q_in.get(timeout=7)
  url = get_url(path)
  print(url)
  return json.loads(requests.get(url, headers={"X-Access-Token": access_token}).text)

def make_request(access_token, q_in, q_out):
  with suppress(Empty):
    while True:
      result = request(q_in, access_token)
      q_out.put(result)
      add_links(result, q_in)

def get_data(jobs):
  all_data = []
  for future in jobs:
    data = future.result()
    if data["text"]:
      all_data.append(future.result())
  return all_data


def parse_data(q_out):
  all_data = []
  with suppress(Empty):
    while True:
      res = q_out.get(timeout=10)
      data = retrieve_data_from_request(res)
      if data["text"]:
        all_data.append(data)

  return all_data

def get_aggregate_data(q_out):
  all_data = parse_data(q_out)
  aggregator = DataAggregator()
  return aggregator.parse_data(all_data)


def main():
  # init_time = time.time()
  access_token, url = make_initial_request()
  q_out = Queue()
  q_in = Queue()
  q_in.put(url)
  with ThreadPoolExecutor(max_workers=10) as executor:
    for _ in range(6):
      executor.submit(make_request, access_token, q_in, q_out)
    data = get_aggregate_data(q_out)
    # print(time.time() - init_time)
    server = TCPServer()
    server.start(data)


if __name__ == "__main__":
  main()
