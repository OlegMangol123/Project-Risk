import os

import pygame

from components.groups import *
from components.other import *


class Door(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, rotate: bool = False) -> None:
        super().__init__(doors_group, indestructible_block_type)

        self.image = images['blocks.door']

        if rotate:
            self.image = pygame.transform.rotate(
                self.image, 90).convert_alpha()

        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen: pygame.Surface, opened: bool) -> None:
        if opened:
            screen.blit(self.image, self.rect.topleft)


class Block(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int, *groups) -> None:
        super().__init__(all_sprites, block_group, *groups)
        self.image: pygame.Surface

        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)


class Wall(Block):
    def __init__(self, x: int, y: int) -> None:
        self.image = images['blocks.wall']

        super().__init__(x, y, indestructible_block_type, impassable_block_type)


class Grass(Block):
    def __init__(self, x: int, y: int) -> None:
        self.image = images['blocks.grass']

        super().__init__(x, y)


class Portal(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, func) -> None:
        super().__init__()
        self.normal_image = images['portal']
        self.selected_image = images['portal.selected']
        self.image = self.normal_image

        self.rect = self.image.get_rect(center=(x, y))

        self.func = func

        self.active = False

    def update(self, player) -> None:
        if player.get_distance(self) <= 200 and not self.active:
            self.image = self.selected_image
            keys = pygame.key.get_pressed()

            if keys[pygame.K_e]:
                print(1)
                self.func(*self.rect.center)
                self.active = True
        else:
            self.image = self.normal_image

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)

    def reset(self, func) -> None:
        self.func = func
        self.active = False
