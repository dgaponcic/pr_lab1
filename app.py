import signal
from my_queue import Queue
from server import TCPServer
from my_thread_pool import ThreadPool
from requests_handlers import make_initial_request, make_request
from data_handlers import get_aggregate_data

def main():
  access_token, url = make_initial_request()
  q_out = Queue()
  q_in = Queue()
  q_in.put(url)

  with ThreadPool(max_workers=6) as executor:
    for _ in range(6):
      executor.submit(make_request, access_token, q_in, q_out)
    data = get_aggregate_data(q_out)
    server = TCPServer()
    server.start(data)

main()
