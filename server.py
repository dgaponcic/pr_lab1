import socket
import json
import threading


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

  def select_column(self, column, data):
    return [value.get(column) for value in data]

  def get_result(self, command, data):
    tokens = command.decode('ascii').split(" ")
    if tokens[0] == "SelectColumn":
      return self.select_column(tokens[1], data)

  def request(self, connection, data):
    command = self.get_command(connection)
    response = self.get_result(command, data)
    connection.sendall(json.dumps(response).encode())
    connection.close()

  def get_command(self, connection):
    data = b''
    try:
      while True:
        data = data + connection.recv(1024)
    except socket.error as e:
      pass
    return data

  def start(self, data):
    sock = self.start_socker("localhost", 10000)
    while True:
      connection = self.get_connection(sock)
      thread = threading.Thread(target=self.request, args=(connection, data))
      thread.start()
