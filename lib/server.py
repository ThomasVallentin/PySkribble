import socket
import threading


class Connection(object):
    def __init__(self, socket, server):
        self.socket = socket
        self.server = server

        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.thread_loop)

        self.thread.start()

    def thread_loop(self):
        while True:
            try:
                data = self.socket.recv(self.server.BUFFER_SIZE)

                if not data:
                    print("Disconnected")
                    break

                self.process_request(data)

            except:
                break

        print("Connection lost :", self.socket.getsockname())
        self.socket.close()

    def process_request(self, data):
        return True


class Server(object):
    CONNECTION_CLASS = Connection
    BUFFER_SIZE = 2048

    def __init__(self):
        self.ip = socket.gethostname()
        self.port = 5555

        self.socket = socket.socket()

        self.connections = []

    @property
    def address(self):
        return self.ip, self.port

    def process_connection(self, conn_socket):
        connection = self.CONNECTION_CLASS(conn_socket, self)
        self.connections.append(connection)

        connection.start()

    def start(self):
        self.socket.bind(self.address)
        self.socket.listen(2)

        print(f"{self.__class__.__name__} started and running on {threading.current_thread().getName()}")
        print("Waiting for a connection...")

        while True:
            conn_socket, address = self.socket.accept()
            print(f"Incoming connection from {address}")

            self.process_connection(conn_socket)


class EchoServer(Server):
    def process_incoming_data(self, connection, data):
        reply = data.decode("utf-8")
        print("Received:", reply)

        reply = "Echo : " + reply
        print("Sending:", reply)

        connection.sendall(str.encode(reply))

        return True


if __name__ == '__main__':
    server = EchoServer()
    server.start()
