import random
import sys
import threading
import time

import pygame
import numpy

import log
from functions import *
from Gui import *


class Blocks(DATA):
    def __init__(self, display_size: SIZE, w_h: int, left_margin, upper_margin, block_size):
        blocks = {}
        for num_let in range(w_h):
            blocks[num_let] = []
            for num in range(w_h):
                blocks[num_let].append(
                    pygame.Rect(left_margin + num_let * block_size, upper_margin + num * block_size, block_size,
                                block_size))
        self.size = display_size
        self.blocks = blocks
        self.block_size = block_size
        super().__init__(self.blocks)

    def GetRect(self, cords: tuple) -> pygame.Rect:
        try:
            return pygame.Rect(self.blocks[cords[0]][cords[1]])
        except Exception:
            log.critical(f'{cords}.')
            raise ValueError

    def GetShip(self, cords: tuple) -> pygame.Rect:
        """
        Get ship rectangle from frozen coordinates
        Return ship window rectangle
        cords     :    tuple of frozen ship coordinates:   tuple
        return    ->   real ship coordinates
        """
        try:
            cords0 = self.GetRect(cords[0])
            cords1 = self.GetRect(cords[1])
            if cords0[1] == cords1[1]:
                return pygame.Rect(*cords0.topleft, cords1.x - cords0.x + self.block_size, self.block_size)
            else:
                return pygame.Rect(*cords0.topleft, self.block_size, cords1.y - cords0.y + self.block_size)

        except Exception:
            log.critical(f'{cords}.')
            raise ValueError

    def GetShipEnv(self, cords: tuple) -> pygame.Rect:
        """
        GetShipEnv(cords)

        Get real ship rectangle
        Return ship environment rectangle within the block radius

        cords     :    tuple of real ship cords:   tuple
        return    ->   list of all ship blocks
        """
        try:
            return pygame.Rect(cords[0] - self.block_size, cords[1] - self.block_size,
                               cords[2] + self.block_size * 2, cords[3] + self.block_size * 2)
        except Exception:
            log.critical(f'{cords}.')
            raise ValueError

    def GetShipBlocks(self, cords: tuple) -> list:
        """
        GetShipBlocks(cords)

        Get real ship coordinates
        Return all ship blocks

        cords     :    tuple of real ship cords:   tuple
        return    ->   list of all ship blocks
        """
        try:
            blocks = []
            for x in range(cords[0][0], cords[1][0] + 1):
                for y in range(cords[0][1], cords[1][1] + 1):
                    blocks.append((x, y))

            # if cords[0][0] == cords[1][0]:
            #     for pos in range(cords[0][1], cords[1][1] + 1):
            #         blocks.append((cords[0][0], pos))
            # else:
            #     for pos in range(cords[0][0], cords[1][0] + 1):
            #         blocks.append((pos, cords[0][1]))
            return blocks
        except Exception:
            log.critical(f'{cords}')
            return False

    def GetCollide(self):
        for letter in self.blocks:
            for num, block in enumerate(self.blocks[letter]):
                if block.collidepoint(pygame.mouse.get_pos()):
                    return [letter, num]


class Ships:
    def __init__(self, blocks: Blocks, alive_ship_color, not_alive_ship_color, ships_width, solo_count=4, duo_count=3, trio_count=2,
                 quadro_count=1):
        self.counts = {1: solo_count, 2: duo_count, 3: trio_count, 4: quadro_count}
        self.ships = dict.fromkeys([1, 2, 3, 4], {})
        self.ships_count = dict.fromkeys([1, 2, 3, 4], 0)
        self.blocks = blocks
        self.alive_ship_color = alive_ship_color
        self.not_alive_ship_color = not_alive_ship_color
        self.ships_width = ships_width
        self.SumShipsMaxCount = sum(self.counts.values())
        self._start_cord = None
        self._end_cord = None
        self._imaginary_ship = None
        self._imaginary_ship_len = 1
        self._imaginary_ship_direction_is_horizontal = None

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
                pygame.draw.rect(image, self.alive_ship_color, self.blocks.GetShip(ship['ship']), self.ships_width)
        if self._imaginary_ship:
            pygame.draw.rect(image, self.alive_ship_color, self.blocks.GetShip(self._merge_start_end_pos()), self.ships_width)
        self.DrawShipCount(image)

    def DrawShipCount(self, image):
        mid = [self.blocks.size.w // 2 + self.blocks.size.w // 2 // 2, self.blocks.size.h // 2 - self.blocks.size.h // 2 // 1.5]
        ships_count = copy.deepcopy(self.ships_count)
        for type_ship in self.counts.keys():
            counter_block_num = 0
            for num_block in range((self.counts[type_ship] * type_ship) + self.counts[type_ship]):
                if counter_block_num < type_ship:
                    if ships_count[type_ship] < self.counts[type_ship]:
                        color = self.alive_ship_color
                    else:
                        color = self.not_alive_ship_color
                    counter_block_num += 1
                else:
                    color = False
                    counter_block_num = 0
                    ships_count[type_ship] += 1 if ships_count[type_ship] < self.counts[type_ship] else 0
                if color:
                    pygame.draw.rect(image, color, (
                        mid[0] + num_block * (self.blocks.block_size // 2), mid[1] + self.blocks.block_size * type_ship, self.blocks.block_size // 2, self.blocks.block_size // 2),
                                     self.ships_width // 2)

    def DrawShip(self, cords: tuple, image, custom_color=None):
        if custom_color:
            pygame.draw.rect(image, custom_color, self.blocks.GetShip(cords), self.ships_width)
        else:
            pygame.draw.rect(image, self.alive_ship_color, self.blocks.GetShip(cords), self.ships_width)

    def DelShip(self, type_ship, number):
        del self.ships[type_ship][number]

    def Clear(self):
        self.ships = dict.fromkeys([1, 2, 3, 4], {})
        self.ships_count = dict.fromkeys([1, 2, 3, 4], 0)

    def RandomPlacing(self, image):
        threading.Thread(target=self._random_placing, args=[image]).start()

    def HasShip(self, cords):
        return any(map(lambda cord: True if cord == cords else False, GetDeepData(self.ships)))

    def CollideShip(self, ship_cord):
        for _ in self.ships:
            for rc in self.ships[_].values():
                if self.blocks.GetShip(rc['ship']).colliderect(self.blocks.GetShip(ship_cord)):
                    return True
        return False

    def CollideShipEnv(self, ship_cord):
        for _ in self.ships:
            for rc in self.ships[_].values():
                if self.blocks.GetShipEnv(self.blocks.GetShip(rc['ship'])).colliderect(self.blocks.GetShip(ship_cord)):
                    return True
        return False

    def SumShipsCount(self):
        return sum(self.ships_count.values())

    def _update_imaginary_ship(self):
        self._imaginary_ship = self._start_cord, self._end_cord
        self._imaginary_ship_len = max(abs(numpy.array(self._start_cord) - numpy.array(self._end_cord))) + 1

    def _end_build_ship(self):
        self.AddShip(self._imaginary_ship_len, self._imaginary_ship)
        self._clear_imaginary_ship()

    def _clear_imaginary_ship(self):
        self._start_cord = None
        self._end_cord = None
        self._imaginary_ship_len = 1
        self._imaginary_ship = None

    def SetStartPos(self, start, end=None):
        self._start_cord = list(start)
        self._end_cord = list(end if end else start)
        self._imaginary_ship_len = 1
        self._update_imaginary_ship()

    def PassBuildShip(self):
        self._clear_imaginary_ship()

    def EndBuildShip(self):
        self._imaginary_ship = self._merge_start_end_pos()
        if not self.CollideShipEnv(self._imaginary_ship):
            if len(self.counts) >= self._imaginary_ship_len:
                if self.ships_count[self._imaginary_ship_len] < self.counts[self._imaginary_ship_len]:
                    self._end_build_ship()
                    self._clear_imaginary_ship()
                    return None
                else:
                    return_data = self._imaginary_ship_len
                    self._clear_imaginary_ship()
                    return DATA({'type': 'len', 'value': return_data})
            else:
                return_data = self._imaginary_ship_len
                self._clear_imaginary_ship()
                return DATA({'type': 'len', 'value': return_data})

        else:
            self._clear_imaginary_ship()
            return DATA({'type': 'rule', 'value': None})

    def SetDirection(self, is_horizontal: bool):
        self._imaginary_ship_direction_is_horizontal = is_horizontal

    def MoveEndPointTo(self, difference=(), value=0):
        if not self._imaginary_ship_direction_is_horizontal:
            self._end_cord[0] += difference[0] if len(difference) else value
        else:
            self._end_cord[1] += difference[1] if len(difference) else value
        self._update_imaginary_ship()

    def CanMergeDirection(self, actual_pos):
        if not self._imaginary_ship_direction_is_horizontal:
            if not self._start_cord[0] - actual_pos[0]:
                return True
        else:
            if not self._start_cord[1] - actual_pos[1]:
                return True
        return False

    def GetImaginaryShipLen(self):
        return self._imaginary_ship_len

    def GetImaginaryShipCords(self):
        return self._merge_start_end_pos()

    def GetImaginaryShipDirection(self):
        return self._imaginary_ship_direction_is_horizontal

    def GetImaginaryShipStartCord(self):
        return self._start_cord

    def GetImaginaryShipEndCord(self):
        return self._end_cord

    def _merge_start_end_pos(self):
        if not all(numpy.array(self._start_cord) <= numpy.array(self._end_cord)):
            return self._end_cord, self._start_cord
        return self._start_cord, self._end_cord

    def _random_placing(self, image):
        while self.SumShipsMaxCount > self.SumShipsCount() and run:
            self.Clear()
            cord_not_used = dict.fromkeys([x for x in range(len(self.blocks.blocks.keys()) - 1)],
                                          dict.fromkeys([y for y in range(len(self.blocks.blocks.values()) - 1)], True))
            cords_used = []
            errors = 0
            for type_ship, count_ships in enumerate(self.counts.values()):
                if errors > 100:
                    break
                errors = 0
                for _ in range(count_ships):
                    while errors < 100:
                        while errors < 100:
                            errors += 1
                            start_x = random.choice(list(cord_not_used.keys()))
                            start_y = random.choice(list(cord_not_used[start_x]))
                            direct = random.randint(0, 1)
                            if not direct:
                                if not (start_x + type_ship >= len(self.blocks.blocks.keys()) - 1):
                                    if not set(self.blocks.GetShipBlocks(((start_x, start_y), (start_x + type_ship, start_y)))) & set(cords_used):
                                        break
                            else:
                                if not (start_y + type_ship >= len(self.blocks.blocks.values()) - 1):
                                    if not set(self.blocks.GetShipBlocks(((start_x, start_y), (start_x, start_y + type_ship)))) & set(cords_used):
                                        break
                        else:
                            break
                        self.SetStartPos((start_x, start_y))
                        self.SetDirection(direct)
                        self.MoveEndPointTo(value=type_ship)
                        ship = self.GetImaginaryShipCords()
                        self.DrawShip(ship, image, (0, 200, 255))
                        error = self.EndBuildShip()
                        if not error:
                            break
                        else:
                            ship[0][0] -= 1 if ship[0][0] - 1 >= 0 else 0
                            ship[0][1] -= 1 if ship[0][1] - 1 >= 0 else 0
                            ship[1][0] += 1 if ship[1][0] + 1 < len(self.blocks.blocks.keys()) - 1 else 0
                            ship[1][1] += 1 if ship[1][1] + 1 < len(self.blocks.blocks.values()) - 1 else 0
                            for block in G.Ships.blocks.GetShipBlocks(ship):
                                cord_not_used[block[0]][block[1]] = False
                                cords_used.append(block)
                    else:
                        break


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
            'Label': ((41, 42, 43), (91, 92, 93), (232, 234, 236), (232, 234, 236), False, (91, 92, 93), (), False,
                      (255, 255, 255), ()),
            'Button': (
            (41, 42, 43), (255, 255, 255), (232, 234, 236), (0, 0, 0), False, (91, 92, 93), (91, 92, 93), False,
            (91, 92, 93)),
            'ButtonRed': (
            (255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
            'ButtonActive': (
            (255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), False, (100, 0, 200), (), False,
            (91, 92, 93)),
            'Switch': ((64, 64, 64), (64, 64, 64), (0, 255, 0), (255, 255, 255)),
            'Slide': ((53, 86, 140, 100), (53, 86, 140, 100), (38, 80, 148), (138, 180, 248)),
            'List': (
            (29, 29, 31), (29, 29, 31), (232, 234, 236), (255, 255, 255), (41, 42, 45), False, (89, 111, 146), (),
            False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), ()),
            'Path': ((138, 180, 248), (53, 86, 140), (232, 234, 236)),
            'ProgressBar': ((255, 255, 255), (0, 255, 0)),
            'TextInput': (
            (24, 24, 24), (24, 24, 24), (155, 155, 155), (255, 255, 255), False, (100, 0, 255, 100), (), False,
            (100, 0, 255), ()),
            'Red': (255, 0, 0),
            'Green': (0, 255, 0),
            'Blue': (0, 0, 255),
            'White': (0, 0, 255),
            'Scene': {
                'Load': {
                    'Label': ((0, 0, 0, 0), (0, 0, 0, 0), (0, 255, 0), (0, 255, 0)),
                    'ProgressBar': ((24, 24, 24), (0, 255, 0))},
                'Main': {
                    'Button': (
                    (0, 0, 0), (0, 0, 0), (255, 255, 255), (100, 0, 200), True, (24, 24, 24), (0, 0, 0), True,
                    (24, 24, 24), (0, 0, 0)),
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

    def PlaySound(self, *args):
        pass

    def update(self, events):
        self.mouse_left_release = False
        self.mouse_right_release = False
        self.mouse_middle_release = False

        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0

        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = events
        for event in self.events:
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


def RndFunc(self):
    self.parent.Ships.RandomPlacing(self.parent.image)


class PlayGame:
    def __init__(self, parent: Exemplar, enemy: (str, int), **kwargs):
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
        self.Blocks = Blocks(self.size, 10, (self.parent.size.w * 0.5 - self.parent.block_size * 5),
                             (self.parent.size.h * 0.5 - self.parent.block_size * 5), self.parent.block_size)
        self.Ships = Ships(self.Blocks, self.parent.Colors.Lines, (100, 100, 100), self.Blocks.block_size // 7)
        self.KilledShips = Ships(self.Blocks, self.parent.Colors.Lines, (100, 100, 100), self.Blocks.block_size // 7)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.parent.source_ip, self.parent.source_port))
        self.condition = GAME_CONDITION_WAIT
        self.selected = None
        self._activate_press = False
        self._keyboard_input = False
        rect_w, rect_h = self.size.w * 0.1, self.size.h * 0.05
        border = rect_h * BORDER_ATTITUDE
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.ClearMap = Button(self,
                               (self.size.w * 0.1, self.size.h * 0.7 - rect_h, rect_w, rect_h),
                               text_rect,
                               text_rect,
                               self.parent.Language.GameClearMap,
                               self.parent.Language.GameClearMap,
                               (10, 10, 10), (10, 10, 10), (255, 255, 255), (255, 255, 255), False, (100, 100, 200),
                               (255, 255, 255), False, (200, 100, 255), (), border=border,
                               func=lambda s: s.parent.Ships.Clear())
        self.RandomPlacing = Button(self,
                                    (self.size.w * 0.1, self.size.h * 0.7, rect_w, rect_h),
                                    text_rect,
                                    text_rect,
                                    self.parent.Language.GameRandomBuild,
                                    self.parent.Language.GameRandomBuild,
                                    (100, 100, 100), (100, 100, 100), (255, 255, 255), (255, 255, 255), False,
                                    (100, 100, 200), (255, 255, 255), False, (200, 100, 255), (), border=border,
                                    func=RndFunc)
        self.Elements = pygame.sprite.Group(self.ClearMap, self.RandomPlacing)
        self._random_place = False

    def DrawLines(self):
        if not self.Lines:
            self.Lines = pygame.Surface(self.parent.size, pygame.SRCALPHA)
            left_margin, upper_margin = (self.parent.size.w * 0.5 - self.parent.block_size * 5), (
                        self.parent.size.h * 0.5 - self.parent.block_size * 5)
            for it in range(11):
                pygame.draw.line(self.Lines, self.parent.Colors.Lines,
                                 (left_margin, upper_margin + it * self.parent.block_size),
                                 (
                                 left_margin + 10 * self.parent.block_size, upper_margin + it * self.parent.block_size),
                                 1)
                pygame.draw.line(self.Lines, self.parent.Colors.Lines,
                                 (left_margin + it * self.parent.block_size, upper_margin),
                                 (
                                 left_margin + it * self.parent.block_size, upper_margin + 10 * self.parent.block_size),
                                 1)
                if it < 10:
                    font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.parent.Language.Letters[0],
                                                                   pygame.Rect(0, 0, self.parent.block_size,
                                                                               self.parent.block_size)))
                    num = font.render(str(it + 1), True, self.parent.Colors.Lines)
                    letter = font.render(self.parent.Language.Letters[it], True, self.parent.Colors.Lines)
                    num_ver_width = num.get_width()
                    num_ver_height = num.get_height()
                    letters_hor_width = letter.get_width()
                    self.Lines.blit(num, (left_margin - (self.parent.block_size * 0.5 + num_ver_width * 0.5),
                                          upper_margin + it * self.parent.block_size + (
                                                      self.parent.block_size * 0.5 - num_ver_height * 0.5)))
                    self.Lines.blit(letter, (left_margin + it * self.parent.block_size + (
                                self.parent.block_size * 0.5 - letters_hor_width * 0.5),
                                             upper_margin - font.size(self.parent.Language.Letters[it])[1] * 1.2))
        self.image.blit(self.Lines, (0, 0))

    def GetData(self):
        pass

    def inBuild(self):
        self.ClearMap.update()
        self.RandomPlacing.update()
        if self.ClearMap.isCollide() and self.parent.mouse_left_release:
            self.ClearMap.Function()
        elif self.RandomPlacing.isCollide() and self.parent.mouse_left_release:
            self.RandomPlacing.Function()
            self._random_place = True
        if self._random_place:
            if self.Ships.SumShipsMaxCount == self.Ships.SumShipsCount():
                self.condition += 1
                self._activate_press = False
        elif self.parent.mouse_left_press or self._activate_press:
            if self.selected:
                if self.Ships.GetImaginaryShipStartCord():
                    as_array_end_pos = numpy.array(self.Ships.GetImaginaryShipEndCord())
                    as_array_selected = numpy.array(self.selected)
                    distance = as_array_selected - as_array_end_pos
                    if any(distance):
                        self.Ships.MoveEndPointTo(distance)
                    if self.Ships.GetImaginaryShipDirection() is None or self.Ships.CanMergeDirection(self.selected):
                        self.Ships.SetDirection(True if not distance[0] else False)
                else:
                    self.Ships.SetStartPos(self.selected)
        else:
            if self.Ships.GetImaginaryShipStartCord() and self.Ships.GetImaginaryShipCords():
                error = self.Ships.EndBuildShip()
                if error:
                    if error.type == 'rule':
                        print('Ne Po Pravilam.')
                    elif error.type == 'count':
                        print(f'{error.value}-h kletochniye corabli zakonchilis')
                    elif error.type == 'len':
                        print('max len ship: 4')
                elif self.Ships.SumShipsMaxCount == self.Ships.SumShipsCount():
                    self.condition += 1

    def inGame(self):  # issue
        pass

    def update(self, active, args):
        for event in self.parent.events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_SPACE):
                    self._activate_press = True
                elif event.key == pygame.K_TAB:
                    self._keyboard_input = [0, 0]
                    pygame.key.set_repeat(200, 100)
                if self._keyboard_input:
                    if event.key == pygame.K_LEFT:
                        self._keyboard_input[0] -= 1 if self._keyboard_input[0] else 0
                    elif event.key == pygame.K_RIGHT:
                        self._keyboard_input[0] += 1 if self._keyboard_input[0] + 1 < len(
                            self.Blocks.blocks.keys()) else 0
                    elif event.key == pygame.K_UP:
                        self._keyboard_input[1] -= 1 if self._keyboard_input[1] else 0
                    elif event.key == pygame.K_DOWN:
                        self._keyboard_input[1] += 1 if self._keyboard_input[1] + 1 < len(
                            self.Blocks.blocks.values()) else 0

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self._activate_press = False
        if self._keyboard_input and self.parent.mouse_left_press:
            self._keyboard_input = False
        self.image.fill(self.parent.Colors.Background)
        self.Elements.draw(self.image)
        self.DrawLines()
        self.Ships.draw(self.image)
        self.selected = self.Blocks.GetCollide()

        if self._keyboard_input:
            self.selected = self._keyboard_input
        if self.selected:
            if self.Ships.GetImaginaryShipStartCord():
                if not self.Blocks.GetRect(self.selected).colliderect(
                        self.Blocks.GetShip(self.Ships.GetImaginaryShipCords())):
                    self.Ships.DrawShip((self.selected, self.selected), self.image, (0, 255, 0))
            else:
                self.Ships.DrawShip((self.selected, self.selected), self.image, (0, 255, 0))

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
    pygame.key.set_repeat(1, 1)
    for e in ev:
        if e.type == pygame.QUIT:
            run = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                run = False
    pygame.display.flip()
    c.tick(60)
