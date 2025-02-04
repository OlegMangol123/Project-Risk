import pygame
import os
import sys

from config import *


class Menu:
    def __init__(self, stats: dict):

        # Загрузка кнопок и логотипа
        self.logo = pygame.image.load(
            os.path.join(
                "GAME",
                "menu",
                "sprites",
                "smth",
                "logo.png"))

        self.stats = stats
        self.first_font = pygame.font.SysFont(None, 40, bold=True)
        self.font = pygame.font.SysFont(None, 30)

        self.logo = pygame.transform.scale(self.logo, (184, 75))

    def update(self):
        ...

    def draw(self, screen):
        f = pygame.draw.rect(screen, '#050505', (0, 0, WIDTH, 100))
        screen.blit(self.logo, (17, 17))

        text = self.first_font.render(f'Вы погибли!', True, '#FF3232')
        rect = text.get_rect(center=f.center)
        screen.blit(text, rect)

        for i, (name, value) in enumerate(self.stats.items()):
            q = pygame.draw.rect(
                screen, ('#000000' if i %
                         2 == 0 else '#050505'), (0, 100 + i * 75, WIDTH, 75))
            text = self.font.render(name, True, '#FFFFFF')
            rect = text.get_rect(
                topleft=(
                    q.topleft[0] + 30,
                    q.topleft[1] + 30))
            screen.blit(text, rect)

            text = self.font.render(value, True, '#FFFFFF')
            rect = text.get_rect(
                topright=(
                    q.topright[0] - 30,
                    q.topright[1] + 30))
            screen.blit(text, rect)


def terminate() -> None:
    pygame.quit()
    sys.exit()


def main_death(stats: dict):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Main Menu")
    clock = pygame.time.Clock()
    menu = Menu(stats)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        menu.update()
        screen.fill((0, 0, 0))  # Черный фон для меню
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
