import os

from pygame import mixer

shot_fx = mixer.Sound(os.path.join("GAME", "fx", "shot.mp3"))
e_shot_fx = mixer.Sound(os.path.join("GAME", "fx", "energy_shot.mp3"))

shot_fx.set_volume(.1)
e_shot_fx.set_volume(.1)
