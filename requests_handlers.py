import json
import requests
from contextlib import suppress
from queue import Empty

def get_url(path):
  return f"http://localhost:5000{path}"


def make_initial_request():
  initial_request = json.loads(requests.get("http://localhost:5000/register").text)
  access_token, path = initial_request["access_token"], initial_request["link"]
  url = path
  return access_token, url


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
