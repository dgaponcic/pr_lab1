# Network Programming

TUM Laboratory work.

## Task description
* Pull and run a docker container alexburlacu/pr-server
* Access the link /register and obtain a token(valid for 20 seconds)
* Add the token to the header of all the following requests, under the key X-Access-Token
* Traverse all the routes that are in the response "links" field
* Fetch all the data(which can be JSON, XML, CSV, YAML), convert to a common representation and join it together
* Make a concurrent TCP server, serving the fetched content

## Implementation


#### Main
In main we make the initial request to get next link to follow and the registration token. Next we create a q_in (queue for storing the links to follow) and q_out 
(queue for storing the data). 

We initialize a thread pool where the workers wait for new links to follow.
At the same time, in the main thread, start aggregating data from q_out.

Finally, we start a TCP server to fetch the data.

```
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
```

#### Primitives

In primites folder there is an implementation of a Queue. It uses a condition variable to wait when trying to get an element from an empty queue and 
signal when a new element was added.

Another primitive is ThreadPool. It has mathods submit (for submitting new tasks) and join (for joining the threads).
```
  def submit(self, f, *args):
    self.runnables.put({"function": f, "args": args})

  def join(self):
    for worker in self.workers:
      worker.was_closed = True

    for worker in self.workers:
      worker.thread.join()
```
It uses the class Worker, which is a thread that waits for a new task, executes it and waits again.

```
  def get_runnable(self, runnables):
    with suppress(Empty):
      while True:
        runnable = runnables.get(timeout=0) if self.was_closed else runnables.get()
        function = runnable["function"]
        args = runnable["args"]
        function(*args)
```

The pool is implemented to work as a context manager.

#### Parsers
There is a parser for each data format(XML, YAML, CSV, JSON). Ex: 

```
class ParserXML:
  def parse(self, input_data):
    tree = ET.parse(StringIO(input_data))
    root = tree.getroot()

    data = []
    for record in root:
      person = {}
      for value in record:
        person[value.tag] = value.text
      data.append(person)
    return data
```

 #### Data Aggregator
 For each response, parse data to a common format and join the new people into the result(based on an unique key).
 
 ```
 
  def parse_data(self, all_data):
    res = []
    for data in all_data:
      data_type = data["data_type"]
      data = self.parser.parse(data_type, data["text"])
      res = self.join_data(res, data)

    return res

 ```
 
 #### TCP Server
 
 ```
  def start_socker(self, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    sock.bind(server_address)
    sock.listen(10)

    return sock
    
    
  def start(self, data):
    sock = self.start_socker("localhost", PORT)
    signal.signal(signal.SIGINT, self.close_server(sock))
    print("socket started")
    while True:
      connection = self.get_connection(sock)
      thread = threading.Thread(target=self.request, args=(connection, data))
      thread.start()

```
 
 
 
 
 
 
 
 
 
 
 
 
 
 
