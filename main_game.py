import pygame
import os
import math
import random

from config import *

all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()

indestructible_block_type = pygame.sprite.Group() 
impassable_block_type = pygame.sprite.Group()


def load_image(path) -> pygame.Surface | None:
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

        self.rect = self.image.get_rect(center = (x, y))
        self.speed = speed

        angle -= 90
        self.dx = math.cos(math.radians(angle)) * self.speed
        self.dy = math.sin(math.radians(angle)) * self.speed
    
    def update(self) -> None:
        # движение пули
        self.rect.x += self.dx
        self.rect.y += self.dy

        if pygame.sprite.spritecollideany(self, indestructible_block_type):
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        # отрисовка пули
        screen.blit(self.image, self.rect.center)


class Block(pygame.sprite.Sprite):
    image: pygame.Surface

    def __init__(self, x: int, y: int, *groups):
        super().__init__(all_sprites, *groups)
        self.rect = self.image.get_rect(topleft = (x, y))
    
    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect.topleft)


class Wall(Block):
    image = load_image(os.path.join("GAME", "blocks", "1.png"))

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, indestructible_block_type, impassable_block_type)


class Grass(Block):
    image = load_image(os.path.join("GAME", "blocks", "0.png"))

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        

class Player(pygame.sprite.Sprite):
    image = load_image(os.path.join("GAME", "Cammando", "untitled.png"))

    def __init__(self, x: int, y: int, speed: float = 5.) -> None:
        super().__init__()

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hitbox_size = 30
        self.hitbox = pygame.Rect(self.rect.centerx - self.hitbox_size // 2,
                                  self.rect.centery - self.hitbox_size // 2,
                                  self.hitbox_size, self.hitbox_size)
        self.money = 100  # Начальное количество денег

        self.image_rotated = self.image

    def update(self, mouse_pos: tuple[int, int]) -> None:
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
        for sprite in impassable_block_type:
            if self.hitbox.colliderect(sprite.rect):
                self.rect = original_rect
    
    def get_distance(self, object: pygame.sprite.Sprite) -> float:
        return math.sqrt((self.rect.centerx - object.rect.centerx) ** 2 + (self.rect.centery - object.rect.centery) ** 2)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_rotated, self.rect.topleft)
        # Отображение денег в формате ${количество денег}
        font = pygame.font.SysFont(None, 36)
        money_text = font.render(f"${self.money}", True, (255, 255, 0))
        screen.blit(money_text, (10, 10))  # Отображение денег в левом верхнем углу


class Camera:
    def __init__(self) -> None:
        self.dx = 0
        self.dy = 0
        self.smoothness = 0.1
        
    def apply(self, obj: pygame.sprite.Sprite) -> None:
        obj.rect.x += self.dx
        obj.rect.y += self.dy
    
    def update(self, target: Player) -> None:
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Chest(pygame.sprite.Sprite):
    image = load_image(os.path.join("GAME", "chests", "normal", "chest.png"))
    image_opened = load_image(os.path.join("GAME", "chests", "normal", "chest_.png"))

    animation_frames = [load_image(os.path.join("GAME", "chests", "normal", f"chest{i}.png")) for i in range(1, 6)]

    def __init__(self, x: int, y: int, price: int = 25) -> None:
        super().__init__()
        self.rect = self.image.get_rect(center=(x, y))
        self.price = price
        self.is_opened = False

        self.current_frame = 0

    def draw(self, screen: pygame.Surface, player: Player) -> None:
        if self.is_opened:
            screen.blit(self.image_opened, self.rect.topleft)
        else:
            screen.blit(self.image, self.rect.topleft)
            if player.get_distance(self) < 150:  # Отображаем цену только если игрок рядом
                screen.blit(self.image_opened, self.rect.topleft)
                font = pygame.font.SysFont(None, 36)
                price_text = font.render(f"${self.price}", True, (255, 255, 0))
                screen.blit(price_text, (self.rect.x + 70, self.rect.y + 40))  # Изменено положение текста

    def update(self, player: Player) -> None:
        if not self.is_opened and player.hitbox.colliderect(self.rect):
            if pygame.key.get_pressed()[pygame.K_e]:  # Если игрок нажимает "E"
                if player.money >= self.price:  # Проверяем, достаточно ли денег
                    player.money -= self.price  # Забираем деньги у игрока
                    self.is_opened = True
                    self.current_frame += 1

        # Обработка анимации
        if self.current_frame > 0:
            if self.current_frame < len(self.animation_frames):
                self.image_opened = self.animation_frames[self.current_frame]
                self.current_frame += 1
            else:
                self.current_frame = 0


class CorruptedChest(Chest):
    image = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest.png"))
    image_opened = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest_.png"))

    animation_frames = [load_image(os.path.join("GAME", "chests", "corrupted chest", f"chest{i}.png")) for i in range(1, 6)]

    def __init__(self, x: int, y: int, price: int = 75) -> None:
        super().__init__(x, y, price)


def get_gun_coord(player: Player, hand: bool) -> tuple[int, int]:
    """ определение координат оружий относительно игрока """

    f = 60.72890558 # длинна гипотенузы
    angle = player.angle - 90
    angle = math.radians(angle + 17.24 * (1 if hand else -1))

    x = player.rect.centerx + math.cos(angle) * f
    y = player.rect.centery + math.sin(angle) * f

    return x, y


def main_game() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    interface_image = pygame.Surface((WIDTH, 120))
    interface_image.fill((0, 0, 0))

    _map = [
        ['#########',
         '#.......#',
         '#...c...#',
         '#.......#',
         '#...@...#',
         '#.......#',
         '#...C...#',
         '#.......#',
         '#########']
    ]

    chests = []

    for _, room in enumerate(_map):
        for y, row in enumerate(room):
            for x, col in enumerate(row):
                coords = 120 * x, 120 * y

                Grass(*coords)

                if col == '#':
                    Wall(*coords)
                if col == '@':
                    player = Player(coords[0] + 60, coords[1] + 60)
                
                if col == 'c':
                    chests.append(Chest(coords[0] + 60, coords[1] + 40))
                if col == 'C':
                    chests.append(CorruptedChest(coords[0] + 60, coords[1] + 40))

    shooting = False
    shooting_cooldown = 0
    hand = False

    camera = Camera()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    shooting_cooldown = 0
                    shooting = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    shooting = False

        mouse_pos = pygame.mouse.get_pos()

        screen.fill("black")

        all_sprites.draw(screen)
        for chest in chests:
            chest.draw(screen, player)
        player.draw(screen)
        bullets_group.draw(screen)

        player.update(mouse_pos)
        camera.update(player)

        all_sprites.update()
        for chest in chests:
            chest.update(player)
        bullets_group.update()

        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in chests:
            camera.apply(sprite)
        camera.apply(player)

        if shooting_cooldown > 150:
            shooting_cooldown = 0

        if shooting and shooting_cooldown == 0:
            Bullet(*get_gun_coord(player, hand), player.angle)
            hand = not hand

        pygame.display.flip()

        shooting_cooldown += clock.get_time()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main_game()
