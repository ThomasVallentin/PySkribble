from lib.server import Server, Connection
import game
import pickle


class SkribbleConnection(Connection):
    def __init__(self, player, socket, server):
        super(SkribbleConnection, self).__init__(socket, server)

        self.player = player

    def send(self, data):
        self.socket.send(data)

    def thread_loop(self):
        # Sending player id to the remote client
        self.send(str.encode(self.player.id))

        # main_loop
        super(SkribbleConnection, self).thread_loop()

    def process_request(self, data):
        request = data.decode("utf-8")

        if request.startswith("NAME:"):
            name = request[5:]
            print(f"Received {self.player.name or self.player.id} player name : {name}")
            self.player.name = name

            self.send(pickle.dumps(self.server.game))

        elif request.startswith("GUESS:"):
            print(f"Received {self.player.name or self.player.id}'s guess : {request[6:]}")
            self.send(pickle.dumps(self.server.game))

        elif request.startswith("CHOICE:"):
            print(f"Received {self.player.name or self.player.id}'s choice : {request[7:]}")
            self.send(pickle.dumps(self.server.game))

        elif request.startswith("DRAW:"):
            print(f"Received {self.player.name or self.player.id}'s drawing : {request[5:]}")
            self.send(pickle.dumps(self.server.game))

        else:
            print("Received unknown data", request)

        return True


class SkribbleServer(Server):
    BUFFER_SIZE = 4096*16
    CONNECTION_CLASS = SkribbleConnection

    def __init__(self):
        super(SkribbleServer, self).__init__()
        self.game = game.Game()

    def process_connection(self, conn_socket):
        player = self.game.new_player()
        print(f"Creating a new player {player.id} for connection {conn_socket.getsockname()}")
        connection = SkribbleConnection(player, conn_socket, self)

        self.connections.append(connection)

        connection.start()


if __name__ == '__main__':
    server = SkribbleServer()
    server.start()
