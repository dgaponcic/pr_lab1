from contextlib import suppress
import threading
import socket
import signal
import json
import sys
import re

PORT = 10000
BUFFER_SIZE = 1024

class TCPServer:
  def start_socker(self, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (host, port)
    sock.bind(server_address)
    sock.listen(10)

    return sock


  def get_connection(self, sock):
    connection, client_address = sock.accept()
    connection.settimeout(0.01)

    return connection


  def select_columns(self, columns, data):
    res = []
    for person in data:
      res.append({column: person[column] for column in columns})

    return res


  def select_column(self, column, data):
    res = []
    for person in data:
      res.append(person[column])

    return {column: res}

  
  def select_from_column_by_pattern(self, column, pattern, data):
    res = []

    for person in data:
      value = person[column]
      if value and bool(re.search(pattern, value)):
        res.append(value)

    return {column: res}


  def get_result_by_selector(self, tokens, data):
    res = None

    if tokens[0] == "SelectColumns":
      columns = tokens[1].split(",")
      res = self.select_columns(columns, data)
    elif tokens[0] == "SelectColumn":
      column = tokens[1]
      if len(tokens) >= 3:
        pattern = tokens[2]
        res = self.select_from_column_by_pattern(column, pattern, data)
      else:
        res = self.select_column(column, data)
    else:
      raise "Unknown command."

    return res


  def apply_flags(self, res, flags):
    for flag in flags:
      if flag == "--pretty":
        res = json.dumps(res, indent=4)
      else:
        raise "Unknown flag."

    return res


  def remove_flags(self, command):
    return re.search(".+?(?=--)", command).group().strip()


  def get_response(self, command, data):
    command = command.decode('ascii')
    flags = re.findall("--[a-z]*", command)
    tokens = self.remove_flags(command).split(" ") if flags else command.split(" ")
    res = self.get_result_by_selector(tokens, data)

    if flags:
      res = self.apply_flags(res, flags)

    return res


  def request(self, connection, data):
    command = self.get_command(connection)
    response = self.get_response(command, data)
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
      print("socket closed")
      sys.exit(0)

    return signal_handler
