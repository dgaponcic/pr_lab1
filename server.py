import socket
import json
import threading
import signal
import sys
from contextlib import suppress

PORT = 10000
BUFFER_SIZE = 1024

class TCPServer:
  def start_socker(self, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    sock.bind(server_address)
    sock.listen(10)

    return sock


  def get_connection(self, sock):
    connection, client_address = sock.accept()
    connection.settimeout(0.01)

    return connection


  def select_column(self, columns, data):
    res = [column for column in columns]
    delimitator = "  |  "
    res = delimitator.join(res)
    for value in data:
      res += "\n"
      res += delimitator.join([str(value.get(column)) for column in columns])

    return res


  def get_result(self, command, data):
    tokens = command.decode('ascii').split(" ")
    if tokens[0] == "SelectColumn":
      columns = tokens[1].split(",")
      return self.select_column(columns, data)
    if tokens[0] == "SelectPattern":
      pass #todo


  def request(self, connection, data):
    command = self.get_command(connection)
    response = self.get_result(command, data)
    connection.sendall(json.dumps(response).encode())
    connection.close()


  def get_command(self, connection):
    data = b''
    with suppress(socket.error):
      while True:
        data = data + connection.recv(BUFFER_SIZE)
    return data


  def start(self, data):
    sock = self.start_socker("localhost", PORT)
    signal.signal(signal.SIGINT, self.close_server(sock))
    print("socket started")
    while True:
      connection = self.get_connection(sock)
      thread = threading.Thread(target=self.request, args=(connection, data))
      thread.start()


  def close_server(self, sock):
    def signal_handler(signal, frame): 
      sock.close()
      sys.exit(0)

    return signal_handler
