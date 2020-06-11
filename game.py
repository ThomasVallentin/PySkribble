import random


class Player(object):
    def __init__(self):
        self.name = None
        self.score = 0

        self.is_choosing = False
        self.has_found = False
        self.is_winner = False

        self.id = hex(id(self))


class Game(object):
    def __init__(self):
        self.words = []
        self.choices_count = 3
        self.current_word = None
        self.already_passed_words = []

        self.players = {}

    def load_words(self, path):
        with open(path, "r") as f:
            self.words = [x.strip() for x in f.read().split(',')]

    def set_current_word(self, word):
        self.current_word = word

    def generate_choices(self):
        return random.sample(self.words, k=self.choices_count)

    def new_player(self):
        player = Player()

        self.players[player.id] = player

        return player
