from queue import Empty
from contextlib import suppress
from threading import Thread
from my_queue import Queue


class Worker():
  def __init__(self, runnables):
    self.was_closed = False
    self.thread = Thread(target=self.get_runnable, args=(runnables, ))
    self.thread.start()

  def get_runnable(self, runnables):
    with suppress(Empty):
      while True:
        runnable = runnables.get(timeout=0) if self.was_closed else runnables.get()
        function = runnable["function"]
        args = runnable["args"]
        function(*args)

class ThreadPool:
  def __init__(self, max_workers):
    self.max_workers = max_workers
    self.runnables = Queue()
    self.workers = []
    for _ in range(max_workers):
      self.workers.append(Worker(self.runnables))

  def submit(self, f, *args):
    self.runnables.put({"function": f, "args": args})

  def join(self):
    for worker in self.workers:
      worker.was_closed = True

    for worker in self.workers:
      worker.thread.join()
