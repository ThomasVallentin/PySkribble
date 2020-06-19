import random
from PySide2 import QtCore
import shuffle


class Player(object):
    def __init__(self, game):
        self.game = game

        self.name = None
        self.score = 0

        self.is_master = False
        self.has_found = False
        self.is_winner = False

        self.id = hex(id(self))

    @property
    def is_choosing(self):
        return self is self.game.game_data.choosing_player

    def __str__(self):
        return "{}({})".format(self.__class__, self.id)


class GameData(object):
    def __init__(self):
        self.players = {}
        self.player_queue = []

        self.choices_count = 3
        self.choices = []
        self.current_word = None

        self.choosing_time = 3000
        self.drawing_time = 5000
        self.score_time = 3000

        self.choosing_player = None
        self.found_players_count = 0


class GameLogic(object):
    def __init__(self):
        self.words = []
        self.remaining_words = []

        self.game_data = GameData()

        self.choosing_timer = QtCore.QTimer()
        self.choosing_timer.setSingleShot(True)
        self.choosing_timer.timeout.connect(self.end_choosing)

        self.drawing_timer = QtCore.QTimer()
        self.drawing_timer.setSingleShot(True)
        self.drawing_timer.timeout.connect(self.end_drawing)

        self.choosing_phase = False
        self.drawing_phase = False

    def load_words(self, path):
        with open(path, "r") as f:
            self.words = [x.strip() for x in f.read().split(',')]
            self.remaining_words = list(self.words)

    # == CHOICES ===================================================================================

    def generate_choices(self):
        self.game_data.choices = random.sample(self.words, k=self.game_data.choices_count)
        print(f"Generated choices are : {self.game_data.choices}")

    def start_choosing(self):
        self.choosing_phase = True

        self.game_data.choosing_player = self.game_data.player_queue[0]

        print(f"{self.game_data.choosing_player.name} is choosing...")

        self.choosing_timer.start(self.game_data.choosing_time)

        QtCore.QTimer.singleShot(random.randint(self.game_data.choosing_time - 1000,
                                                self.game_data.choosing_time + 1000),
                                 lambda: self.choosing_word(self.game_data.choosing_player,
                                                            random.randint(0, self.game_data.choices_count - 1)))

    def _select_word(self, index):
        self.game_data.current_word = self.game_data.choices[index]
        self.remaining_words.remove(self.game_data.current_word)

        print(f"Current word is now : {self.game_data.current_word}")

    def choosing_word(self, player, index):
        if not self.choosing_phase:
            return

        if player is not self.game_data.choosing_player:
            return

        self.choosing_timer.stop()

        print(f"{player.name} made its choice !")
        self._select_word(index)

        self.start_drawing()

    def end_choosing(self):
        print("Time is up ! No choice has been made, choosing randomly instead...")
        self._select_word(random.randint(0, self.game_data.choices_count - 1))

        self.start_drawing()

    # == DRAWING ===================================================================================

    def start_drawing(self):
        print("Starting to draw...")

        self.choosing_phase = False
        self.drawing_phase = True

        self.found_players_count = 0

        self.drawing_timer.start(self.game_data.drawing_time)

        def random_guess():
            self.make_guess(random.choice(self.game_data.player_queue),
                            self.game_data.choices[random.randint(0, self.game_data.choices_count - 1)])

        QtCore.QTimer.singleShot(random.randint(self.game_data.drawing_time - 2000,
                                                self.game_data.drawing_time), random_guess)

    def make_guess(self, player, guess):
        if not self.drawing_phase:
            return

        if player is self.game_data.choosing_player:
            return

        print(f"{player.name} made a guess : {guess}")

        if guess != self.game_data.current_word:
            print(f"{player.name} was wrong...")
            return

        player.has_found = True
        self.found_players_count += 1

        player_rank = self.found_players_count
        bonus = {1: 25, 2: 15, 3: 5}.get(self.found_players_count, 0)
        points = self.compute_points(self.drawing_timer.remainingTime()) + bonus
        player.score += points

        # Display points
        print(f"{player.name} has found the correct word and wins {points} points !")
        if bonus:
            print(f"He got {bonus} bonus points because he was {player_rank}")

        for ply in self.game_data.players.values():
            if not ply.has_found:
                break
        else:
            print("All players have found the word, going to the next round...")
            self.game_data.choosing_player.score += self.drawing_timer.remainingTime() * 1.5
            self.drawing_timer.stop()
            self.end_round()

    def compute_points(self, remaining_time):
        return int(float(remaining_time) / self.drawing_timer.interval() * 100)

    def end_drawing(self):
        print("Time is up ! Going to the next round...")
        self.end_round()

    # == PLAYERS ===================================================================================

    def create_player(self, name):
        player = Player(self)
        player.name = name

        if not self.game_data.players:
            player.is_master = True

        self.game_data.players[player.id] = player
        self.game_data.player_queue.append(player)

        print(f"Player \"{name}\" entered the game !")

        return player

    def remove_player(self, player_id):
        if player_id not in self.game_data.players:
            return

        player = self.game_data.players.pop(player_id, None)
        self.game_data.player_queue.remove(player_id)

        if player.is_master:
            new_master = random.choice(self.game_data.players.values())
            new_master.is_master = True

    # == GLOBAL ====================================================================================

    def start(self):
        if not self.game_data.players:
            return

        print("Starting the game !")

        self.load_words("skribble.txt")
        self.start_round()

    def start_round(self):
        print("It is time for a new round...")
        self.generate_choices()
        self.start_choosing()

    def end_round(self):
        self.drawing_phase = False

        self.display_scores()
        QtCore.QTimer.singleShot(self.game_data.score_time, self.next_round)

    def next_round(self):
        if not self.game_data.players:
            self.stop()

        # move the drawing player to the end of the queue
        drawing_player = self.game_data.player_queue.pop(0)
        self.game_data.player_queue.append(drawing_player)

        self.start_round()

    def stop(self):
        pass

    def display_scores(self):
        print("\nSCORE BOARD :")
        print("\n".join([f"{p.name} : {p.score}" for p in sorted(self.game_data.players.values(),
                                                                 key=lambda x: -x.score)]))
        print("")


if __name__ == '__main__':
    app = QtCore.QCoreApplication([])

    game = GameLogic()

    p1 = game.create_player("Bob")
    p2 = game.create_player("Patrick")
    p3 = game.create_player("Karen")

    game.start()

    app.exec_()
