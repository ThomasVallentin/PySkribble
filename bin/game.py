from PySide2 import QtCore

import os
import json
import random

from constants import RESSOURCES_DIR, DEFAULT_CONFIG
from lib import logger
from lib import utils


class Player(object):
    def __init__(self):
        self.name = None
        self.avatar = bytearray()
        self.score = 0
        self.round_score = 0

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

        self.hints = {}

        self.config = DEFAULT_CONFIG.copy()
        self.drawing_player = None
        self.master_player = None
        self.found_players_count = 0

        self.has_started = False


class GameLogic(QtCore.QObject):
    game_started = QtCore.Signal()
    game_ended = QtCore.Signal()

    round_started = QtCore.Signal()
    round_ended = QtCore.Signal(str)

    choosing_started = QtCore.Signal(str, list, int)
    drawing_started = QtCore.Signal(str, str, int)
    hint_added = QtCore.Signal(dict)
    player_guessed = QtCore.Signal(str, int)

    def __init__(self):
        super(GameLogic, self).__init__()
        self.logger = logger.Logger(self.__class__.__name__, logger.INFO)

        self.words = []
        self.remaining_words = []
        self.choices = []
        self.found_players_count = 0

        self.game_data = GameData()
        self.paint_buffer = []

        self.current_word = ""
        self.bonus_rules = {1: 25, 2: 15, 3: 5}

        self.choosing_timer = QtCore.QTimer(self)
        self.choosing_timer.setSingleShot(True)
        self.choosing_timer.timeout.connect(self.end_choosing)

        self.drawing_timer = QtCore.QTimer(self)
        self.drawing_timer.setSingleShot(True)
        self.drawing_timer.timeout.connect(self.end_drawing)

        self.hints_timer = QtCore.QTimer(self)
        self.hints_timer.timeout.connect(self.add_hint)

        self.choosing_phase = False
        self.drawing_phase = False

    def load_words(self, path):
        with open(path, "r") as f:
            self.words = json.load(f)
            self.remaining_words = self.words

    # == PAINT BUFFER ==============================================================================

    def add_paint_to_buffer(self, paint_info):
        self.paint_buffer.append(paint_info)

    def flush_paint_buffer(self):
        self.paint_buffer.clear()

    # == CHOICES ===================================================================================

    def generate_choices(self):
        if len(self.remaining_words) < self.config["choices_count"]:
            self.remaining_words = list(self.words)

        self.choices = random.sample(self.remaining_words, k=self.config["choices_count"])
        self.logger.debug(f"Generated choices are : {self.choices}")

    def start_choosing(self):
        self.choosing_phase = True

        if self.game_data.drawing_player:
            self.game_data.drawing_player.is_drawing = False

        self.game_data.drawing_player = self.player_from_id(self.game_data.player_queue[0])
        self.game_data.drawing_player.is_drawing = True

        self.logger.info(f"{self.game_data.drawing_player.name} is choosing...")

        self.choosing_timer.start(self.config["choosing_time"])
        self.choosing_timer.timeout.connect(lambda: self.logger.debug("TIMEOUT"))

        self.choosing_started.emit(self.game_data.drawing_player.id, self.choices, self.config["choosing_time"])

    def _select_word(self, index):
        self.current_word = self.choices[index]
        self.remaining_words.remove(self.current_word)

        self.logger.debug(f"Current word is now : {self.current_word}")

    def make_choice(self, player, index):
        if not self.choosing_phase:
            return

        if not isinstance(index, int):
            return

        if player is not self.game_data.drawing_player:
            return

        if index >= self.config["choices_count"]:
            return

        self.choosing_timer.stop()

        self.logger.info(f"{player.name} made its choice !")
        self._select_word(index)

        self.start_drawing()

    def end_choosing(self):
        self.logger.debug("Time is up ! No choice has been made, choosing randomly instead...")
        self._select_word(random.randint(0, self.config["choices_count"] - 1))

        self.flush_hints()

        self.start_drawing()

    # == DRAWING ===================================================================================

    def start_drawing(self):
        self.logger.info("Starting to draw...")

        self.choosing_phase = False
        self.drawing_phase = True

        self.found_players_count = 0

        self.drawing_started.emit(self.game_data.drawing_player.id, self.current_word, self.config["drawing_time"])
        self.drawing_timer.start(self.config["drawing_time"])
        self.hints_timer.start(self.compute_hints_interval())

    def compute_hints_interval(self):
        if not self.current_word:
            return 0

        difficulty = max(1, min(self.config["hints_level"], 5))
        hints_percent = (5 - difficulty) / 5 * 0.9 + 0.001
        draw_time = self.config["drawing_time"]

        print(draw_time / len(self.current_word) / hints_percent)
        return draw_time / len(self.current_word) / hints_percent

    def add_hint(self):
        indices = [i for i in range(len(self.current_word)) if i not in self.game_data.hints]

        if not indices:
            return

        current_index = random.choice(indices)

        self.game_data.hints[current_index] = self.current_word[current_index]

        self.hint_added.emit(self.game_data.hints)

    def flush_hints(self):
        self.game_data.hints.clear()

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
        player.round_score = points
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

            self.end_round()

    def compute_guesser_points(self, remaining_time):
        return int(remaining_time / self.drawing_timer.interval() * 100)

    def compute_drawer_points(self, remaining_time):
        found_points = float(self.found_players_count) / (len(self.game_data.players) - 1) * 75
        timing_points = remaining_time / self.drawing_timer.interval() * 75

        return int(found_points + timing_points)

    def end_drawing(self):
        self.logger.info("Time is up !")

        self.hints_timer.stop()

        self.end_round()

    # == PLAYERS ===================================================================================

    def create_player(self):
        player = Player()

        if not self.game_data.players:
            player.is_master = True
            self.game_data.master_player = player

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

        if player.is_master and self.game_data.player_queue:
            new_master = self.player_from_id(random.choice(self.game_data.player_queue))
            new_master.is_master = True
            self.game_data.master_player = new_master

    def player_from_id(self, id):
        return self.game_data.players.get(id, None)

    # == GLOBAL ====================================================================================

    @property
    def config(self):
        return self.game_data.config

    def set_config(self, config_dict):
        self.game_data.config.update(config_dict)

    def start(self):
        if len(self.game_data.players) < 2:
            self.logger.debug("Cannot start the game without at least 2 players...")
            return

        self.logger.info("Starting the game !")

        self.game_started.emit()
        self.game_data.has_started = True

        self.load_words(os.path.join(RESSOURCES_DIR, "words.json"))
        self.start_round()

    def start_round(self):
        self.logger.info("It is time for a new round...")

        self.round_started.emit()

        self.generate_choices()
        self.start_choosing()

    def end_round(self):
        points = self.compute_drawer_points(remaining_time=self.drawing_timer.remainingTime())
        self.game_data.drawing_player.round_score = points
        self.game_data.drawing_player.score += points

        self.drawing_timer.stop()
        self.drawing_phase = False

        self.round_ended.emit(self.current_word)

        # Reset various states
        self.flush_paint_buffer()
        for player in self.game_data.players.values():
            player.has_found = False
            player.round_score = 0

        self.display_scores()
        QtCore.QTimer.singleShot(self.config["score_time"], self.next_round)

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
        self.hints_timer.stop()

        self.flush_hints()

        self.game_data.has_started = False
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
