import random

import pygame

from components.groups import all_sprites
#

room_group = pygame.sprite.Group()


NORMAL_ROOM = 0
BOSS_ROOM = 1



class RoomData(pygame.sprite.Sprite):
    def __init__(self, type, x_sceen: int, y_screen: int, x:int, y: int,
                 monsters_pos: list = [], chests_pos: list = []) -> None:
        super().__init__(all_sprites, room_group)

        self.image = pygame.Surface((9 * 80, 9 * 80)).convert()
        self.rect = self.image.get_rect(topleft=(x_sceen, y_screen))

        self.x, self.y = x, y

        self.trial = False
        self.monsters_pos = monsters_pos
        self.chests_pos = chests_pos

        self.type = type

        self.monsters_count = len(self.monsters_pos)
    
    def killed_monster(self) -> None:
        self.monsters_count -= 1


class Room:
    # [top, left, bott, right]
    def __init__(self, passages: list) -> None:
        self.passages = passages

        self.surface = [
            '#############',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#############',
        ]

        self.type = NORMAL_ROOM

    def format(self) -> None:
        if self.passages[0] is not None:
            self.surface[0] = '#####ddd#####'
        
        if self.passages[2] is not None:
            self.surface[-1] = '#####ddd#####'
        
        if self.passages[1] is not None:
            for i in range(5, 8):
                self.surface[i] ='D' + self.surface[i][1:]
        
        if self.passages[3] is not None:
            for i in range(5, 8):
                self.surface[i] = self.surface[i][:-1] + 'D'
    
    def get_random_pos(self, count: int) -> list[int]:
        f = []
        for x, row in enumerate(self.surface[3:-3]):
            for y, col in enumerate(row[3:-3]):
                if col == '.':
                    f.append((x + 2, y + 2))

        return random.sample(f, count)


class Room2(Room):
    # [top, left, bott, right]
    def __init__(self, passages: list) -> None:
        super().__init__(passages)
    
        self.surface = [
            '#############',
            '#...........#',
            '#...........#',
            '#..##.......#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#.......##..#',
            '#...........#',
            '#...........#',
            '#############',
        ]

        self.type = NORMAL_ROOM



class Start(Room):
    def __init__(self, passages: list) -> None:
        super().__init__(passages)

        self.surface = [
            '#############',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#.....@.....#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#############',
        ]


class Boss(Room):
    def __init__(self, passages: list) -> None:
        super().__init__(passages)

        self.surface = [
            '#############',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#.....p.....#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#...........#',
            '#############',
        ]

        self.type = BOSS_ROOM


rooms = [Room, Room2]
    

def make_map(rooms_count: int):
    first_map = _map = recurs_map(rooms_count)
    f = list(filter(lambda a: a and type(a) is not bool, _map.passages))
    while f:
        _map = random.choice(f)
        f = list(filter(lambda a: a and type(a) is not bool, _map.passages))
    _map.surface = Boss(_map.passages).surface
    _map.type = BOSS_ROOM
    _map.format()
    return first_map



def recurs_map(rooms_count: int, x: int = 0, y: int = 0, last: int | None = None,
               room: Room = Start([None] * 4), generated_rooms: set = set()) -> Room:
    generated_rooms.add((x, y))

    if rooms_count <= 0:
        room.passages[last - 2] = True
        room.format()
        return room

    neighbors = [None] * 4
    while len(tuple(filter(lambda a: a, neighbors))) < 3:
        neighbors = random.choices((True, None), k=4)

    room_n = rooms_count - 1

    for i, neighbor in enumerate(neighbors):
        if neighbor:
            new_room = random.choice(rooms)([None] * 4)

            new_x, new_y = x, y 
            if i == 0:
                new_x -= 1
            if i == 1:
                new_y -= 1
            if i == 2:
                new_x += 1
            if i == 3:
                new_y += 1

            if (new_x, new_y) not in generated_rooms:
                room.passages[i] = recurs_map(room_n, x=new_x, y=new_y, last=i,
                                            room=new_room, generated_rooms=generated_rooms)                        

    if last is not None:
        room.passages[last - 2] = True
    room.format()
    return room