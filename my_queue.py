from queue import Empty
from threading import Thread, Lock, Event, Condition
import signal
import time

class Queue(object):
  def __init__(self):
    self.length = 0
    self.nodes = []
    self.lock = Lock()
    self.was_added = Condition(self.lock)

  def put(self, x):
    self.was_added.acquire()
    self.length += 1
    self.nodes.append(x)
    self.was_added.notify()
    self.was_added.release()


  def get(self, timeout):
    try:
      self.lock.acquire()

      endtime = time.time() + timeout
      while not self.length:
        remaining = endtime - time.time()
        if remaining <= 0.0:
            raise Empty
        self.was_added.wait(timeout=remaining)

      item = self.nodes.pop(0)
      self.length -= 1
      return item
    
    finally:
      self.lock.release()
