import os
import math
import random

import pygame
from pygame import Color

from config import *
from components.other import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

from components.database import add_death
from components.groups import *
from components import music
from components import monsters
from components import game_map
from components import items
from components import blocks

from death import main_death

#


class Bullet(pygame.sprite.Sprite):
    image = load_image(os.path.join("GAME", "ENTITY", "bullet.png")).convert_alpha()
    damage = 10

    def __init__(self, x: int, y: int, angle: float, damage: int = 10, speed: float = 30.) -> None:
        super().__init__(bullets_group, all_sprites)

        self.angle = angle
        self.image = pygame.transform.rotate(self.image, -self.angle)  # поворот пули

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.damage = damage

        self.lives = 5

        self.angle -= 90
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = math.sin(math.radians(self.angle)) * self.speed

    def update(self, player) -> None:
        # движение пули
        self.rect.x += self.dx
        self.rect.y += self.dy

        for monster in monsters_group:
            if monster.hitbox.colliderect(self.rect):
                monster.hp -= self.damage
                player.all_damage += self.damage

                DamageView(self.damage, *self.rect.center)
                self.kill()

        self.check()

    def check(self) -> None:
        if pygame.sprite.spritecollideany(self, indestructible_block_type):
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        # отрисовка пули
        screen.blit(self.image, self.rect.center)


class EnergyBullet(Bullet):
    image = load_image(os.path.join("GAME", "ENTITY", "energy_bullet.png")).convert_alpha()
    damage = 15

    def __init__(self, x: int, y: int, angle: float, damage: int = 20):
        super().__init__(x, y, angle, damage=damage)

        self.lives = 10

    def check(self) -> None:
        if pygame.sprite.spritecollideany(self, indestructible_block_type):
            if self.lives:
                self.image = pygame.transform.rotate(self.image, 90).convert_alpha()

                self.angle -= 90
                self.dx = math.cos(math.radians(self.angle)) * self.speed
                self.dy = math.sin(math.radians(self.angle)) * self.speed

                self.lives -= 1
            else:
                self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, camera, speed: float = 5.) -> None:
        super().__init__(all_sprites)
        
        self.image = load_image(os.path.join("GAME", "Cammando", "untitled.png"))
        self.camera = camera

        self.max_greade = self.grenade = 1

        self.max_sprint = self.sprint = 1
        self.sprint_angle = 0
        self.sprint_reload_cooldown = 0
        self.max_sprint_value = self.sprint_value = 80
        self.sprint_angle = None

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
        self.hitbox_size = 16
        self.hitbox = pygame.Rect(self.rect.centerx - self.hitbox_size // 2,
                                  self.rect.centery - self.hitbox_size // 2,
                                  self.hitbox_size, self.hitbox_size)
        self.money = 50  # Начальное количество денег

        self.max_items = 300
        self.items = {}
        self.active_slot = 0

        self.image_rotated = self.image

        self.max_hp = self.hp = 2000

        self.doors = False

        # статистика
        self.all_money = self.money
        self.all_damage = 0

        # В классе Player
        self.info_image = None
        self.info_display_time = 0


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
            self.rect.x += math.sin(
                math.radians(self.sprint_angle if self.sprint_angle is not None else self.angle)
                ) * self.sprint_value
            self.rect.y -= math.cos(
                math.radians(self.sprint_angle if self.sprint_angle is not None else self.angle)
                ) * self.sprint_value
            self.sprint_value -= 10

            if self.sprint:
                self.sprint -= 1
                self.sprint_angle = self.angle
                self.camera.shake(5, 10)
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

        # Проверка столкновений с стенами
        self.hitbox.center = self.rect.center  # Обновляем хитбокс

        if self.doors:
            for sprite in doors_group:
                if self.hitbox.colliderect(sprite.rect):
                    self.rect = original_rect
        for sprite in impassable_block_type:
        # and (doors_group if False else none_group):
            if self.hitbox.colliderect(sprite.rect):
                self.rect = original_rect

        buttons = pygame.mouse.get_pressed()
        # обычные патроны
        if buttons[0]:
            # if self.bullets:
            #    self.camera.shake(1, 1)
            if not self.bullets_shooting:
                self.bullets_shooting = True
                self.bullets_shooting_cooldown = 0

        if self.bullets_shooting_cooldown > 150:
            self.bullets_shooting_cooldown = 0

        if self.bullets_shooting and self.bullets_shooting_cooldown == 0:
            self.bullets_reload_cooldown = 500
            if self.bullets > 0:
                Bullet(*get_gun_coord(self.rect.center, self.angle, self.hand), self.angle)
                self.bullets -= 1
                music.shot_fx.play()
                self.hand = not self.hand

        if self.bullets_reload_cooldown <= 0 and self.bullets < self.max_bullets:
            self.bullets += 1
            self.bullets_reload_cooldown = 50

        # заряженные патроны
        if buttons[2]:
            # if self.energy_bullets:
            #     self.camera.shake(1, 1)
            if not self.e_bullets_shooting:
                self.e_bullets_shooting = True
                self.e_bullets_shooting_cooldown = 0

        if self.e_bullets_shooting_cooldown > 150:
            self.e_bullets_shooting_cooldown = 0

        if self.e_bullets_shooting and self.e_bullets_shooting_cooldown == 0:
            self.e_bullets_reload_cooldown = 1000
            if self.energy_bullets > 0:
                EnergyBullet(*get_gun_coord(self.rect.center, self.angle, self.hand), self.angle)
                self.energy_bullets -= 1
                music.e_shot_fx.play()
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
        if self.info_display_time > 0:
            self.info_display_time -= clock.get_time()

    def get_distance(self, object: pygame.sprite.Sprite) -> float:
        return math.sqrt(
            (self.rect.centerx - object.rect.centerx) ** 2 + (self.rect.centery - object.rect.centery) ** 2)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_rotated, self.rect.topleft)

        # Отображение информации о предмете
        if self.info_image and self.info_display_time > 0:
            screen.blit(self.info_image, (WIDTH//3.5, HEIGHT//1.4))  # Отображаем над игроком

    def show_item_info(self, item: items.Item):
        # Отображение информации о предмете
        self.info_image = item.image_info  # Сохраняем изображение информации
        self.info_display_time = 3000  # Время отображения в миллисекундах

    def add_item(self, item: items.Item, count: int = 1) -> None:
        if len(self.items) < self.max_items:
            self.items.setdefault(item, 0)
            self.items[item] += count
            self.show_item_info(item)  # Отображение информации о предмете

    def push(self, value: int | float) -> None:
        self.rect.x += math.sin(math.radians(self.angle)) * value
        self.rect.y -= math.cos(math.radians(self.angle)) * value


class DamageView(pygame.sprite.Sprite):
    font = pygame.font.SysFont(None, 20)

    def __init__(self, damage: int, x: int, y: int):
        super().__init__(all_sprites, damage_text_group)

        self.damage = damage

        self.text = self.font.render(f'-{self.damage}', True, '#FF0000')
        self.rect = self.text.get_rect(center=(x, y))

        self.focus = 150
    
    def update(self) -> None:
        self.text.set_alpha(self.focus)
        self.rect.y -= 1

        self.focus -= 1
        if self.focus == 0:
            self.kill()
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.text, self.rect)


class Camera:
    def __init__(self):
        self.dx, self.dy = 0, 0

        self.shake_intensity = 0.
        self.shake_time = 0

    def update(self, target):
        if self.shake_time > 0:
            self.dx += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.dy += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_time -= 1

        dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2) * .12
        dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2) * .12
        if abs(dx - self.dx) > 1 or abs(dy - self.dy) > 1:
            self.dx += (dx - self.dx) * .12
            self.dy += (dy - self.dy) * .12

        self.dx = round(self.dx)
        self.dy = round(self.dy)

    def apply(self, sprite):
        sprite.rect.x += self.dx
        sprite.rect.y += self.dy

    def shake(self, intensity: int, time: int):
        self.shake_intensity = intensity
        self.shake_time = time


class Interface:
    hp_bar_background = Color(92, 172, 64)
    hp_bar_background_none = Color(34, 56, 19)
    hp_bar_text_color = Color(242, 249, 216)

    m1_skill = load_image(os.path.join("GAME", "gui", "skills", "m1.png")).convert_alpha()
    off_m1_skill = m1_skill.copy()
    off_m1_skill.set_alpha(50)
    off_m1_skill.convert_alpha()
    #
    m2_skill = load_image(os.path.join("GAME", "gui", "skills", "m2.png")).convert_alpha()
    off_m2_skill = m2_skill.copy()
    off_m2_skill.set_alpha(50)
    off_m2_skill.convert_alpha()
    #
    shift_skill = load_image(os.path.join("GAME", "gui", "skills", "shift.png")).convert_alpha()
    off_shift_skill = shift_skill.copy()
    off_shift_skill.set_alpha(50)
    off_shift_skill.convert_alpha()
    #
    r_skill = load_image(os.path.join("GAME", "gui", "skills", "r.png")).convert_alpha()
    off_r_skill = r_skill.copy()
    off_r_skill.set_alpha(50)
    off_r_skill.convert_alpha()

    def __init__(self) -> None:
        self.item_info_image = None
        self.item_info_display_time = 0
        self.item_info_position = (0, 0)

    def draw(self, screen: pygame.surface.Surface, player: Player) -> None:
        # border
        pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, WIDTH, 85))
        pygame.draw.rect(screen, BACKGROUND_COLOR, (0, HEIGHT - 100, WIDTH, 100))

        self.draw_graph(screen, self.hp_bar_background_none, self.hp_bar_background, self.hp_bar_text_color,
                        50, HEIGHT - 65, 254, 30, player.hp / player.max_hp, f"{player.hp} / {player.max_hp}")

        items = (
            (player.bullets, player.max_bullets, 'M1', self.m1_skill, self.off_m1_skill),
            (player.energy_bullets, player.max_energy_bullets, 'M2', self.m2_skill, self.off_m2_skill),
            (player.sprint, player.max_sprint, 'SHIFT', self.shift_skill, self.off_shift_skill),
            (player.grenade, player.max_greade, 'R', self.r_skill, self.off_r_skill)
        )

        self.draw_skills(screen, WIDTH - 100, HEIGHT - 90, items)

        inv = list(sorted(player.items.items(), key=lambda a: a[0].name))
        inv += [None] * (9 - len(inv))
        self.draw_inv(screen, 240, 10, inv)

        font = pygame.font.SysFont(None, 35)
        text = font.render(f'${player.money}', True, '#FFFF00')
        screen.blit(text, (10, 10))

        if self.item_info_image:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            scaled_image = pygame.transform.scale(self.item_info_image, (self.item_info_image.get_width() // 1.5,
                                                                         self.item_info_image.get_height() // 1.5))
            screen.blit(scaled_image, (mouse_x + 10, mouse_y + 10))

    def show_item_info(self, item: items.Item):
        self.item_info_image = item.image_info  # Сохраняем изображение информации
        self.item_info_display_time = 3000  # Время отображения в миллисекундах

    def hide_item_info(self):
        self.item_info_image = None

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
                    items: tuple[tuple[int, int, str, pygame.Surface]]) -> None:
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
                 items: tuple[tuple[items.Item, int]]) -> None:
        # Сбрасываем информацию о предмете перед отрисовкой инвентаря
        self.hide_item_info()

        for i, data in enumerate(items):
            place = pygame.draw.rect(screen, "#404974", (x + i * 60, y, 60, 60))

            if not data:
                continue

            item, count = data
            screen.blit(item.image_item, place.topleft)
            font = pygame.font.SysFont(None, 30)
            text = font.render(f"x{count}", True, "#FFFFFF")
            screen.blit(text, (place.bottomright[0] - text.get_size()[0], place.bottomright[1] - text.get_size()[1]))

            # Проверка наведения курсора на иконку
            if place.collidepoint(pygame.mouse.get_pos()):
                self.show_item_info(item)  # Отображаем информацию о предмете


class Chest(pygame.sprite.Sprite):
    chance_item = (
        (0, 80),
        (1, 19),
        (3, 1)
    )

    def __init__(self, x: int, y: int, price: int = 25) -> None:
        self.image = load_image(os.path.join("GAME", "chests", "normal", "chest.png")).convert_alpha()
        self.image_opened = load_image(os.path.join("GAME", "chests", "normal", "chest_.png")).convert_alpha()

        self.animation_frames = [load_image(os.path.join("GAME", "chests", "normal", f"chest{i}.png")).convert_alpha()
                                 for i in range(1, 6)]
        
        super().__init__(all_sprites)
    
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
    chance_item = (
        (2, 100),
    )

    def __init__(self, x: int, y: int, price: int = 75) -> None:
        self.image = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest.png")).convert_alpha()
        self.image_opened = load_image(os.path.join("GAME", "chests", "corrupted chest", "chest_.png")).convert_alpha()

        self.animation_frames = [load_image(os.path.join("GAME", "chests", "corrupted chest", f"chest{i}.png")).convert_alpha()
                                 for i in range(1, 6)]
    
        super().__init__(x, y, price)


def get_gun_coord(coords: tuple[int, int], angle: float, hand: bool) -> tuple[int, int]:
    """ определение координат оружий относительно игрока """

    f = 60.72890558  # длинна гипотенузы
    angle -= 90
    angle = math.radians(angle + 17.24 * (1 if hand else -1))

    x = coords[0] + math.cos(angle) * f
    y = coords[1] + math.sin(angle) * f

    return x, y


def main_game(dr: int = 0, dg: int = 0, db: int = 0,
              player_items = {}, player_money: int = 50,
              player_hp: int = 100, player_max_hp: int = 100,
              player_all_money: int = 50, player_all_damage: int = 0) -> None:
    convert_path_to_img((dr, dg, db))

    interface = Interface()
    camera = Camera()

    chests = []
    doors = []

    opened_rooms = set()
    opened_rooms.add((0, 0))

    def next_level(*_) -> None:
        global portal, player, camera, interface
        for sprite in all_sprites:
            sprite.kill()
        for sprite in doors:
            sprite.kill()
        for sprite in chests:
            sprite.kill()

        data = (player.items, player.money, player.hp, player.max_hp,
                player.all_money, player.all_damage)

        portal = None
        player = None
        interface = None
        camera = None

        screen.fill(BACKGROUND_COLOR)
        pygame.display.flip()
        clock.tick(FPS)

        r = random.randint(-50, 50)
        g = random.randint(-50, 50)
        b = random.randint(-50, 50)

        main_game(r, g, b, *data)
        return

    def spawn_boss(x: int, y: int) -> None:
        player.doors = True
        monsters.SpawnMonster(x, y, monsters.Quen, (boss_room, ))

    def draw_any(surface, _x: int, _y: int) -> None:
        global player, portal

        for y, row in enumerate(surface):
            for x, col in enumerate(row):
                coords = 80 * x + _x, 80 * y + _y

                if col == '.':
                    blocks.Grass(*coords)
                if col == '#':
                    blocks.Wall(*coords)
                if col == '@':
                    blocks.Grass(*coords)
                    player = Player(coords[0] + 60, coords[1] + 60, camera)
                    player.hp = player_hp
                    player.max_hp = player_max_hp
                    player.items = player_items
                    player.money = player_money
                    player.all_money = player_all_money
                    player.all_damage = player_all_damage

                if col == 'c':
                    blocks.Grass(*coords)
                    chests.append(Chest(coords[0] + 60, coords[1] + 40))
                if col == 'C':
                    blocks.Grass(*coords)
                    chests.append(CorruptedChest(coords[0] + 60, coords[1] + 40))
                
                if col == 'Q':
                    monsters.Quen(*coords)
                
                if col == 'D':
                    blocks.Grass(*coords)
                    doors.append(blocks.Door(*coords))
                if col == 'd':
                    blocks.Grass(*coords)
                    doors.append(blocks.Door(*coords, True))
                
                if col == 'p':
                    blocks.Grass(*coords)
                    portal = blocks.Portal(coords[0] + 40, coords[1] + 40, spawn_boss)

    def draw_hallway(x: int, y: int, rotate: bool = False) -> None:
        surface = ['#...#',
                   '#...#',
                   '#...#',
                   '#...#',
                   '#...#']
        
        if rotate:
            surface = [''.join(a) for a in zip(*surface)]
        
        draw_any(surface, x, y)

    def draw_map(room: game_map.Room, x_room = 0, y_room = 0):
        global boss_room

        draw_any(room.surface, x_room * 18 * 80, y_room * 18 * 80)

        pos = []
        if room.type == game_map.NORMAL_ROOM:
            pos.append(room.get_random_pos(3))
            pos.append(room.get_random_pos(1))
        f = game_map.RoomData(room.type, x_room * 18 * 80 + 160, y_room * 18 * 80 + 160, x_room, y_room, *pos)
        if room.type == game_map.BOSS_ROOM:
            boss_room = f

        for i, neighbor in enumerate(room.passages):
            if neighbor and type(neighbor) is not bool:
                new_x, new_y = x_room, y_room
                if i == 0:
                    new_y -= 1
                if i == 1:
                    new_x -= 1
                if i == 2:
                    new_y += 1
                if i == 3:
                    new_x += 1
                draw_map(neighbor, new_x, new_y)
            if type(neighbor) is bool:
                x_h, y_h = x_room * 18 * 80, y_room * 18 * 80
                if i == 0:
                    draw_hallway(x_h + 80 * 4, y_h - 5 * 80)
                elif i == 1:
                    draw_hallway(x_h - 5 * 80, y_h + 80 * 4, True)
                elif i == 2:
                    draw_hallway(x_h + 80 * 4, y_h + 80 * 13)
                elif i == 3:
                    draw_hallway(x_h + 80 * 13, y_h + 80 * 4, True)
    
    draw_map(game_map.make_map(2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_pos = pygame.mouse.get_pos()

        screen.fill(BACKGROUND_COLOR)

        # Отрисовка объектов на экране
        block_group.draw(screen)
        for door in doors:
            door.draw(screen, player.doors)
        for chest in chests:
            chest.draw(screen, player)
        portal.draw(screen)
        mosters_spawns_group.draw(screen)
        monsters_group.draw(screen)
        monsters_bullets_group.draw(screen)

        # Рисуем игрока
        player.draw(screen)  # Здесь вызывается метод draw игрока

        bullets_group.draw(screen)
        damage_text_group.draw(screen)

        interface.draw(screen, player)

        # Обновление состояния объектов
        block_group.update()
        bullets_group.update(player)
        mosters_spawns_group.update()
        monsters_bullets_group.update(player)
        portal.update(player)
        player.update(mouse_pos)  # Обновляем состояние игрока
        camera.update(player)

        # Обновляем другие группы объектов
        game_map.room_group.update(player)
        damage_text_group.update()

        for chest in chests:
            chest.update(player)
        monsters_group.update(player)

        # Применяем камеру ко всем объектам
        for sprite in block_group:
            camera.apply(sprite)
        for sprite in damage_text_group:
            camera.apply(sprite)
        for sprite in game_map.room_group:
            camera.apply(sprite)
        for sprite in monsters_group:
            camera.apply(sprite)
        for sprite in monsters_bullets_group:
            camera.apply(sprite)
        for sprite in mosters_spawns_group:
            camera.apply(sprite)
        for sprite in chests:
            camera.apply(sprite)
        for sprite in doors:
            camera.apply(sprite)
        camera.apply(player)
        camera.apply(portal)

        pygame.display.flip()

        if (obj := pygame.sprite.spritecollideany(player, game_map.room_group)):
            if obj.type == game_map.NORMAL_ROOM:
                if (obj.x, obj.y) not in opened_rooms:
                    if not obj.trial:
                        player.doors = True
                        obj.trial = True

                        player.push(50)
                        for x, y in obj.monsters_pos:
                            monsters.SpawnMonster(obj.rect.topleft[0] + x * 80 - 40,
                                                  obj.rect.topleft[1] + y * 80 - 40,

                                                  monsters.Lem, (obj, ))
                    if obj.monsters_count == 0:
                        player.doors = False
                        opened_rooms.add((obj.x, obj.y))
                        for x, y in obj.chests_pos:
                            chests.append(Chest(obj.rect.topleft[0] + x * 80 + 60, obj.rect.topleft[1] + y * 80  + 40))
            else:
                if obj.monsters_count == -1:
                    portal.reset(next_level)
        
        if player.hp <= 0:
            add_death(player.all_money, player.all_damage)
            main_death(
                {'Урона нанесено': str(player.all_damage),
                 'Собрано монет': str(player.all_money)}
            )

        clock.tick(FPS)

    pygame.quit()
