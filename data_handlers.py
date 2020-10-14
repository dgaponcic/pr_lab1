from contextlib import suppress
from queue import Empty
from data_aggregator import DataAggregator

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


def get_data(jobs):
  all_data = []
  for future in jobs:
    data = future.result()
    if data["text"]:
      all_data.append(future.result())

  return all_data


def retrieve_data(q_out):
  all_data = []
  with suppress(Empty):
    while True:
      res = q_out.get(timeout=7)
      data = retrieve_data_from_request(res)
      if data["text"]:
        all_data.append(data)

  return all_data


def get_aggregate_data(q_out):
  all_data = retrieve_data(q_out)
  aggregator = DataAggregator()
  return aggregator.parse_data(all_data)
