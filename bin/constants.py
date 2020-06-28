import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESSOURCES_DIR = os.path.join(ROOT_DIR, "bin", "gui", "ressources")

AVATARS = (("Chandler", os.path.join(RESSOURCES_DIR, "avatars", "Chandler.png")),
           ("Gael", os.path.join(RESSOURCES_DIR, "avatars", "Gael.png")),
           ("Joy", os.path.join(RESSOURCES_DIR, "avatars", "Joy.png")),
           ("Meena", os.path.join(RESSOURCES_DIR, "avatars", "Meena.png")),
           ("Francis", os.path.join(RESSOURCES_DIR, "avatars", "Francis.png")))
