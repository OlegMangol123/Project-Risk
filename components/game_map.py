import random


class Room:
    # [top, left, bott, right]
    def __init__(self, passages: list) -> None:
        self.passages = passages

        self.surface = [
            '             ',
            ' ########### ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' ########### ',
            '             ',
        ]

    def format(self) -> None:
        if self.passages[0] is not None:
            self.surface[0] = '    #...#    '
            self.surface[1] = ' ####...#### '
        
        if self.passages[2] is not None:
            self.surface[-1] = '    #...#    '
            self.surface[-2] = ' ####...#### '
        
        if self.passages[1] is not None:
            self.surface[4] = '#' + self.surface[4][1:]
            for i in range(5, 8):
                self.surface[i] = '..' + self.surface[i][2:]
            self.surface[8] = '#' + self.surface[4][1:]
        
        if self.passages[3] is not None:
            self.surface[4] = self.surface[4][:-1] + '#'
            for i in range(5, 8):
                self.surface[i] = self.surface[i][:-2] + '..'
            self.surface[8] = self.surface[4][:-1] + '#'



class Room2(Room):
    # [top, left, bott, right]
    def __init__(self, passages: list) -> None:
        super().__init__(passages)
    
        self.surface = [
            '             ',
            ' ########### ',
            ' #.........# ',
            ' #.##......# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #......##.# ',
            ' #.........# ',
            ' ########### ',
            '             ',
        ]



class Start(Room):
    def __init__(self, passages: list) -> None:
        super().__init__(passages)

        self.surface = [
            '             ',
            ' ########### ',
            ' ##.......## ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #....@....# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' ##.......## ',
            ' ########### ',
            '             ',
        ]


class Boss(Room):
    def __init__(self, passages: list) -> None:
        super().__init__(passages)

        self.surface = [
            '             ',
            ' ########### ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #....B....# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' #.........# ',
            ' ########### ',
            '             ',
        ]


rooms = [Room, Room2]


def make_map(rooms_count: int, x: int = 0, y: int = 0, last: int | None = None,
             room: Room = Start([None] * 4), boss_side: bool = True, generated_rooms: set = set()) -> Room:
    rooms_count -= 1
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
                room.passages[i] = make_map(room_n, x=new_x, y=new_y, last=i, room=new_room, generated_rooms=generated_rooms)

    if last is not None:
        room.passages[last - 2] = True
    room.format()
    return room