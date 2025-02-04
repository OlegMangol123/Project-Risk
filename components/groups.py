import pygame


class TextGroup(pygame.sprite.Group):
    def draw(self, screen: pygame.Surface):
        for sprite in self.sprites():
            sprite.draw(screen)


all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()
mosters_spawns_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
none_group = pygame.sprite.Group()
block_group = pygame.sprite.Group()
damage_text_group = TextGroup()

monsters_bullets_group = pygame.sprite.Group()

indestructible_block_type = pygame.sprite.Group()
destructible_block_type = pygame.sprite.Group()
impassable_block_type = pygame.sprite.Group()
