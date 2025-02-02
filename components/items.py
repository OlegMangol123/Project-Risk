import os
import random

import pygame

from components.other import load_image


def item(data: str) -> pygame.Surface:
    return pygame.transform.scale(load_image(os.path.join("GAME", "items", data, "item.png")), (60, 60))


def info(data: str) -> pygame.Surface:
    return load_image(os.path.join("GAME", "items", data, "info.png"))


class Item:
    image_item: pygame.Surface
    image_info: pygame.Surface

    name: str
    rare: int

    def __init__(self) -> None:
        ...


class Bungus(Item):
    image_item = item('bungus')
    image_info = info('bungus')

    name = 'Буйногриб'
    rare = 0

    def __init__(self) -> None:
        ...


class Crowbar(Item):
    image_item = item('crowbar')
    image_info = info('crowbar')

    name = 'Лом'
    rare = 0

    def __init__(self) -> None:
        ...


class Dio(Item):
    image_item = item('dio')
    image_info = info('dio')

    name = 'Дио'
    rare = 3

    def __init__(self) -> None:
        ...


class Glass(Item):
    image_item = item('glass')
    image_info = info('glass')

    name = 'Формованное стекло'
    rare = 2

    def __init__(self) -> None:
        ...


class Goat(Item):
    image_item = item('goat')
    image_info = info('goat')

    name = 'Козлиное копыто'
    rare = 0

    def __init__(self) -> None:
        ...


class Root(Item):
    image_item = item('root')
    image_info = info('root')

    name = 'Странный корень'
    rare = 1

    def __init__(self) -> None:
        ...


class Seed(Item):
    image_item = item('seed')
    image_info = info('seed')

    name = 'Семена пиявки'
    rare = 1

    def __init__(self) -> None:
        ...


class Steak(Item):
    image_item = item('steak')
    image_info = info('steak')

    name = 'Стейк из бизона'
    rare = 0

    def __init__(self) -> None:
        ...


class Syringe(Item):
    image_item = item('syringe')
    image_info = info('syringe')

    name = 'Шприц солдата'
    rare = 0

    def __init__(self) -> None:
        ...


ALL_ITEMS = Item.__subclasses__()


def get_random(rare: int) -> Item:
    return random.choice(tuple(filter(lambda a: a.rare == rare, ALL_ITEMS)))