import os
import math
import random

import pygame
from pygame import Color

from components.other import load_image
from components import items 

from config import *
#

all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()

indestructible_block_type = pygame.sprite.Group() 
destructible_block_type = pygame.sprite.Group()
impassable_block_type = pygame.sprite.Group()
#

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
#

INV_BUTTONS = (pygame.K_1, pygame.K_2, pygame.K_3,pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9)


class Bullet(pygame.sprite.Sprite):
    image = load_image(os.path.join("GAME", "ENTITY", "bullet.png"))

    def __init__(self, x: int, y: int, angle: float, damage: int = 10, speed: float = 20.) -> None:
        super().__init__(bullets_group, all_sprites)

        self.angle = angle
        self.image = pygame.transform.rotate(self.image, -self.angle) # поворот пули

        self.rect = self.image.get_rect(center = (x, y))
        self.speed = speed
        self.damage = damage

        self.lives = 5

        self.angle -= 90
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = math.sin(math.radians(self.angle)) * self.speed
    
    def update(self) -> None:
        # движение пули
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.check()

        if (obj := pygame.sprite.spritecollideany(self, destructible_block_type)):
            if self.lives:
                obj.kill()

                self.lives -= 1
            else:
                self.kill()

    def check(self) -> None:
        if pygame.sprite.spritecollideany(self, indestructible_block_type):
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        # отрисовка пули
        screen.blit(self.image, self.rect.center)


class EnergyBullet(Bullet):
    image = load_image(os.path.join("GAME", "ENTITY", "energy_bullet.png"))

    def __init__(self, x: int, y: int, angle: float, damage: int = 20):
        super().__init__(x, y, angle, damage = damage)

        self.lives = 10
    
    def check(self) -> None:
        if pygame.sprite.spritecollideany(self, indestructible_block_type):
            if self.lives:
                self.image = pygame.transform.rotate(self.image, 90)

                self.angle -= 90
                self.dx = math.cos(math.radians(self.angle)) * self.speed
                self.dy = math.sin(math.radians(self.angle)) * self.speed

                self.lives -= 1
            else:
                self.kill()

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

        self.max_greade = self.grenade = 1

        self.max_sprint = self.sprint = 1
        self.sprint_angle = 0
        self.sprint_reload_cooldown = 0
        self.max_sprint_value = self.sprint_value = 80

        self.max_bullets = self.bullets = 15
        self.bullets_shooting = False
        self.bullets_shooting_cooldown = 0
        self.bullets_reload_cooldown = 0

        self.max_energy_bullets = self.energy_bullets = 7
        self.e_bullets_shooting = False
        self.e_bullets_shooting_cooldown = 0
        self.e_bullets_reload_cooldown = 0

        self.hand = False

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hitbox_size = 30
        self.hitbox = pygame.Rect(self.rect.centerx - self.hitbox_size // 2,
                                  self.rect.centery - self.hitbox_size // 2,
                                  self.hitbox_size, self.hitbox_size)
        self.money = 500  # Начальное количество денег

        self.max_items = 9
        self.items = {}
        self.active_slot = 0

        self.image_rotated = self.image

        self.max_hp = self.hp = 100

    def update(self, mouse_pos: tuple[int, int]) -> None:
        # Поворот персонажа в сторону мыши
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        self.angle = (math.degrees(math.atan2(rel_y, rel_x)) + 360 + 90) % 360
        self.image_rotated = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.image_rotated.get_rect(center=self.rect.center)

        # Движение игрока
        keys = pygame.key.get_pressed()
        original_rect = self.rect.copy()  # Сохраняем оригинальное положение

        if (keys[pygame.K_LSHIFT] and self.sprint) or (self.sprint_value != self.max_sprint_value):
            self.rect.x += math.sin(math.radians(self.angle)) * self.sprint_value
            self.rect.y -= math.cos(math.radians(self.angle)) * self.sprint_value
            self.sprint_value -= 10
        
            if self.sprint:
                self.sprint -= 1
                self.sprint_reload_cooldown = 2000
            if self.sprint_value == 0:
                self.sprint_value = self.max_sprint_value
        
        if self.sprint_reload_cooldown <= 0:
            self.sprint = self.max_sprint

        if keys[pygame.K_w]:  # Вверх
            self.rect.y -= self.speed
        if keys[pygame.K_s]:  # Вниз
            self.rect.y += self.speed
        if keys[pygame.K_a]:  # Влево
            self.rect.x -= self.speed
        if keys[pygame.K_d]:  # Вправо
            self.rect.x += self.speed
        
        for i, key in enumerate(INV_BUTTONS):
            if keys[key]:
                self.active_slot = i
                break

        # Проверка столкновений с стенами
        self.hitbox.center = self.rect.center  # Обновляем хитбокс
        for sprite in impassable_block_type:
            if self.hitbox.colliderect(sprite.rect):
                self.rect = original_rect

        buttons = pygame.mouse.get_pressed()
        # обычные патроны
        if buttons[0] and not self.bullets_shooting:
            self.bullets_shooting = True
            self.bullets_shooting_cooldown = 0

        if self.bullets_shooting_cooldown > 150:
            self.bullets_shooting_cooldown = 0

        if self.bullets_shooting and self.bullets_shooting_cooldown == 0:
            self.bullets_reload_cooldown = 500
            if self.bullets > 0:
                Bullet(*get_gun_coord(self.rect.center, self.angle, self.hand), self.angle)
                self.bullets -= 1
                self.hand = not self.hand

        if self.bullets_reload_cooldown <= 0 and self.bullets < self.max_bullets:
            self.bullets += 1
            self.bullets_reload_cooldown = 50

        # заряженные патроны
        if buttons[2] and not self.e_bullets_shooting:
            self.e_bullets_shooting = True
            self.e_bullets_shooting_cooldown = 0

        if self.e_bullets_shooting_cooldown > 150:
            self.e_bullets_shooting_cooldown = 0

        if self.e_bullets_shooting and self.e_bullets_shooting_cooldown == 0:
            self.e_bullets_reload_cooldown = 1000
            if self.energy_bullets > 0:
                EnergyBullet(*get_gun_coord(self.rect.center, self.angle, self.hand), self.angle)
                self.energy_bullets -= 1
                self.hand = not self.hand

        if self.e_bullets_reload_cooldown <= 0 and self.energy_bullets < self.max_energy_bullets:
            self.energy_bullets += 1
            self.e_bullets_reload_cooldown = 125

        time = clock.get_time()
        self.e_bullets_shooting_cooldown += time
        self.bullets_shooting_cooldown += time
        self.bullets_reload_cooldown -= time
        self.e_bullets_reload_cooldown -= time
        self.sprint_reload_cooldown -= time
    
        if not buttons[0]:
            self.bullets_shooting = False
        if not buttons[2]:
            self.e_bullets_shooting = False  
    
    def get_distance(self, object: pygame.sprite.Sprite) -> float:
        return math.sqrt((self.rect.centerx - object.rect.centerx) ** 2 + (self.rect.centery - object.rect.centery) ** 2)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_rotated, self.rect.topleft)
    
    def add_item(self, item: items.Item, count: int = 1) -> None:
        if len(self.items) < self.max_items:
            self.items.setdefault(item, 0)
            self.items[item] += count

    def use_item(self) -> None:
        if self.active_slot < len(self.items):
            item = list(sorted(self.items.items(), key=lambda a: a[0].name))[self.active_slot][0]
            if self.items[item] == 1:
                self.items.pop(item)
            else:
                self.items[item] -= 1


class Lem(pygame.sprite.Sprite):
    idle_image = load_image(os.path.join("GAME", "enemy", "lem", "idle.png"))
    attack_anim1 = [load_image(os.path.join("GAME", "enemy", "lem", "at1", f"{i}.png"))
                    for i in range(1, 7)]
    attack_anim2 = [load_image(os.path.join("GAME", "enemy", "lem", "at2", f"{i}.png"))
                    for i in range(1, 5)]
    
    image_rotated = image = idle_image

    def __init__(self, x: int, y: int) -> None:
        super().__init__(monsters_group)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.hitbox_size = 30
        self.hitbox = pygame.Rect(0, 0, self.hitbox_size, self.hitbox_size)
        self.hitbox.center = self.rect.center

    def update(self, player: Player) -> None:
        rel_x = player.rect.centerx - self.rect.centerx
        rel_y = player.rect.centery - self.rect.centery
        angle = math.degrees(math.atan2(rel_x, rel_y))
        self.image_rotated = pygame.transform.rotate(self.image, angle)
        self.rect = self.image_rotated.get_rect(center=self.rect.center)

        if (rel_x, rel_y) == (0, 0):
            return

        direction = pygame.math.Vector2(rel_x, rel_y).normalize()
        original_rect = self.rect.copy()
        
        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed
        self.hitbox.center = self.rect.center

        collision = any(
            self.hitbox.colliderect(block.rect) 
            for block in impassable_block_type
        )

        if collision:
            perp1 = pygame.math.Vector2(-direction.y, direction.x)
            perp2 = pygame.math.Vector2(direction.y, -direction.x)
            
            test_rect1 = original_rect.move(perp1 * self.speed)
            collision1 = any(
                test_rect1.colliderect(block.rect) 
                for block in impassable_block_type
            )
            
            test_rect2 = original_rect.move(perp2 * self.speed)
            collision2 = any(
                test_rect2.colliderect(block.rect) 
                for block in impassable_block_type
            )

            if not collision1:
                self.rect = test_rect1
            elif not collision2:
                self.rect = test_rect2
            else:
                self.rect = original_rect

            self.hitbox.center = self.rect.center

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_rotated, self.rect.topleft)


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


class Interface:
    hp_bar_background = Color(92, 172, 64)
    hp_bar_background_none = Color(34, 56, 19)
    hp_bar_text_color = Color(242, 249, 216)

    m1_skill = load_image(os.path.join("GAME", "gui", "skills", "m1.png"))
    off_m1_skill = m1_skill.copy()
    off_m1_skill.set_alpha(50)
    #
    m2_skill = load_image(os.path.join("GAME", "gui", "skills", "m2.png"))
    off_m2_skill = m2_skill.copy()
    off_m2_skill.set_alpha(50)
    #
    shift_skill = load_image(os.path.join("GAME", "gui", "skills", "shift.png"))
    off_shift_skill = shift_skill.copy()
    off_shift_skill.set_alpha(50)
    #
    r_skill = load_image(os.path.join("GAME", "gui", "skills", "r.png"))
    off_r_skill = r_skill.copy()
    off_r_skill.set_alpha(50)

    def __init__(self) -> None:
        ...
    
    def draw(self, screen: pygame.surface.Surface, player: Player) -> None:
        # border
        pygame.draw.rect(screen, "#000000", (0, 0, WIDTH, 85))
        pygame.draw.rect(screen, "#000000", (0, HEIGHT - 100, WIDTH, 100))

        self.draw_graph(screen, self.hp_bar_background_none, self.hp_bar_background, self.hp_bar_text_color,
                        50, HEIGHT - 65, 254, 30, player.hp // player.max_hp, f"{player.hp} / {player.max_hp}")
        
        items = (
            (player.bullets, player.max_bullets, 'M1', self.m1_skill, self.off_m1_skill),
            (player.energy_bullets, player.max_energy_bullets, 'M2', self.m2_skill, self.off_m2_skill),
            (player.sprint, player.max_sprint, 'SHIFT', self.shift_skill, self.off_shift_skill),
            (player.grenade, player.max_greade, 'R', self.r_skill, self.off_r_skill)
        )

        self.draw_skills(screen, WIDTH - 100, HEIGHT - 90, items)

        inv = list(sorted(player.items.items(), key=lambda a: a[0].name))
        inv += [None] * (9 - len(inv))
        self.draw_inv(screen, 240, 10, inv, player.active_slot)

        font = pygame.font.SysFont(None, 35)
        text = font.render(f'${player.money}', True, '#FFFF00')
        screen.blit(text, (10, 10))
    
    def draw_graph(self, screen: pygame.Surface,
                   background_color: Color, graph_color: Color, text_color: Color,
                   x: int, y: int, width: int, height: int,
                   value: float, text: str = "") -> None:
        pygame.draw.rect(screen, background_color, (x, y, width, height))
        pygame.draw.rect(screen, graph_color, (x, y, int(width * value), height))

        font = pygame.font.SysFont(None, int(min(width, height) * 1.3))
        text = font.render(text, True, text_color)
        place = text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text, place)
    
    def draw_skills(self, screen: pygame.Surface, right_x: int, right_y: int,
                   items: tuple[ tuple[int, int, str, pygame.Surface] ]) -> None:
        for i, (current, _max, title, image, off_image) in enumerate(items[::-1]):
            fill = int(64 * (1 - current / _max))
            if fill > 0:
                screen.blit(off_image, (right_x - 64 * i, right_y))
            rect = pygame.Rect(0, fill, 64, 64 - fill)
            screen.blit(image.subsurface(rect), (right_x - 64 * i, right_y + fill))
            place = pygame.draw.rect(screen, '#FFFFFF', (right_x - 64 * i, right_y + 68, 64, 20))

            font = pygame.font.SysFont(None, 25)
            text = font.render(title, True, '#000000')
            screen.blit(text, place.topleft)
    
    def draw_inv(self, screen: pygame.Surface, x: int, y: int,
                 items: tuple[ tuple[items.Item, int] ], active: int) -> None:
        for i, data in enumerate(items):
            place = pygame.draw.rect(screen, "#404974", (x + i * 60, y, 60, 60))

            if i == active:
                pygame.draw.rect(screen, "#FFFFFF", (x + i * 60, y, 60, 60), 2)

            if not data:
                continue

            item, count = data
            screen.blit(item.image_item, place.topleft)
            font = pygame.font.SysFont(None, 30)
            text = font.render(f"x{count}", True, "#FFFFFF")
            screen.blit(text, (place.bottomright[0] - text.get_size()[0], place.bottomright[1] - text.get_size()[1]))


class Chest(pygame.sprite.Sprite):
    image = load_image(os.path.join("GAME", "chests", "normal", "chest.png"))
    image_opened = load_image(os.path.join("GAME", "chests", "normal", "chest_.png"))

    animation_frames = [load_image(os.path.join("GAME", "chests", "normal", f"chest{i}.png")) for i in range(1, 6)]

    chance_item = (
        (0, 80),
        (1, 19),
        (3, 1)
    )

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

                    random_item = items.get_random(random.choices(tuple(map(lambda a: a[0], self.chance_item)),
                                                                  tuple(map(lambda b: b[1], self.chance_item)))[0])
                    
                    player.add_item(random_item)

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

    chance_item = (
        (2, 100),
    )

    def __init__(self, x: int, y: int, price: int = 75) -> None:
        super().__init__(x, y, price)


def get_gun_coord(coords: tuple[int, int], angle: float, hand: bool) -> tuple[int, int]:
    """ определение координат оружий относительно игрока """

    f = 60.72890558 # длинна гипотенузы
    angle -= 90
    angle = math.radians(angle + 17.24 * (1 if hand else -1))

    x = coords[0] + math.cos(angle) * f
    y = coords[1] + math.sin(angle) * f

    return x, y


def main_game() -> None:
    interface = Interface()

    _map = [
        ['#############',
         '#...........#',
         '#....#......#',
         '#....#......#',
         '#....#......#',
         '#.c.c.c.c.c.#',
         '#...........#',
         '#.....@.....#',
         '#...........#',
         '#...C...C...#',
         '#...........#',
         '#....M......#',
         '#...........#',
         '#############']
    ]

    chests = []
    monsters = []

    for _, room in enumerate(_map):
        for y, row in enumerate(room):
            for x, col in enumerate(row):
                coords = 80 * x, 80 * y

                Grass(*coords)

                if col == '#':
                    Wall(*coords)
                if col == '@':
                    player = Player(coords[0] + 60, coords[1] + 60)
                
                if col == 'c':
                    chests.append(Chest(coords[0] + 40, coords[1] + 20))
                if col == 'C':
                    chests.append(CorruptedChest(coords[0] + 40, coords[1] + 20))
                
                if col == 'M':
                    monsters.append(Lem(coords[0] + 60, coords[1] + 60))

    camera = Camera()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    player.use_item()
        mouse_pos = pygame.mouse.get_pos()

        screen.fill("black")

        all_sprites.draw(screen)
        for chest in chests:
            chest.draw(screen, player)
        for monster in monsters:
            monster.draw(screen)
        player.draw(screen)
        bullets_group.draw(screen)

        interface.draw(screen, player)

        bullets_group.update()
        player.update(mouse_pos)
        camera.update(player)

        all_sprites.update()

        for chest in chests:
            chest.update(player)
        for monster in monsters:
            monster.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in monsters:
            camera.apply(sprite)
        for sprite in chests:
            camera.apply(sprite)
        camera.apply(player)

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
