import signal
from requests_handlers import make_initial_request, make_request
from primitives.thread_pool import ThreadPool
from data_handlers import get_aggregate_data
from primitives.queue import Queue
from server import TCPServer

if __name__ == "__main__":
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
