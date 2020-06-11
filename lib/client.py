import socket


class Client(object):
    def __init__(self, ip=None, port=None):
        self.ip = ip or socket.gethostname()
        self.port = port or 5555

        self.socket = socket.socket()

    @property
    def address(self):
        return self.ip, self.port

    def connect(self):
        try:
            self.socket.connect(self.address)
            return self.socket.recv(2048).decode()

        except:
            print("Failed to connect")

    def send(self, data):
        try:
            self.socket.send(str.encode(data))
            return self.socket.recv(8192)

        except socket.error as e:
            print(e)

    def start(self):
        self.connect()


if __name__ == '__main__':
    import datetime, time

    client = Client()

    client.connect()
    while True:
        time.sleep(2)
        reply = client.send(datetime.datetime.now().strftime("%Y/%m/%d - %H:%M:%S"))
        print(reply)
