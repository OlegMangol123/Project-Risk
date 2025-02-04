import math
import random

import pygame

from components.groups import *
from components.other import *


class Lem(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, room_data) -> None:
        super().__init__(all_sprites, monsters_group)

        self.idle_image = images['enemy.lem']
        self.attack_anim1 = images['enemy.lem.at1']
        self.attack_anim2 = images['enemy.lem.at2']

        self.all_attacks = ((self.attack_anim1, 15), (self.attack_anim2, 10))

        self.image = self.this_image = self.idle_image
        self.angle = 0

        self.hp = 60

        self.room_data = room_data

        self.rect = self.image.get_rect(center=(x, y))

        self.speed = 2
        self.hitbox_size = 80
        self.hitbox = pygame.Rect(0, 0, self.hitbox_size, self.hitbox_size)
        self.hitbox.center = self.rect.center

        self.freeze = False
        self.freeze_cooldown = 0

        self.attack_frame = 0
        self.attacked = False
        self.attack_id = 0

    def update(self, player) -> None:
        if self.hp <= 0:
            self.kill()
            money = random.randint(0, 5)
            player.money += money
            player.all_money += money

            self.room_data.killed_monster()

        self.hitbox.center = self.rect.center

        if not self.freeze:
            rel_x = player.rect.centerx - self.rect.centerx
            rel_y = player.rect.centery - self.rect.centery
            self.angle = math.degrees(math.atan2(rel_x, rel_y))

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

            if player.get_distance(self) <= 125:
                self.freeze = True
                self.attacked = False
                self.attack_frame = 0
                self.attack_id = random.randrange(0, len(self.all_attacks))
                self.freeze_cooldown = 75

        else:
            self.this_image = self.all_attacks[self.attack_id][0][self.attack_frame]
            if self.attack_frame + \
                    1 < len(self.all_attacks[self.attack_id][0]):
                self.attack_frame += 1
            else:
                if not self.attacked:
                    self.attack(player)
                    self.attacked = True
                self.freeze_cooldown -= 1
                if self.freeze_cooldown <= 0:
                    self.freeze = False

        self.image = pygame.transform.rotate(self.this_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def attack(self, player) -> None:
        # координаты центра окружности
        dx = self.rect.centerx + math.sin(math.radians(self.angle)) * 100
        dy = self.rect.centery + math.cos(math.radians(self.angle)) * 100

        dist = math.sqrt(
            (dx - player.rect.centerx) ** 2 +
            (dy - player.rect.centery) ** 2)

        if dist <= 50:
            player.hp -= self.all_attacks[self.attack_id][1]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.center)


class Quen(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, room_data) -> None:
        super().__init__(all_sprites, monsters_group)

        self.idle_image = images['enemy.quen']
        self.attack_anim = images['enemy.quen.at']

        self.image = self.this_image = self.idle_image
        self.angle = 0
        self.room_data = room_data

        self.hp = 1200

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.hitbox_size = 200
        self.hitbox = pygame.Rect(0, 0, self.hitbox_size, self.hitbox_size)
        self.hitbox.center = self.rect.center

        self.freeze = False

        self.attack_frame = 0
        self.attacked = False
        self.attack_cooldown = 300
        self.shooting_cooldown = 0
        self.attack_count = 0

    def update(self, player) -> None:
        if self.hp <= 0:
            self.kill()
            self.room_data.killed_monster()

        self.hitbox.center = self.rect.center

        rel_x = player.rect.centerx - self.rect.centerx
        rel_y = player.rect.centery - self.rect.centery
        self.angle = math.degrees(math.atan2(rel_x, rel_y))

        self.image = pygame.transform.rotate(self.this_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.attack_cooldown <= 0:
            if self.attack_frame + 1 < len(self.attack_anim):
                self.this_image = self.attack_anim[self.attack_frame]
                self.attack_frame += 1
            else:
                self.attack_frame = 0
                QuenAttack(*self.rect.center, self.angle)
                self.attack_cooldown = 20
                self.attack_count += 1

                if self.attack_count == 3:
                    self.attack_count = 0
                    self.attack_cooldown = 200
                    self.this_image = self.idle_image

        self.attack_cooldown -= 1

    def attack(self, player) -> None:
        # координаты центра окружности
        dx = self.rect.centerx + math.sin(math.radians(self.angle)) * 100
        dy = self.rect.centery + math.cos(math.radians(self.angle)) * 100

        dist = math.sqrt(
            (dx - player.rect.centerx) ** 2 +
            (dy - player.rect.centery) ** 2)

        if dist <= 50:
            player.hp -= self.all_attacks[self.attack_id][1]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.center)


class QuenAttack(pygame.sprite.Sprite):
    def __init__(
            self,
            x: int,
            y: int,
            angle: float,
            speed: float = 12) -> None:
        super().__init__(all_sprites, monsters_bullets_group)

        self.speed = speed
        self.angle = angle - 90

        self.flying_image = images['entity.quen.harch']
        self.ground_image = images['entity.quen.harch1']

        self.image = self.flying_image
        self.image = pygame.transform.rotate(self.image, self.angle + 90)

        self.rect = self.image.get_rect(center=(x, y))

        self.on_ground = False
        self.damage_cooldown = 0
        self.lives = 5

        self.dx = math.cos(math.radians(-self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed

    def update(self, player) -> None:
        if not self.on_ground:
            self.rect.x += self.dx
            self.rect.y += self.dy

            if pygame.sprite.spritecollideany(self, indestructible_block_type):
                self.image = self.ground_image
                self.on_ground = True
            if player.hitbox.colliderect(self.rect):
                self.image = self.ground_image
                self.on_ground = True
        else:
            if self.damage_cooldown <= 0:
                if player.hitbox.colliderect(self.rect):
                    player.hp -= 25

                self.damage_cooldown = 200
                self.lives -= 1

                if self.lives == 0:
                    self.kill()
            else:
                self.damage_cooldown -= 1

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.center)


class SpawnMonster(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, monster, monster_data) -> None:
        super().__init__(all_sprites, mosters_spawns_group)

        self.anim = images['monster_spawn']
        self.frame = 0
        self.image = self.anim[self.frame]
        self.start = 60
        self.rect = self.image.get_rect(center=(x, y))

        self.monser, self.monser_data = monster, monster_data

    def update(self) -> None:
        if self.start <= 0:
            if self.frame + 1 < len(self.anim):
                self.frame += 1
                self.image = self.anim[self.frame]
            else:
                self.monser(*self.rect.center, *self.monser_data)
                self.kill()
        else:
            self.start -= 1

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
