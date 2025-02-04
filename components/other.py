import os
import pygame


BACKGROUND_COLOR = pygame.Color(0, 0, 0)


def load_image(path, gamma: tuple[int, int, int] = [
               0, 0, 0]) -> pygame.Surface | None:
    try:
        return inc_clrs(pygame.image.load(path), *gamma)
    except FileNotFoundError:
        print(f"FileNotFoundError: No file '{path}'")
        return


def inc_clrs(image: pygame.Surface, dr: int, dg: int, db: int):
    if dr == dg == db == 0:
        return image

    width, height = image.get_size()

    for x in range(width):
        for y in range(height):
            r, g, b, a = image.get_at((x, y))

            r = max(min(r + dr, 255), 0)
            g = max(min(g + dg, 255), 0)
            b = max(min(b + db, 255), 0)

            # Устанавливаем новый цвет пикселя
            image.set_at((x, y), (r, g, b, a))

    return image


pathes = {
    'portal': os.path.join("GAME", "portal", "image.png"),
    'portal.selected': os.path.join("GAME", "portal", "selected.png"),

    'monster_spawn': [os.path.join("GAME", "spawn_area", f"{i}.png") for i in range(1, 7)],

    'blocks.wall': os.path.join("GAME", "blocks", "1.png"),
    'blocks.grass': os.path.join("GAME", "blocks", "0.png"),
    'blocks.door': os.path.join("GAME", "blocks", "2.png"),

    'chest.normal': os.path.join("GAME", "chests", "normal", "chest.png"),
    'chest.selected': os.path.join("GAME", "chests", "normal", "chest_.png"),
    'chest.selected': [os.path.join("GAME", "chests", "normal", f"chest{i}.png") for i in range(1, 6)],
    'chest.corr.normal': os.path.join("GAME", "chests", "normal", "chest.png"),
    'chest.corr.selected': os.path.join("GAME", "chests", "normal", "chest_.png"),
    'chest.corr.selected': [os.path.join("GAME", "chests", "normal", f"chest{i}.png") for i in range(1, 6)],

    'enemy.lem': os.path.join("GAME", "enemy", "lem", "idle.png"),
    'enemy.lem.at1': [os.path.join("GAME", "enemy", "lem", "at1", f"{i}.png") for i in range(1, 8)],
    'enemy.lem.at2': [os.path.join("GAME", "enemy", "lem", "at2", f"{i}.png") for i in range(1, 6)],

    'enemy.quen': os.path.join("GAME", "enemy", "quen", "quen.png"),
    'enemy.quen.at': [os.path.join("GAME", "enemy", "quen", "at", f"at{i}.png") for i in range(1, 5)],
    'entity.quen.harch': os.path.join("GAME", "enemy", "quen", "entity", "harch.png"),
    'entity.quen.harch1': os.path.join("GAME", "enemy", "quen", "entity", "harch1.png"),

    'entity.bullet': os.path.join("GAME", "entity", "bullet.png"),
    'entity.energy_bullet': os.path.join("GAME", "entity", "energy_bullet.png"),
}
images = {}


def convert_path_to_img(gamma: tuple[int, int, int]) -> None:
    for key, path in pathes.items():
        if type(path) is list:
            images[key] = [load_image(f, gamma) for f in path]
        else:
            images[key] = load_image(path, gamma).convert_alpha()
