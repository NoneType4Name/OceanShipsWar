import threading
import time

import pygame

from functions import *
from Gui import *


class Blocks(DATA):
    def __init__(self, w_h: int, left_margin, upper_margin, block_size):
        blocks = {}
        for num_let in range(w_h):
            blocks[num_let] = []
            for num in range(w_h):
                blocks[num_let].append(
                    pygame.Rect(left_margin + num_let * block_size, upper_margin + num * block_size, block_size,
                                block_size))
        self.blocks = blocks
        self.block_size = block_size
        super().__init__(self.blocks)

    def GetRect(self, cords: tuple) -> pygame.Rect:
        if cords:
            return pygame.Rect(self.blocks[cords[0]][cords[1]])
        else:
            return False

    def GetShip(self, cords: tuple) -> pygame.Rect:
        """
        Get ship rectangle from frozen coordinates
        Return ship window rectangle
        cords     :    tuple of frozen ship coordinates:   tuple
        return    ->   real ship coordinates
        """
        if cords:
            cords0 = self.GetRect(cords[0])
            cords1 = self.GetRect(cords[1])
            if cords0[1] == cords1[1]:
                return pygame.Rect(*cords0.topleft, cords1.x - cords0.x + self.block_size, self.block_size)
            else:
                return pygame.Rect(*cords0.topleft, self.block_size, cords1.y - cords0.y + self.block_size)

        else:
            log.critical(f'{cords}.')
            return False

    def GetShipEnv(self, cords: tuple) -> pygame.Rect:
        """
        GetShipEnv(cords)

        Get real ship rectangle
        Return ship environment rectangle within the block radius

        cords     :    tuple of real ship cords:   tuple
        return    ->   list of all ship blocks
        """
        if cords:
            return pygame.Rect(cords[0] - self.block_size, cords[1] - self.block_size,
                               cords[2] + self.block_size * 2, cords[3] + self.block_size * 2)
        else:
            log.critical(f'{cords}.')
            return False

    def GetShipBlocks(self, cords: tuple) -> list:
        """
        GetShipBlocks(cords)

        Get real ship coordinates
        Return all ship blocks

        cords     :    tuple of real ship cords:   tuple
        return    ->   list of all ship blocks
        """
        if cords:
            cord = []
            if cords[0][0] == cords[1][0]:
                for pos in range(cords[0][1], cords[1][1] + 1):
                    cord.append((cords[0][0], pos))
            else:
                for pos in range(cords[0][0], cords[1][0] + 1):
                    cord.append((pos, cords[0][1]))
            return cord
        else:
            log.critical(f'{cords}')
            return False

    def GetCollide(self):
        for letter in self.blocks:
            for num, block in enumerate(self.blocks[letter]):
                if block.collidepoint(pygame.mouse.get_pos()):
                    return letter, num


class Ships:
    def __init__(self, blocks:Blocks, ship_color, ships_width, solo_count=4, duo_count=3, trio_count=2, quadro_count=1):
        self.counts = {1: solo_count, 2: duo_count, 3: trio_count, 4: quadro_count}
        self.ships = dict.fromkeys([1,2,3,4], {})
        self.ships_count = dict.fromkeys([1,2,3,4], 0)
        self.blocks = blocks
        self.ship_color = ship_color
        self.ships_width = ships_width
        self.SumShipsMaxCount = sum(self.counts.values())
        self._selected = None

    def AddShip(self, type_ship, ship):
        if self.counts[type_ship]:
            ship_num = len(self.ships[type_ship]) + 1
            self.ships[type_ship][ship_num] = {}
            self.ships[type_ship][ship_num]['ship'] = ship
            self.ships[type_ship][ship_num]['blocks'] = self.blocks.GetShipBlocks(ship)
            self.ships_count[type_ship] += 1

    def draw(self, image):
        for _ in self.ships.values():
            for ship in _.values():
                pygame.draw.rect(image, self.ship_color, self.blocks.GetShip(ship['ship']), self.ships_width)

    def DrawShip(self, cords: tuple, image, custom_color=None):
        if custom_color:
            pygame.draw.rect(image, custom_color, self.blocks.GetShip(cords), self.ships_width)
        else:
            pygame.draw.rect(image, self.ship_color, self.blocks.GetShip(cords), self.ships_width)

    def DelShip(self, type_ship, number):
        del self.ships[type_ship][number]

    def HasShip(self, cords):
        return any(map(lambda cord: True if cord == cords else False, GetDeepData(self.ships)))

    def HasCollide(self, cords):
        for _ in self.ships:
            for ship_cords in self.ships[_].values():
                if self.blocks.GetShipEnv(self.blocks.GetShip(ship_cords['ship'])).colliderect(self.blocks.GetShip(cords)):
                    return True

    def CanBuild_DrawCursor(self, cords) -> tuple:
        if not cords:
            return False, False
        cords_rect = self.blocks.GetShip((cords, cords))
        return_data = [True, True]
        for _ in self.ships:
            for rc in self.ships[_].values():
                rect = self.blocks.GetShip(rc['ship'])
                if self.blocks.GetShipEnv(rect).colliderect(cords_rect):
                    return_data[0] = False
                    if rect.colliderect(cords_rect):
                        return_data[1] = False
                    return return_data
        return return_data

    def SumShipsCount(self):
        return sum(self.ships_count.values())

    def StartBuildShip(self, selected):
        self._selected = selected


sz = (920, 540)
bl = int(sz[0] // BLOCK_ATTITUDE)
# blocs = Blocks(10, (sz[0] * 0.5 - bl * 5), (sz[1] * 0.5 - bl * 5), bl)


# def Synchronize(self, *text):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((self.source_ip, self.source_port))
#     while True:
#         sock.sendto(' '.join(text).encode(), self.enemy_addr)
#         data, addr = sock.recvfrom(1024)
#         try:
#             if data.decode() == 'start':
#                 sock.sendto(' '.join(text).encode(), addr)
#                 self.enemy_addr = addr
#                 print(('enemy', addr))
#                 break
#         except UnicodeError:
#             pass
#     sock.close()


class Exemplar:
    def __init__(self):
        self.size = SIZE(sz)
        self.block_size = int(self.size.w // BLOCK_ATTITUDE)
        self.Colors = DATA({
        'KilledShip': (60, 60, 60),
        'Lines': (255, 255, 255),
        'Background': (24, 24, 24),
        'Label': ((41, 42, 43), (91, 92, 93), (232, 234, 236), (232, 234, 236), False, (91, 92, 93), (), False, (255, 255, 255), ()),
        'Button': ((41, 42, 43), (255, 255, 255), (232, 234, 236), (0, 0, 0), False, (91, 92, 93), (91, 92, 93), False, (91, 92, 93)),
        'ButtonRed': ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
        'ButtonActive': ((255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), False, (100, 0, 200), (), False, (91, 92, 93)),
        'Switch': ((64, 64, 64), (64, 64, 64), (0, 255, 0), (255, 255, 255)),
        'Slide': ((53, 86, 140, 100), (53, 86, 140, 100), (38, 80, 148), (138, 180, 248)),
        'List': ((29, 29, 31), (29, 29, 31), (232, 234, 236), (255, 255, 255), (41, 42, 45), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), ()),
        'Path': ((138, 180, 248), (53, 86, 140), (232, 234, 236)),
        'ProgressBar': ((255, 255, 255), (0, 255, 0)),
        'TextInput': ((24, 24, 24), (24, 24, 24), (155, 155, 155), (255, 255, 255), False, (100, 0, 255, 100), (), False, (100, 0, 255), ()),
        'Red': (255, 0, 0),
        'Green': (0, 255, 0),
        'Blue': (0, 0, 255),
        'White': (0, 0, 255),
        'Scene':{
            'Load':{
                'Label': ((0, 0, 0, 0), (0, 0, 0, 0), (0, 255, 0), (0, 255, 0)),
                'ProgressBar': ((24, 24, 24), (0, 255, 0))},
            'Main':{
                'Button':((0, 0, 0), (0, 0, 0), (255, 255, 255), (100, 0, 200), True, (24, 24, 24), (0, 0, 0), True, (24, 24, 24), (0, 0, 0)),
            }
        }
        })
        self.VERSION = '0'
        self.Language = DATA(replace_str_var(Language(DEFAULT_LANGUAGES, DEFAULT_LANGUAGE, False).__dict__, self))
        self.source_ip, self.source_port = '0.0.0.0', 9997
        self.external_ip = None
        self.external_port = None
        self.mouse_pos = (0, 0)
        self.mouse_right_press = False
        self.mouse_right_release = False
        self.mouse_left_press = False
        self.mouse_left_release = False
        self.mouse_middle_press = False
        self.mouse_middle_release = False
        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = []
        # self.enemy_addr = ('109.252.70.249', 1359)
        # GetIP(self)
        # Synchronize(self, 'start')

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.mouse_left_press = True
                    self.mouse_left_release = False
                elif event.button == pygame.BUTTON_RIGHT:
                    self.mouse_right_press = True
                    self.mouse_right_release = False
                elif event.button == pygame.BUTTON_MIDDLE:
                    self.mouse_middle_press = True
                    self.mouse_middle_release = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    self.mouse_left_press = False
                    self.mouse_left_release = True
                elif event.button == pygame.BUTTON_RIGHT:
                    self.mouse_right_press = False
                    self.mouse_right_release = True
                elif event.button == pygame.BUTTON_MIDDLE:
                    self.mouse_middle_press = False
                    self.mouse_middle_release = True
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel_x = event.x
                self.mouse_wheel_y = event.y

            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] or event.touch:
                    self.mouse_wheel_x = event.rel[0]
                    self.mouse_wheel_y = event.rel[1]


class PlayGame:
    def __init__(self, parent:Exemplar, enemy:(str, int), **kwargs):
        self.type = PLAY
        self.parent = parent
        if kwargs.get('demo'):
            self.host = ''
            self.port = 0
        else:
            self.host = enemy[0]
            self.port = enemy[1]
        self.size = self.parent.size
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.image.fill(self.parent.Colors.Background)
        self.Lines = None
        self.Blocks = Blocks(10, (self.parent.size.w * 0.5 - self.parent.block_size * 5), (self.parent.size.h * 0.5 - self.parent.block_size * 5), self.parent.block_size)
        self.Ships = Ships(self.Blocks, self.parent.Colors.Lines, self.Blocks.block_size//7)
        self.KilledShips = Ships(self.Blocks, self.parent.Colors.Lines, self.Blocks.block_size//7)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.parent.source_ip, self.parent.source_port))
        self.condition = GAME_CONDITION_WAIT
        self.selected = None
        self._in_build = False
        self._build = False
        self._start_build = None
        self._horizontal_build = False
        self._select_to_build = False
        self._mediocre_ship = None
        self._ship_direction = 0
        self._ship_len = 0

    def DrawLines(self):
        if not self.Lines:
            self.Lines = pygame.Surface(self.parent.size, pygame.SRCALPHA)
            left_margin, upper_margin = (self.parent.size.w * 0.5 - self.parent.block_size * 5), (self.parent.size.h * 0.5 - self.parent.block_size * 5)
            for it in range(11):
                pygame.draw.line(self.Lines, self.parent.Colors.Lines, (left_margin, upper_margin + it * self.parent.block_size),
                                 (left_margin + 10 * self.parent.block_size, upper_margin + it * self.parent.block_size), 1)
                pygame.draw.line(self.Lines, self.parent.Colors.Lines, (left_margin + it * self.parent.block_size, upper_margin),
                                 (left_margin + it * self.parent.block_size, upper_margin + 10 * self.parent.block_size), 1)
                if it < 10:
                    font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.parent.Language.Letters[0], pygame.Rect(0, 0, self.parent.block_size, self.parent.block_size)))
                    num = font.render(str(it + 1), True, self.parent.Colors.Lines)
                    letter = font.render(self.parent.Language.Letters[it], True, self.parent.Colors.Lines)
                    num_ver_width = num.get_width()
                    num_ver_height = num.get_height()
                    letters_hor_width = letter.get_width()
                    self.Lines.blit(num, (left_margin - (self.parent.block_size * 0.5 + num_ver_width * 0.5), upper_margin + it * self.parent.block_size + (self.parent.block_size * 0.5 - num_ver_height * 0.5)))
                    self.Lines.blit(letter, (left_margin + it * self.parent.block_size + (self.parent.block_size * 0.5 - letters_hor_width * 0.5), upper_margin - font.size(self.parent.Language.Letters[it])[1] * 1.2))
        self.image.blit(self.Lines, (0, 0))

    def GetData(self):
        pass

    def inBuild(self):
        CanBuild, DrawCursorRect = self.Ships.CanBuild_DrawCursor(self.selected)
        if self.Ships.SumShipsCount() == self.Ships.SumShipsMaxCount:
            self.condition += 1
        elif self.parent.mouse_left_press and self.selected and CanBuild:
            DrawCursorRect = False
            self._in_build = True
            if not self._build:
                self._start_build = self.selected
                self._horizontal_build = True
                self._build = True
                self._select_to_build = True
            else:
                if self._start_build == self.selected:
                    self._mediocre_ship = self._start_build, self.selected
                else:
                    if self._select_to_build:
                        if self.Blocks.GetRect(self._start_build).x < self.Blocks.GetRect(self.selected).x:
                            self._select_to_build = False
                            self._ship_direction = 0

                        elif self.Blocks.GetRect(self._start_build).x > self.Blocks.GetRect(self.selected).x:
                            self._select_to_build = False
                            self._ship_direction = 1

                        elif self.Blocks.GetRect(self._start_build).y < self.Blocks.GetRect(self.selected).y:
                            self._select_to_build = False
                            self._ship_direction = 2

                        elif self.Blocks.GetRect(self._start_build).y > self.Blocks.GetRect(self.selected).y:
                            self._select_to_build = False
                            self._ship_direction = 3
                    else:
                        if not self._ship_direction:
                            if self.Blocks.GetRect(self.selected).x - self.Blocks.GetRect(self._start_build).x > 0:
                                self._ship_len = self.selected[0] - self._start_build[0] + 1
                                self._mediocre_ship = (self._start_build, (self.selected[0], self._start_build[1]))
                                self._horizontal_build = True
                            else:
                                self._select_to_build = True

                        elif self._ship_direction == 1:
                            if self.Blocks.GetRect(self._start_build).x - self.Blocks.GetRect(self.selected).x > 0:
                                self._ship_len = self._start_build[0] - self.selected[0] + 1
                                self._mediocre_ship = ((self.selected[0], self._start_build[1]), self._start_build)
                                self._horizontal_build = True
                            else:
                                self._select_to_build = True

                        elif self._ship_direction == 2:
                            if self.Blocks.GetRect(self.selected).y - self.Blocks.GetRect(self._start_build).y > 0:
                                self._ship_len = self.selected[1] - self._start_build[1] + 1
                                self._mediocre_ship = (self._start_build, (self._start_build[0], self.selected[1]))
                                self._horizontal_build = False
                            else:
                                self._select_to_build = True

                        elif self._ship_direction == 3:
                            if self.Blocks.GetRect(self._start_build).y - self.Blocks.GetRect(self.selected).y > 0:
                                self._ship_len = self._start_build[1] - self.selected[1] + 1
                                self._mediocre_ship = ((self._start_build[0], self.selected[1]), self._start_build)
                                self._horizontal_build = False
                            else:
                                self._select_to_build = True
                if self._mediocre_ship:
                    pygame.draw.rect(self.image, self.Ships.ship_color, self.Blocks.GetShip(self._mediocre_ship), self.Ships.ships_width)

        else:
            if self._build and self._mediocre_ship:
                if self.Ships.HasCollide(self._mediocre_ship):
                    self._build = False
                    self._select_to_build = True
                    DrawCursorRect = True
                    self._start_build = None
                    self._ship_direction = 0
                    print('ne po pravilam.')
                    # self.parent.AddNotification('NE PO PRAVILAM!.')
                else:
                    if self._ship_len > 4:
                        print('Максимальная длина корабля 4 клетки!.')
                        self._mediocre_ship = None
                        self._build = False
                        self._select_to_build = True
                        DrawCursorRect = True
                        self._start_build = None
                        self._ship_direction = 0
                    elif self._ship_len == 4:
                        if self.Ships.ships_count[4] < self.Ships.counts[4]:
                            self.Ships.ships_count[4] += 1
                            self.Ships.AddShip(4, self._mediocre_ship)
                            self._in_build = True
                        else:
                            print('4-х палубные корабли закончились!.')
                            self._mediocre_ship = None
                            self._build = False
                            self._select_to_build = True
                            DrawCursorRect = True
                            self._start_build = None
                            self._ship_direction = 0
                    elif self._ship_len == 3:
                        if self.Ships.ships_count[3] < self.Ships.counts[3]:
                            self.Ships.ships_count[3] += 1
                            self.Ships.AddShip(3, self._mediocre_ship)
                            self._in_build = True
                        else:
                            print('3-х палубные корабли закончились!.')
                            self._mediocre_ship = None
                            self._build = False
                            self._select_to_build = True
                            DrawCursorRect = True
                            self._start_build = None
                            self._ship_direction = 0
                    elif self._ship_len == 2:
                        if self.Ships.ships_count[2] < self.Ships.counts[2]:
                            self.Ships.ships_count[2] += 1
                            self.Ships.AddShip(2, self._mediocre_ship)
                            self._in_build = True
                        else:
                            print('2-х палубные корабли закончились!.')
                            self._mediocre_ship = None
                            self._build = False
                            self._select_to_build = True
                            DrawCursorRect = True
                            self._start_build = None
                            self._ship_direction = 0
                    elif self._ship_len == 1:
                        if self.Ships.ships_count[1] < self.Ships.counts[1]:
                            self.Ships.ships_count[1] += 1
                            self.Ships.AddShip(1, self._mediocre_ship)
                            self._in_build = True
                        else:
                            print('1-о палубные корабли закончились!.')
                            self._mediocre_ship = None
                            self._build = False
                            self._select_to_build = True
                            DrawCursorRect = True
                            self._start_build = None
                            self._ship_direction = 0
                if self._in_build:
                    self._in_build = False
                    self._build = False
                    self._select_to_build = True
                    DrawCursorRect = True
                    self._start_build = None
                    self._ship_direction = 0
                    self._mediocre_ship = None
                    self._horizontal_build = True

        # for event in self.parent.events:

    def update(self, active, args):
        self.image.fill(self.parent.Colors.Background)
        self.DrawLines()
        self.Ships.draw(self.image)
        self.selected = self.Blocks.GetCollide()
        if self.condition == GAME_CONDITION_WAIT:
            self.condition = GAME_CONDITION_BUILD
        elif self.condition == GAME_CONDITION_BUILD:
            self.inBuild()
        return self.image


E = Exemplar()
G = PlayGame(E, (), demo=True)

pygame.init()
screen = pygame.display.set_mode(sz, pygame.SRCALPHA)
c = pygame.time.Clock()
run = True
while run:
    ev = pygame.event.get()
    E.update(ev)
    screen.blit(G.update(True, ''), (0, 0))
    for e in ev:
        if e.type == pygame.QUIT:
            run = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                run = False
    pygame.display.flip()
    c.tick(60)
