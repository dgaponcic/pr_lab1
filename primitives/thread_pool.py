from contextlib import suppress
from threading import Thread
from queue import Empty
from primitives.queue import Queue


class Worker():
  def __init__(self, runnables):
    self.is_closed = False
    self.thread = Thread(target=self.get_runnable, args=(runnables, ))
    self.thread.start()

  def get_runnable(self, runnables):
    with suppress(Empty):
      while True:
        runnable = runnables.get(timeout=0) if self.is_closed else runnables.get()
        function = runnable["function"]
        args = runnable["args"]
        function(*args)

  def set_closed(self, value):
    self.is_closed = value

class ThreadPool:
  def __init__(self, max_workers):
    self.max_workers = max_workers
    self.runnables = Queue()
    self.workers = []
    for _ in range(max_workers):
      self.workers.append(Worker(self.runnables))

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.join()

  def submit(self, f, *args):
    self.runnables.put({"function": f, "args": args})

  def join(self):
    for worker in self.workers:
      worker.is_closed = True

    for worker in self.workers:
      worker.thread.join()
