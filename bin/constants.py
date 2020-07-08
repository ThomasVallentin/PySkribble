import os

ROOT_DIR = os.path.dirname(__file__)
RESSOURCES_DIR = os.path.join(ROOT_DIR, "ressources")

DEFAULT_CONFIG = {"choices_count": 3,
                  "score_time": 10000,
                  "choosing_time": 30000,
                  "drawing_time": 80000}
