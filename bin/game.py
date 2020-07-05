from PySide2 import QtCore

import os
import json
import random

from constants import RESSOURCES_DIR
from lib import logger
from lib import utils


class Player(object):
    def __init__(self):
        self.name = None
        self.avatar_id = 0
        self.score = 0

        self.is_master = False
        self.has_found = False
        self.is_winner = False
        self.is_drawing = False

        self.id = hex(id(self))

    def __str__(self):
        return "{}({})".format(self.__class__, self.id)


class GameData(object):
    def __init__(self):
        self.players = {}
        self.player_queue = []

        self.choices_count = 3
        self.choices = []

        self.choosing_time = 30000
        self.drawing_time = 50000

        self.drawing_player = None
        self.found_players_count = 0


class GameLogic(QtCore.QObject):
    game_started = QtCore.Signal()
    game_ended = QtCore.Signal()

    round_started = QtCore.Signal()
    round_ended = QtCore.Signal()

    choosing_started = QtCore.Signal(str, list, int)
    drawing_started = QtCore.Signal(str, str, int)
    player_guessed = QtCore.Signal(str, int)

    def __init__(self):
        super(GameLogic, self).__init__()
        self.logger = logger.Logger(self.__class__.__name__, logger.INFO)
        self.words = []
        self.remaining_words = []

        self.game_data = GameData()

        self.is_running = False
        self.score_time = 1000
        self.current_word = None
        self.bonus_rules = {1: 25, 2: 15, 3: 5}

        self.choosing_timer = QtCore.QTimer(self)
        self.choosing_timer.setSingleShot(True)
        self.choosing_timer.timeout.connect(self.end_choosing)

        self.drawing_timer = QtCore.QTimer(self)
        self.drawing_timer.setSingleShot(True)
        self.drawing_timer.timeout.connect(self.end_drawing)

        self.choosing_phase = False
        self.drawing_phase = False

    def load_words(self, path):
        with open(path, "r") as f:
            self.words = json.load(f)
            self.remaining_words = self.words

    # == CHOICES ===================================================================================

    def generate_choices(self):
        if len(self.remaining_words) < self.game_data.choices_count:
            self.remaining_words = list(self.words)

        self.game_data.choices = random.sample(self.remaining_words, k=self.game_data.choices_count)
        self.logger.debug(f"Generated choices are : {self.game_data.choices}")

    def start_choosing(self):
        self.choosing_phase = True

        if self.game_data.drawing_player:
            self.game_data.drawing_player.is_drawing = False

        self.game_data.drawing_player = self.player_from_id(self.game_data.player_queue[0])
        self.game_data.drawing_player.is_drawing = True

        self.logger.info(f"{self.game_data.drawing_player.name} is choosing...")

        self.choosing_timer.start(self.game_data.choosing_time)
        self.choosing_timer.timeout.connect(lambda: self.logger.debug("TIMEOUT"))

        self.choosing_started.emit(self.game_data.drawing_player.id, self.game_data.choices, self.game_data.choosing_time)

    def _select_word(self, index):
        self.current_word = self.game_data.choices[index]
        self.remaining_words.remove(self.current_word)

        self.logger.debug(f"Current word is now : {self.current_word}")

    def make_choice(self, player, index):
        if not self.choosing_phase:
            return

        if not isinstance(index, int):
            return

        if player is not self.game_data.drawing_player:
            return

        if index >= self.game_data.choices_count:
            return

        self.choosing_timer.stop()

        self.logger.info(f"{player.name} made its choice !")
        self._select_word(index)

        self.start_drawing()

    def end_choosing(self):
        self.logger.debug("Time is up ! No choice has been made, choosing randomly instead...")
        self._select_word(random.randint(0, self.game_data.choices_count - 1))

        self.start_drawing()

    # == DRAWING ===================================================================================

    def start_drawing(self):
        self.logger.info("Starting to draw...")

        self.choosing_phase = False
        self.drawing_phase = True

        self.found_players_count = 0

        self.drawing_started.emit(self.game_data.drawing_player.id, self.current_word, self.game_data.drawing_time)
        self.drawing_timer.start(self.game_data.drawing_time)

        # def random_guess():
        #     self.make_guess(random.choice(self.game_data.player_queue),
        #                     self.game_data.choices[random.randint(0, self.game_data.choices_count - 1)])
        #
        # QtCore.QTimer.singleShot(random.randint(self.game_data.drawing_time - 2000,
        #                                         self.game_data.drawing_time), random_guess)

    def make_guess(self, player, guess):
        if not self.drawing_phase:
            return

        if not isinstance(guess, str):
            return

        if player is self.game_data.drawing_player:
            return

        if player.has_found:
            return

        self.logger.info(f"{player.name} made a guess : {guess}")

        if not utils.words_match(guess, self.current_word):
            self.logger.info(f"{player.name} was wrong...")
            return

        player.has_found = True
        self.found_players_count += 1
        self.player_guessed.emit(player.id, self.found_players_count)

        player_rank = self.found_players_count
        bonus = self.bonus_rules.get(self.found_players_count, 0)
        points = self.compute_guesser_points(self.drawing_timer.remainingTime()) + bonus
        player.score += points

        # Display points
        self.logger.info(f"{player.name} has found the correct word and wins {points} points !")
        if bonus:
            self.logger.info(f"He got {bonus} bonus points because he was {player_rank}")

        for ply in self.game_data.players.values():
            if not ply.has_found and ply is not self.game_data.drawing_player:
                break
        else:
            self.logger.info("All players have found the word, going to the next round...")
            self.game_data.drawing_player.score += self.compute_drawer_points(remaining_time=self.drawing_timer.remainingTime())
            self.drawing_timer.stop()
            self.end_round()

    def compute_guesser_points(self, remaining_time):
        return int(remaining_time / self.drawing_timer.interval() * 100)

    def compute_drawer_points(self, remaining_time):
        found_points = float(self.found_players_count) / (len(self.game_data.players) - 1) * 75
        timing_points = remaining_time / self.drawing_timer.interval() * 75

        return int(found_points + timing_points)

    def end_drawing(self):
        self.logger.info("Time is up !")
        self.end_round()

    # == PLAYERS ===================================================================================

    def create_player(self):
        player = Player()

        if not self.game_data.players:
            player.is_master = True

        self.game_data.players[player.id] = player
        self.game_data.player_queue.append(player.id)

        return player

    def remove_player(self, player_id):
        if player_id not in self.game_data.players:
            return

        player = self.game_data.players.pop(player_id, None)
        self.game_data.player_queue.remove(player_id)

        if not self.game_data.players:
            self.stop()
            return

        if player.is_master:
            new_master = self.player_from_id(random.choice(self.game_data.player_queue))
            new_master.is_master = True

    def player_from_id(self, id):
        return self.game_data.players.get(id, None)

    # == GLOBAL ====================================================================================

    def start(self):
        if len(self.game_data.players) < 2:
            self.logger.debug("Cannot start the game without at least 2 players...")
            return

        self.logger.info("Starting the game !")
        self.game_started.emit()
        self.is_running = True

        self.load_words(os.path.join(RESSOURCES_DIR, "words.json"))
        self.start_round()

    def start_round(self):
        self.logger.info("It is time for a new round...")

        self.round_started.emit()

        self.generate_choices()
        self.start_choosing()

    def end_round(self):
        self.drawing_phase = False

        for player in self.game_data.players.values():
            player.has_found = False

        self.round_ended.emit()
        self.display_scores()
        QtCore.QTimer.singleShot(self.score_time, self.next_round)

    def next_round(self):
        if not self.game_data.players:
            self.stop()

        # move the drawing player to the end of the queue
        drawing_player_id = self.game_data.player_queue.pop(0)
        self.game_data.player_queue.append(drawing_player_id)

        self.start_round()

    def stop(self):
        self.drawing_timer.stop()
        self.choosing_timer.stop()

        self.is_running = False
        self.game_ended.emit()

    def display_scores(self):
        print("\nSCORE BOARD :")
        print("\n".join([f"{p.name} : {p.score}" for p in sorted(self.game_data.players.values(),
                                                                 key=lambda x: -x.score)]), "\n")


if __name__ == '__main__':
    app = QtCore.QCoreApplication([])

    game = GameLogic()

    p1 = game.create_player()
    p1.name = "Bob"

    p2 = game.create_player()
    p2.name = "Patrick"

    p3 = game.create_player()
    p3.name = "Karen"

    game.start()

    app.exec_()
