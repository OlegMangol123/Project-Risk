import pygame
import os
import sys
from main_game import main_game  # Импортируем функцию main_game из main_game.py

from config import *


class Menu:
    def __init__(self):
        self.sprite_images = self.load_sprites()
        self.current_frame = 0
        self.frame_time = 200  # Время между кадрами в миллисекундах
        self.last_update = pygame.time.get_ticks()

        # Загрузка кнопок и логотипа
        self.play_button = pygame.image.load(os.path.join("GAME", "menu", "sprites", "smth", "play.png"))
        self.quit_button = pygame.image.load(os.path.join("GAME", "menu", "sprites", "smth", "quit.png"))
        self.logo = pygame.image.load(os.path.join("GAME", "menu", "sprites", "smth", "logo.png"))

        # Изменение размеров кнопок
        self.play_button = pygame.transform.scale(self.play_button, (384, 100))
        self.quit_button = pygame.transform.scale(self.quit_button, (384, 100))
        # Логотип оставляем без изменений

        # Позиции кнопок и логотипа (слева)
        self.logo_rect = self.logo.get_rect(topleft=(50, 150))  # Логотип
        self.play_button_rect = self.play_button.get_rect(topleft=(50, 200 + 300))  # Кнопка "Играть" ниже логотипа
        self.quit_button_rect = self.quit_button.get_rect(topleft=(50, 320 + 300))  # Кнопка "Выйти" ниже кнопки "Играть"

    def load_sprites(self):
        sprites = []
        sprite_folder = os.path.join("GAME", "menu", "sprites", "anim")
        for i in range(1, 21):
            image_path = os.path.join(sprite_folder, f"menu{i}.png")
            sprites.append(pygame.image.load(image_path))
        return sprites

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_time:
            self.current_frame = (self.current_frame + 1) % len(self.sprite_images)
            self.last_update = current_time

    def draw(self, screen):
        # Отрисовка текущего кадра анимации
        screen.blit(self.sprite_images[self.current_frame], (0, 0))

        # Отрисовка логотипа и кнопок
        screen.blit(self.logo, self.logo_rect)
        screen.blit(self.play_button, self.play_button_rect)
        screen.blit(self.quit_button, self.quit_button_rect)

    def check_buttons(self, pos):
        if self.play_button_rect.collidepoint(pos):
            # Запускаем игру при нажатии на кнопку "Играть"
            main_game()  # Вызов функции main_game из main_game.py
        elif self.quit_button_rect.collidepoint(pos):
            pygame.quit()
            sys.exit()

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Main Menu")
    clock = pygame.time.Clock()
    menu = Menu()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    menu.check_buttons(event.pos)

        menu.update()
        screen.fill((0, 0, 0))  # Черный фон для меню
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
