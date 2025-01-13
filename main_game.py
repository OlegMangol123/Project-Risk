import pygame
import os
import math
import random

from config import *

all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()


def load_image(path):
    try:
        return pygame.image.load(path)
    except FileNotFoundError:
        print(f"FileNotFoundError: No file '{path}'")
        return


class Bullet(pygame.sprite.Sprite):
    image = load_image(os.path.join("GAME", "ENTITY", "bullet.png"))

    def __init__(self, x: int, y: int, angle: float, speed: float = 20.) -> None:
        super().__init__(bullets_group, all_sprites)

        self.image = pygame.transform.rotate(self.image, -angle) # поворот пули

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

        angle -= 90
        self.dx = math.cos(math.radians(angle)) * self.speed
        self.dy = math.sin(math.radians(angle)) * self.speed
    
    def update(self) -> None:
        # движение пули
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen: pygame.Surface) -> None:
        # отрисовка пули
        screen.blit(self.image, self.rect.center)
        

class Player:
    def __init__(self, x: int, y: int, speed: int = 5) -> None:
        self.image = load_image(os.path.join("GAME", "Cammando", "untitled.png"))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hitbox_size = 30
        self.hitbox = pygame.Rect(self.rect.centerx - self.hitbox_size // 2,
                                  self.rect.centery - self.hitbox_size // 2,
                                  self.hitbox_size, self.hitbox_size)
        self.money = 100  # Начальное количество денег

    def update(self, mouse_pos: tuple[int, int], walls: list) -> None:
        # Поворот персонажа в сторону мыши
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        self.angle = (math.degrees(math.atan2(rel_y, rel_x)) + 360 + 90) % 360
        self.image_rotated = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.image_rotated.get_rect(center=self.rect.center)

        # Движение игрока
        keys = pygame.key.get_pressed()
        original_rect = self.rect.copy()  # Сохраняем оригинальное положение

        if keys[pygame.K_w]:  # Вверх
            self.rect.y -= self.speed
        if keys[pygame.K_s]:  # Вниз
            self.rect.y += self.speed
        if keys[pygame.K_a]:  # Влево
            self.rect.x -= self.speed
        if keys[pygame.K_d]:  # Вправо
            self.rect.x += self.speed

        # Проверка столкновений с стенами
        self.hitbox.center = self.rect.center  # Обновляем хитбокс
        for wall in walls:
            if self.hitbox.colliderect(wall):
                self.rect = original_rect

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_rotated, self.rect.topleft)
        # Отображение денег в формате ${количество денег}
        font = pygame.font.SysFont(None, 36)
        money_text = font.render(f"${self.money}", True, (255, 255, 0))
        screen.blit(money_text, (10, 10))  # Отображение денег в левом верхнем углу


class Chest:
    def __init__(self, x: int, y: int, price: int = 25) -> None:
        self.image_normal = load_image(os.path.join("GAME", "chests", "normal", "chest.png"))
        self.image_opened = load_image(os.path.join("GAME", "chests", "normal", "chest_.png"))
        self.rect = self.image_normal.get_rect(center=(x, y))
        self.price = price
        self.is_opened = False
        self.animation_frames = [load_image(os.path.join("GAME", "chests", "normal", f"chest{i}.png")) for i in range(1, 6)]
        self.current_frame = 0
        self.animation_playing = False

    def draw(self, screen: pygame.Surface, player: Player) -> None:
        if self.is_opened:
            screen.blit(self.image_opened, self.rect.topleft)
        else:
            screen.blit(self.image_normal, self.rect.topleft)
            # Проверяем расстояние до игрока
            distance = math.sqrt((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2)
            if distance < 150:  # Отображаем цену только если игрок рядом
                font = pygame.font.SysFont(None, 36)
                price_text = font.render(f"${self.price}", True, (255, 255, 0))
                screen.blit(price_text, (self.rect.x + 70, self.rect.y + 40))  # Изменено положение текста

    def update(self, player: Player) -> None:
        # Измеряем расстояние до игрока
        distance = math.sqrt((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2)

        if distance < 150:
            self.image_normal = load_image(os.path.join("GAME", "chests", "normal", "chest_.png"))  # Изменяем спрайт
        else:
            self.image_normal = load_image(os.path.join("GAME", "chests", "normal", "chest.png"))  # Возвращаем обратно

        if not self.is_opened and player.hitbox.colliderect(self.rect):
            if pygame.key.get_pressed()[pygame.K_e]:  # Если игрок нажимает "E"
                if player.money >= self.price:  # Проверяем, достаточно ли денег
                    player.money -= self.price  # Забираем деньги у игрока
                    self.is_opened = True
                    self.animation_playing = True

        # Обработка анимации
        if self.animation_playing:
            if self.current_frame < len(self.animation_frames):
                self.image_opened = self.animation_frames[self.current_frame]
                self.current_frame += 1
            else:
                self.animation_playing = False


class CorruptedChest:
    def __init__(self, x: int, y: int, price: int = 75) -> None:
        self.image_normal = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest.png"))
        self.image_opened = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest_.png"))
        self.rect = self.image_normal.get_rect(center=(x, y))
        self.price = price
        self.is_opened = False

        # Кадры анимации открытия сундука
        self.opening_animation_frames = [
            load_image(os.path.join("GAME", "chests", "corrupted chest", f"chest{i}.png")) for i in range(1, 6)
        ]
        self.current_opening_frame = 0
        self.opening_animation_playing = False

        # Кадры глитча
        self.glitch_animation_frames = [
            load_image(os.path.join("GAME", "chests", "corrupted chest", "glitch", f"chest{i}.png")) for i in range(1, 11)
        ]
        self.current_glitch_frame = 0
        self.glitch_animation_active = False

        # Параметры глича
        self.glitch_probability = 0.01  # Вероятность активации глича (1%)
        self.glitch_distance_threshold = 150  # Максимальное расстояние для активации глича

    def draw(self, screen: pygame.Surface, player: Player) -> None:
        if self.is_opened:
            screen.blit(self.image_opened, self.rect.topleft)
        elif self.glitch_animation_active:
            # Убедитесь, что текущий кадр не выходит за пределы массива
            if self.current_glitch_frame < len(self.glitch_animation_frames):
                screen.blit(self.glitch_animation_frames[self.current_glitch_frame], self.rect.topleft)
        else:
            screen.blit(self.image_normal, self.rect.topleft)

            # Проверяем расстояние до игрока
            distance = math.sqrt((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2)
            if distance < self.glitch_distance_threshold:
                font = pygame.font.SysFont(None, 36)
                price_text = font.render(f"${self.price}", True, (255, 255, 0))
                screen.blit(price_text, (self.rect.x + 70, self.rect.y + 40))  # Отображение цены только рядом с игроком

    def update(self, player: Player) -> None:
        # Измеряем расстояние до игрока
        distance = math.sqrt((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2)

        if distance < 150:
            self.image_normal = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest_.png"))
        else:
            self.image_normal = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest.png"))

        if not self.is_opened and player.hitbox.colliderect(self.rect):
            if pygame.key.get_pressed()[pygame.K_e]:
                if player.money >= self.price:
                    player.money -= self.price
                    self.is_opened = True
                    self.opening_animation_playing = True

        # Обработка анимации открытия сундука
        if self.opening_animation_playing:
            if self.current_opening_frame < len(self.opening_animation_frames):
                self.image_opened = self.opening_animation_frames[self.current_opening_frame]
                self.current_opening_frame += 1
            else:
                self.opening_animation_playing = False

        # Проверяем расстояние до игрока
        if distance >= self.glitch_distance_threshold:
            # Проверяем вероятность активации глича
            if not self.glitch_animation_active and random.random() < self.glitch_probability:
                self.glitch_animation_active = True
                self.current_glitch_frame = 0  # Сброс текущего кадра для глитча

        # Обработка анимации глитча
        if self.glitch_animation_active:
            # Убедитесь, что текущий кадр не выходит за пределы массива
            if self.current_glitch_frame < len(self.glitch_animation_frames):
                self.current_glitch_frame += 1
            else:
                self.glitch_animation_active = False
                self.current_glitch_frame = 0  # Сброс текущего кадра


def main_game() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    floor_image = load_image(os.path.join("GAME", "blocks", "0.png"))
    wall_image = load_image(os.path.join("GAME", "blocks", "1.png"))

    interface_image = pygame.Surface((WIDTH, 120))
    interface_image.fill((0, 0, 0))

    walls = []
    room_matrix = [
        ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
    ]

    for row in range(len(room_matrix)):
        for col in range(len(room_matrix[row])):
            if room_matrix[row][col] == 1:
                wall_rect = pygame.Rect(col * 120, row * 120, 120, 120)
                walls.append(wall_rect)

    player = Player(WIDTH // 2, HEIGHT // 2)
    chest = Chest(WIDTH // 2, HEIGHT // 2 - 100)
    corrupted_chest = CorruptedChest(WIDTH // 2, HEIGHT // 2 + 100)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)

        mouse_pos = pygame.mouse.get_pos()
        player.update(mouse_pos, walls)
        chest.update(player)
        bullets_group.update()
        corrupted_chest.update(player)

        screen.fill("black")
        for row in range(len(room_matrix)):
            for col in range(len(room_matrix[row])):
                if room_matrix[row][col] == 1:
                    screen.blit(wall_image, (col * 120, row * 120))
                elif room_matrix[row][col] == 0:
                    screen.blit(floor_image, (col * 120, row * 120))
                elif room_matrix[row][col] == "_":
                    screen.blit(interface_image, (0, row * 120))

        chest.draw(screen, player)  # Передаем игрока в draw
        corrupted_chest.draw(screen, player)  # Передаем игрока в draw
        player.draw(screen)
        bullets_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main_game()
