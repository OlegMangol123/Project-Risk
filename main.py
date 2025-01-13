import pygame
import os
import sys
from menu import Menu

from config import *

# Инициализация Pygame
pygame.init()

# Установка размеров окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project of Risk")

# Главный игровой цикл
def main():
    clock = pygame.time.Clock()
    menu = Menu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик мыши
                    menu.check_buttons(event.pos)

        # Обновление меню
        menu.update()

        # Отрисовка меню
        screen.fill((0, 0, 0))  # Очистка экрана
        menu.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)  # Ограничение FPS

if __name__ == "__main__":
    main()
