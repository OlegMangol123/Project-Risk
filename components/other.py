import pygame


def load_image(path) -> pygame.Surface | None:
    try:
        return pygame.image.load(path)
    except FileNotFoundError:
        print(f"FileNotFoundError: No file '{path}'")
        return