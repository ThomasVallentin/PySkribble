from lib.client import Client

import pickle


class SkribbleClient(Client):
    def __init__(self, ip=None, port=None):
        super(SkribbleClient, self).__init__(ip=ip, port=port)

        self.id = None
        self._game = None

    @property
    def player(self):
        return self.game.players[self.id]

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, value):
        self._game = value

    def start(self):
        self.id = self.connect()

    def send_request(self, data):
        recv = self.send(data)
        self.game = pickle.loads(recv)

    def set_name(self, name):
        self.send_request("NAME:" + name)

    def make_guess(self, guess):
        self.send_request("GUESS:" + guess)

    def make_choice(self, choice):
        self.send_request("CHOICE:" + choice)

    def draw(self, line):
        self.send_request("DRAW:" + line)
        
        
if __name__ == '__main__':
    client = SkribbleClient()
    client.start()
    print(client.id)

    client.set_name("Daexs")
    print(client.player.name)

    client.make_choice("pulsar")

    client.make_guess("supernova")

    client.draw("very precise drawing")

