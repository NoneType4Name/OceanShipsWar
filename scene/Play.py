import pygame

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
                return pygame.Rect(*numpy.array(cords0.topleft) + 1, cords1.x - cords0.x + self.block_size - 1, self.block_size - 1)
            else:
                return pygame.Rect(*numpy.array(cords0.topleft) + 1, self.block_size - 1, cords1.y - cords0.y + self.block_size - 1)

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
                    blocks.append([x, y])
            return blocks
        except Exception:
            log.critical(f'{cords}')
            return False

    def GetCollide(self):
        for letter in self.blocks:
            for num, block in enumerate(self.blocks[letter]):
                if block.collidepoint(pygame.mouse.get_pos()):
                    return [letter, num]

    def GetShipLen(self, cords):
        return max(abs(numpy.array(cords[0]) - numpy.array(cords[1]))) + 1


def AliveCount(self, image, rect):
    pygame.draw.rect(image, self.alive_ship_color, rect, self.ships_width // 2)


def NotAliveCount(self, image, rect):
    pygame.draw.rect(image, self.not_alive_ship_color, rect, self.ships_width // 2)


def AliveShip(self, image, rect):
    pygame.draw.rect(image, self.alive_ship_color, rect, self.ships_width)


def NotAliveShip(self, image, rect):
    pygame.draw.rect(image, self.not_alive_ship_color, rect, self.ships_width)


def MyAliveShip(self, image, rect):
    pygame.draw.rect(image, self.alive_ship_color, rect, self.ships_width)


def MyNotAliveShip(self, image, rect):
    pygame.draw.rect(image, self.not_alive_ship_color, rect, self.ships_width)


def DieBlocks(self, image, rect):
    pygame.draw.line(image, self.not_alive_ship_color, numpy.array(rect.topleft) + self.ships_width // 2, numpy.array(rect.bottomright) - self.ships_width // 2, self.ships_width)
    pygame.draw.line(image, self.not_alive_ship_color, numpy.array(rect.topright) - numpy.array((self.ships_width // 2, -self.ships_width // 2)),
                     numpy.array(rect.bottomleft) + numpy.array((self.ships_width // 2, -self.ships_width // 2)), self.ships_width)


def MyDieBlocks(self, image, rect):
    pygame.draw.line(image, self.not_alive_ship_color,
                     numpy.array(rect.topright) - numpy.array((self.ships_width // 2, -self.ships_width // 2)),
                     numpy.array(rect.midbottom) - numpy.array((0, self.ships_width // 2)))
    pygame.draw.line(image, self.not_alive_ship_color,
                     numpy.array(rect.midtop) + numpy.array((0, self.ships_width // 2)),
                     numpy.array(rect.bottomleft) - numpy.array((-self.ships_width // 2, self.ships_width // 2)))


def EscActivate(self, **kwargs):
    self.parent.socket.close()
    log.debug('UDP Socket closed.')
    if self.parent.AroundNatSocket:
        self.parent.AroundNatSocket.close()
        log.debug('TCP Socket closed.')
    log.debug('Play Game: Exit.')
    self.parent.parent.SetScene(self.parent.InputScene, *kwargs)
    self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')


class Ships:
    def __init__(self, parent, blocks: Blocks, alive_ship_color, not_alive_ship_color, ships_width,
                 func_to_draw_alive_count, func_to_draw_not_alive_count,
                 func_to_draw_alive_ship, func_to_draw_not_alive_ship,
                 func_to_draw_die_blocks,
                 solo_count=4, duo_count=3, trio_count=2,
                 quadro_count=1):
        self.parent = parent
        self.counts = {1: solo_count, 2: duo_count, 3: trio_count, 4: quadro_count}
        log.debug(f'Ships count: {self.counts}')
        self.ships = dict(map(lambda key: (key, {}), [1, 2, 3, 4]))
        self.ships_count = dict.fromkeys([1, 2, 3, 4], 0)
        self.die_ships = dict(map(lambda key: (key, {}), [1, 2, 3, 4]))
        self.die_ships_count = dict.fromkeys([1, 2, 3, 4], 0)
        self.die_blocks = []

        self.blocks = blocks
        self.alive_ship_color = alive_ship_color
        self.not_alive_ship_color = not_alive_ship_color
        self.ships_width = ships_width
        self.func_to_draw_alive_count = func_to_draw_alive_count
        self.func_to_draw_not_alive_count = func_to_draw_not_alive_count
        self.func_to_draw_alive_ship = func_to_draw_alive_ship
        self.func_to_draw_not_alive_ship = func_to_draw_not_alive_ship
        self.func_to_draw_die_blocks = func_to_draw_die_blocks
        self.SumShipsMaxCount = sum(self.counts.values())
        self._start_cord = None
        self._end_cord = None
        self._imaginary_ship = None
        self._imaginary_ship_len = 1
        self._imaginary_ship_direction_is_horizontal = None

    def draw(self, image, alive=True, not_alive=True, die_blocks=True, imaginary=True):
        if alive:
            data = GetDeepData([[list(self.ships[type_sh][s].values())[0] for s in self.ships[type_sh]] for type_sh in self.ships])
            if data:
                [self.func_to_draw_alive_ship(self, image, self.blocks.GetShip(ship)) for ship in data]
        if not_alive:
            data = GetDeepData([[list(self.die_ships[type_sh][s].values())[0] for s in self.die_ships[type_sh]] for type_sh in self.die_ships])
            if data:
                [self.func_to_draw_not_alive_ship(self, image, self.blocks.GetShip(ship)) for ship in data]
        if die_blocks:
            [self.func_to_draw_die_blocks(self, image, self.blocks.GetRect(block)) for block in self.die_blocks]
        if self._imaginary_ship and imaginary:
            self.func_to_draw_alive_ship(self, image, self.blocks.GetShip(self._merge_start_end_pos()))
        self.DrawShipCount(image)

    def DrawShipCount(self, image):
        mid = [self.blocks.size.w // 2 + self.blocks.size.w // 2 // 2, self.blocks.size.h // 2 - self.blocks.size.h // 2 // 1.5]
        ships_count = copy.deepcopy(self.ships_count)
        for type_ship in self.counts.keys():
            counter_block_num = 0
            for num_block in range((self.counts[type_ship] * type_ship) + self.counts[type_ship]):
                if counter_block_num < type_ship:
                    if ships_count[type_ship] < self.counts[type_ship]:
                        color = True
                    else:
                        color = False
                    counter_block_num += 1
                else:
                    color = None
                    counter_block_num = 0
                    ships_count[type_ship] += 1 if ships_count[type_ship] < self.counts[type_ship] else 0
                if color is not None:
                    if color:
                        self.func_to_draw_alive_count(
                            self,
                            image,
                            (mid[0] + num_block * (self.blocks.block_size // 2), mid[1] + self.blocks.block_size * type_ship, self.blocks.block_size // 2, self.blocks.block_size // 2))
                    else:
                        self.func_to_draw_not_alive_count(
                            self,
                            image,
                            (mid[0] + num_block * (self.blocks.block_size // 2), mid[1] + self.blocks.block_size * type_ship, self.blocks.block_size // 2, self.blocks.block_size // 2))

    def DrawShip(self, cords: tuple, image, custom_color=None):
        if custom_color:
            pygame.draw.rect(image, custom_color, self.blocks.GetShip(cords), self.ships_width)
        else:
            pygame.draw.rect(image, self.alive_ship_color, self.blocks.GetShip(cords), self.ships_width)

    def AddShip(self, ship, type_ship=None):
        if type_ship is None:
            type_ship = max(abs(numpy.array(ship[0]) - numpy.array(ship[1]))) + 1
        if self.counts[type_ship] > self.ships_count[type_ship]:
            self.ships_count[type_ship] += 1
            self.ships[type_ship][self.ships_count[type_ship]] = {
                'ship': ship,
                'blocks': self.blocks.GetShipBlocks(ship)
            }
            log.debug(f'Added new ship: {ship}, type: {type_ship}.')
        else:
            log.warning(f'{type_ship} ships ended!, ship:{ship},\n{self.ships}.')

    def DelShip(self, type_ship, number):
        if number in self.ships[type_ship]:
            del self.ships[type_ship][number]
            self.ships_count[type_ship] -= 1
            log.debug(f'Deleted ship type:{type_ship}, number:{number}, remainder: {self.ships_count[type_ship]}')
        else:
            log.warning(f'{type_ship} ship is not in Ships!, ship num: {number}, \n{self.ships}.')

    def KillBlock(self, block):
        rtn = self.CollideShip((block, block))
        if rtn:
            type_ship, number = rtn
            self.ships[type_ship][number]['blocks'].remove(block)
            self.die_blocks.append(block)
            log.debug(f'Block {block} successful killed.')
            if not self.ships[type_ship][number]['blocks']:
                log.debug(f'Ship type: {type_ship}, num: {number} killed (cords:{self.ships[type_ship][number]["ship"]}')
                self.KillShip(self.ships[type_ship][number]['ship'], type_ship)
                return True
            return False
        elif block in self.die_blocks:
            log.warning(f'Duplicated data, block: {block} already die.')
            return 0
        else:
            return None

    def KillShip(self, ship, type_ship, number=False):
        if type_ship is None:
            type_ship = max(abs(numpy.array(ship[0]) - numpy.array(ship[1]))) + 1

        ship_num = len(self.die_ships[type_ship]) + 1
        self.die_ships[type_ship][ship_num] = {}
        self.die_ships[type_ship][ship_num]['ship'] = ship
        self.die_ships[type_ship][ship_num]['blocks'] = self.blocks.GetShipBlocks(ship)
        self.die_ships_count[type_ship] += 1
        if self.HasShip(ship):
            if type(number) is int:
                self.DelShip(type_ship, number)
            else:
                self.DelShip(*self.CollideShip(ship))
            log.debug(f'Ship type: {type_ship}, num: {number}, cords: {ship} successful killed.')
        else:
            log.warning(f'Ship cords: {ship} (type: {type_ship}, num: {number}), is not alive!, alive ships: {self.ships}.')

    def Clear(self):
        self.ships = dict(map(lambda key: (key, {}), [1, 2, 3, 4]))
        self.ships_count = dict.fromkeys([1, 2, 3, 4], 0)
        self.die_ships = dict(map(lambda key: (key, {}), [1, 2, 3, 4]))
        self.die_ships_count = dict.fromkeys([1, 2, 3, 4], 0)
        self.die_blocks = []
        log.debug('Ships successfully removed.', stack_info=True)

    def HasShip(self, ship):
        return ship in GetDeepData([[list(self.ships[type_sh][s].values())[0] for s in self.ships[type_sh]] for type_sh in self.ships])

    def CollideShip(self, ship_cord):
        for type_ship in self.ships:
            for num_ship in self.ships[type_ship]:
                if self.blocks.GetShip(self.ships[type_ship][num_ship]['ship']).colliderect(self.blocks.GetShip(ship_cord)):
                    # log.debug(f'ship: {ship_cord} collided with {type_ship}, {num_ship}.', stack_info=True)
                    return type_ship, num_ship
        return False

    def CollideShipEnv(self, ship_cord):
        for type_ship in self.ships:
            for num_ship in self.ships[type_ship]:
                if self.blocks.GetShipEnv(self.blocks.GetShip(self.ships[type_ship][num_ship]['ship'])).colliderect(self.blocks.GetShip(ship_cord)):
                    # log.debug(f'ship env: {ship_cord} collided with {type_ship}, {num_ship}.', stack_info=True)
                    return type_ship, num_ship
        return False

    def CollideDieShip(self, ship_cord):
        for type_ship in self.die_ships:
            for num_ship in self.die_ships[type_ship]:
                if self.blocks.GetShip(self.die_ships[type_ship][num_ship]['ship']).colliderect(self.blocks.GetShip(ship_cord)):
                    # log.debug(f'Die ship: {ship_cord} collided with {type_ship}, {num_ship}.', stack_info=True)
                    return type_ship, num_ship
        return False

    def CollideDieShipEnv(self, ship_cord):
        for type_ship in self.die_ships:
            for num_ship in self.die_ships[type_ship]:
                if self.blocks.GetShipEnv(self.blocks.GetShip(self.die_ships[type_ship][num_ship]['ship'])).colliderect(self.blocks.GetShip(ship_cord)):
                    # log.debug(f'Die ship env: {ship_cord} collided with {type_ship}, {num_ship}.', stack_info=True)
                    return type_ship, num_ship
        return False

    def SumShipsCount(self):
        return sum(self.ships_count.values())

    def SumDieShipCount(self):
        return sum(self.die_ships_count.values())

    def SetStartPos(self, start, end=None):
        self._start_cord = list(start)
        self._end_cord = list(end if end else start)
        self._imaginary_ship_len = 1
        self._update_imaginary_ship()
        log.debug(f'Start pos set at: {self._start_cord}, end cord: {self._end_cord}.')

    def EndBuildShip(self):
        log.debug('End build ship start.')
        self._imaginary_ship = self._merge_start_end_pos()
        if not self.CollideShipEnv(self._imaginary_ship):
            if len(self.counts) >= self._imaginary_ship_len:
                if self.ships_count[self._imaginary_ship_len] < self.counts[self._imaginary_ship_len]:
                    self._end_build_ship()
                    self._clear_imaginary_ship()
                    log.debug('Success end build ship.')
                    return None
                else:
                    return_data = self._imaginary_ship_len
                    self._clear_imaginary_ship()
                    log.debug('ships limit exceeded.')
                    return DATA({'type': 'count', 'value': return_data})
            else:
                return_data = self._imaginary_ship_len
                self._clear_imaginary_ship()
                log.debug('ship length limit exceeded.')
                return DATA({'type': 'len', 'value': return_data})

        else:
            self._clear_imaginary_ship()
            log.debug('Ship is collied with other ship env.')
            return DATA({'type': 'rule', 'value': None})

    def SetDirection(self, is_horizontal: bool):
        self._imaginary_ship_direction_is_horizontal = is_horizontal
        log.debug(f'Ship is horizontal: {is_horizontal}, ship cord: {self.GetImaginaryShipCords()}, len: {self.GetImaginaryShipLen()}')

    def MoveEndPointTo(self, difference=(), value=0):
        if not self._imaginary_ship_direction_is_horizontal:
            self._end_cord[0] += difference[0] if len(difference) else value
        else:
            self._end_cord[1] += difference[1] if len(difference) else value
        self._update_imaginary_ship()
        log.debug(f'End cord moved to: {self._end_cord}, ship: {self.GetImaginaryShipCords()}, len: {self.GetImaginaryShipLen()}, horizontal: {self.GetImaginaryShipDirection()}')

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

    def RandomPlacing(self, image):
        threading.Thread(target=self._random_placing, args=[image], daemon=True).start()

    def _merge_start_end_pos(self):
        if not all(numpy.array(self._start_cord) <= numpy.array(self._end_cord)):
            return self._end_cord, self._start_cord
        return self._start_cord, self._end_cord

    def _random_placing(self, image):
        log.debug('Start random placing.')
        while self.SumShipsMaxCount > self.SumShipsCount() and self.parent.parent.RUN and self.parent.parent.ConvertScene.new.type == PLAY:
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
                                    if not {tuple(map(tuple, self.blocks.GetShipBlocks(((start_x, start_y), (start_x + type_ship, start_y)))))} & set(map(tuple, cords_used)):
                                        break
                            else:
                                if not (start_y + type_ship >= len(self.blocks.blocks.values()) - 1):
                                    if not {tuple(map(tuple, self.blocks.GetShipBlocks(((start_x, start_y), (start_x, start_y + type_ship)))))} & set(map(tuple, cords_used)):
                                        break
                        else:
                            break
                        self.SetStartPos((start_x, start_y))
                        self.SetDirection(direct)
                        self.MoveEndPointTo(value=type_ship)
                        ship = self.GetImaginaryShipCords()
                        self.DrawShip(ship, image, (0, 200, 255))
                        time.sleep(0.005)
                        error = self.EndBuildShip()
                        if not error:
                            break
                        else:
                            ship[0][0] -= 1 if ship[0][0] - 1 >= 0 else 0
                            ship[0][1] -= 1 if ship[0][1] - 1 >= 0 else 0
                            ship[1][0] += 1 if ship[1][0] + 1 < len(self.blocks.blocks.keys()) - 1 else 0
                            ship[1][1] += 1 if ship[1][1] + 1 < len(self.blocks.blocks.values()) - 1 else 0
                            for block in self.blocks.GetShipBlocks(ship):
                                cord_not_used[block[0]][block[1]] = False
                                cords_used.append(block)
                    else:
                        break
        log.debug('End random placing.')

    def _update_imaginary_ship(self):
        self._imaginary_ship = self._start_cord, self._end_cord
        self._imaginary_ship_len = max(abs(numpy.array(self._start_cord) - numpy.array(self._end_cord))) + 1

    def _end_build_ship(self):
        self.AddShip(self._imaginary_ship, self._imaginary_ship_len)
        self._clear_imaginary_ship()

    def _clear_imaginary_ship(self):
        self._start_cord = None
        self._end_cord = None
        self._imaginary_ship_len = 1
        self._imaginary_ship = None


def RndFunc(self):
    self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')
    self.parent.Ships.RandomPlacing(self.parent.image)


def again(self):
    self.parent.Again()
    self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')


class PlayGame:
    def __init__(self, parent, input_scene, kwargs):
        self.type = PLAY
        self.parent = parent
        self.InputScene = input_scene
        self.AroundNatSocket, self.external_host, self.external_port, self.enemy_external_host, self.enemy_external_port, self.enemy_host, self.enemy_port = None, None, None, None, None, None, None
        if 'enemy' in kwargs:
            self.enemy_host, self.enemy_port = kwargs.get('enemy')
        self.link = False
        if 'link' in kwargs and kwargs.get('link'):
            self.link = True
            lnk = kwargs.get('link')
            if isinstance(lnk, (tuple, list)):
                self.external_host, self.external_port, self.AroundNatSocket, self.enemy_external_host, self.enemy_external_port = lnk
            else:
                self.AroundNatSocket = lnk

        self.size = self.parent.size
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.image.fill(self.parent.Colors.Background)
        self.Lines = None
        self.Blocks = Blocks(self.size, 10, (self.parent.size.w * 0.5 - self.parent.block_size * 5),
                             (self.parent.size.h * 0.5 - self.parent.block_size * 5), self.parent.block_size)
        self.Ships = Ships(self, self.Blocks, self.parent.Colors.Lines, (100, 100, 100), self.Blocks.block_size // 7,
                           AliveCount, NotAliveCount, MyAliveShip, MyNotAliveShip, MyDieBlocks)
        self.EnemyShips = Ships(self, self.Blocks, (255, 0, 0), (0, 0, 255), self.Blocks.block_size // 7,
                                AliveCount, NotAliveCount, AliveShip, NotAliveShip, DieBlocks)

        self.socket = kwargs.get('socket')
        self.socket.settimeout(None)
        self.socket_activated = False
        log.debug(f'Play Game inited, enemy TCP addr: {GetIpFromTuple((self.enemy_external_host, self.enemy_external_port))}, '
                  f'enemy UDP addr: {GetIpFromTuple((self.enemy_host, self.enemy_port))}, '
                  f'external addr: {GetIpFromTuple((self.external_host, self.external_port))}, '
                  f'UDP socket: {self.socket}.')

        self.recv_thread = threading.Thread(target=lambda a: a, args=[None], daemon=True)
        self.recv_thread.start()
        self.send_messages = 0
        self.recv_messages = 0
        self.attacked_blocks = []
        self.condition = GAME_CONDITION_WAIT
        self.events = []
        self.selected = None
        self._activate_press = False
        self._activate_release = False
        self._keyboard_input = False
        self._activate = 0
        self._activate_enemy = 0
        self._send_dict = {
            'ships': self.Ships.ships,
            'ships_count': self.Ships.counts,
            'die_ships': self.Ships.die_ships,
            'die_ships_count': self.Ships.die_ships_count,
            'die_blocks': self.Ships.die_blocks,
            'attacked_blocks': self.attacked_blocks,
            'condition': self.condition,
            'events': self.events,
            'count': self.send_messages
        }
        self._recv_dict = {
            'ships': self.EnemyShips.ships,
            'ships_count': self.EnemyShips.counts,
            'die_ships': self.EnemyShips.die_ships,
            'die_ships_count': self.EnemyShips.die_ships_count,
            'die_blocks': self.EnemyShips.die_blocks,
            'attacked_blocks': [],
            'condition': self.condition,
            'events': [],
            'count': self.recv_messages
        }
        rect_w, rect_h = self.size.w * 0.1, self.size.h * 0.05
        border = rect_h * BORDER_ATTITUDE
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.ClearMap = Button(self,
                               (self.size.w * 0.1, self.size.h * 0.7 - rect_h, rect_w, rect_h),
                               text_rect,
                               text_rect,
                               self.parent.Language.GameClearMap,
                               self.parent.Language.GameClearMap,
                               *self.parent.Colors.ButtonRed, border=border,
                               func=lambda s: s.parent.Ships.Clear() or s.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select'))
        self.RandomPlacing = Button(self,
                                    (self.size.w * 0.1, self.size.h * 0.7, rect_w, rect_h),
                                    text_rect,
                                    text_rect,
                                    self.parent.Language.GameRandomBuild,
                                    self.parent.Language.GameRandomBuild,
                                    *self.parent.Colors.Button,
                                    border=border,
                                    func=RndFunc)
        rect_w, rect_h = self.size.w * 0.2, self.size.h * 0.1
        border = rect_h * BORDER_ATTITUDE
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.EndGameLabel = Label(self, (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.7, rect_w, rect_h * 0.5),
                                  text_rect,
                                  0.5,
                                  '',
                                  *parent.Colors.Scene.Load.Label
                                  )
        self.MoveLabel = Label(self, (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.9, rect_w, rect_h),
                               (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.9, rect_w, rect_h),
                               0.5,
                               '',
                               *parent.Colors.Scene.Load.Label
                               )
        rect_w, rect_h = self.size.h * 0.22, self.size.h * 0.07
        border = rect_h * BORDER_ATTITUDE
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        # self.EndGameButtonAgain = Button(self,
        #                                  (self.size.w * 0.5 - rect_w * 0.5, self.size.h * 0.4 - rect_h * 0.5, rect_w, rect_h),
        #                                  text_rect,
        #                                  text_rect,
        #                                  'Again',
        #                                  'Again',
        #                                  (100, 100, 100), (100, 100, 100), (255, 255, 255), (255, 255, 255), False,
        #                                  (100, 100, 200), (255, 255, 255), False, (200, 100, 255), (), border=border,
        #                                  func=RndFunc)
        self.EndGameButtonQuit = Button(self,
                                        (self.size.w * 0.5 - rect_w * 0.5, self.size.h * 0.5 - rect_h * 0.5, rect_w, rect_h),
                                        text_rect,
                                        text_rect,
                                        self.parent.Language.PlayGameQuit,
                                        self.parent.Language.PlayGameQuit,
                                        *self.parent.Colors.Button, border=border,
                                        func=EscActivate)
        self.BuildElements = pygame.sprite.Group(self.ClearMap, self.RandomPlacing, self.MoveLabel)
        self.GameElements = pygame.sprite.Group(self.MoveLabel)
        self.EndGameElements = pygame.sprite.Group(self.EndGameLabel, self.EndGameButtonQuit)
        self._random_place = False
        self.ActivateSocket()

    def Again(self):
        pass

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
                    num = Font.render(str(it + 1), pygame.Rect(0, 0, self.parent.block_size, self.parent.block_size), True, self.parent.Colors.Lines)
                    letter = Font.render(self.parent.Language.Letters[it], pygame.Rect(0, 0, self.parent.block_size, self.parent.block_size), True, self.parent.Colors.Lines)
                    num_ver_width = num.get_width()
                    num_ver_height = num.get_height()
                    letters_hor_width = letter.get_width()
                    self.Lines.blit(num, (left_margin - (self.parent.block_size * 0.5 + num_ver_width * 0.5),
                                          upper_margin + it * self.parent.block_size + (
                                                      self.parent.block_size * 0.5 - num_ver_height * 0.5)))
                    self.Lines.blit(letter, (left_margin + it * self.parent.block_size + (
                                self.parent.block_size * 0.5 - letters_hor_width * 0.5),
                                             upper_margin - letter.get_height() * 1.2))
        self.image.blit(self.Lines, (0, 0))

    def ActivateSocket(self):
        threading.Thread(target=self._activate_socket, daemon=True).start()
        log.debug('Socket activate start.')

    def _ping(self):
        log.debug('Start TCP socket ping method.')
        while self.parent.RUN and self.parent.ConvertScene.new.type == PLAY:
            try:
                try:
                    l = time.time()
                    while time.time() - l < 1 and self.parent.RUN and self.parent.ConvertScene.new.type == PLAY:
                        pass
                    self.AroundNatSocket.send('ping!.'.encode())
                except (ConnectionAbortedError, OSError):
                    self.AroundNatSocket.close()
            except Exception as err:
                log.warning(err, stack_info=True, exc_info=True)
                self.parent.Report(err)
                self.Event(GAME_EVENT_LEAVE_GAME, {})

    def _around_nat(self):
        log.debug('TCP connection start.')
        threading.Thread(target=self._ping, daemon=True).start()
        try:
            if self.enemy_host:
                self.AroundNatSocket.send(f'ConnectAroundNAT{self.enemy_external_host}:{self.enemy_external_port}|'
                                          f'{self.enemy_host}:{self.external_port}'.encode())
                log.debug(f'ConnectAroundNAT{self.enemy_external_host}:{self.enemy_external_port}|'
                          f'{self.enemy_host}:{self.external_port}')
            while self.parent.RUN and self.parent.ConvertScene.new.type == PLAY:
                try:
                    d = self.AroundNatSocket.recv(1024).decode()
                except (ConnectionAbortedError, OSError) as err:
                    log.debug(f'TCP connection aborted, error: type:{type(err)}, msg: {err}', stack_info=True, exc_info=True)
                    self.Event(GAME_EVENT_LEAVE_GAME, {})
                    break
                if 'pong!.' not in d:
                    log.debug(4)
                    log.debug(f'TCP socket recv: {d}.')
                    if self.enemy_host:
                        if 'ConnectAroundNATInboundError' in d:
                            self.socket.shutdown(0)
                            self.socket.close()
                            log.warning('Incorrect connection link.')
                            self.parent.AddNotification(self.parent.Language.PlayGameIncorrectLink)
                            self.parent.SetScene(MAIN)
                            break
                    else:
                        if 'ConnectAroundNATInbound' in d and not self.enemy_host:
                            log.debug('TCP socket received enemy addr.')
                            self.enemy_host, self.enemy_port = GetIpFromString(d.replace('ConnectAroundNATInbound', ''))
                            log.debug(f'Enemy UDP addr: {GetIpFromTuple((self.enemy_host, self.enemy_port))}')
                            break
            try:
                self.AroundNatSocket.shutdown(0)
                self.AroundNatSocket.close()
            except OSError:
                pass
            log.debug('TCP connection close.')
        except Exception as err:
            log.critical(err, stack_info=True, exc_info=True)
            self.parent.Report(err)
            self.Event(GAME_EVENT_LEAVE_GAME, {})

    def _read_thread(self):
        log.debug('Started UDP waiting enemy connect.')
        while not self._activate_enemy and self.parent.RUN and self.parent.ConvertScene.new.type == PLAY:
            try:
                data, addr = self.socket.recvfrom(GAME_DATA_LEN)
                data = data.decode()
                log.debug(f'UDP socket received data: {data}')
                if 'OSW' in data:
                    data = data.split(',')
                    self.enemy_host, self.enemy_port = addr
                    self._activate_enemy = float(data[1])
                    log.debug(f'Enemy UDP addr: {GetIpFromTuple((self.enemy_host, self.enemy_port))}.')
                    break
            except UnicodeError:
                log.warning(f'UDP socket received unknown data: {data}, from: {addr}.')
            except OSError:
                self.Event(GAME_EVENT_LEAVE_GAME, {})

    def _activate_socket(self):
        self._activate = time.time()
        log.debug('UDP connection start.')
        threading.Thread(target=self._read_thread, daemon=True).start()
        if self.link:
            threading.Thread(target=self._around_nat, daemon=True).start()
        log.debug('Waiting UDP enemy connection.')
        while not self.socket_activated and self.parent.RUN and self.parent.ConvertScene.new.type == PLAY:
            if self.enemy_host:
                try:
                    self.socket.sendto(f'OSW,{self._activate},{self._activate_enemy}'.encode(), (self.enemy_host, self.enemy_port))
                    if self._activate_enemy:
                        self.socket_activated = True
                        self.recv_thread = threading.Thread(target=self._socket_recv, daemon=True)
                        self.recv_thread.start()
                        self.socket.settimeout(GAME_PING_DELAY)
                        log.debug(f'UDP socket enemy connected, UDP ping delay:{self.socket.gettimeout()}.')
                        return
                except Exception as err:
                    log.critical(err, stack_info=True, exc_info=True)
                    self.parent.Report(err)
                    self.Event(GAME_EVENT_LEAVE_GAME, {})

    def _socket_recv(self):
        log.debug('UDP receiver started.')
        while self.socket_activated and self.parent.RUN and self.parent.ConvertScene.new.type == PLAY:
            try:
                data = self.socket.recv(GAME_DATA_LEN)
                data = data.decode()
                if 'OSW' in data:
                    data = data.split(',')
                    if not float(data[2]):
                        self.socket.sendto(f'OSW,{self._activate},{self._activate_enemy}'.encode(), (self.enemy_host, self.enemy_port))
                    continue
                elif 'SYNC' in data:
                    self.Send()
                    continue
                elif 'PING' in data:
                    self.Send('PONG!.')
                elif 'PONG' in data:
                    self.socket.settimeout(GAME_PING_DELAY)
                    continue
                else:
                    data = literal_eval(data)
                    if data['count'] >= self.recv_messages:
                        self._recv_dict = data
                        self.recv_messages += 1
                    else:
                        continue
                self.EnemyShips.ships = self._recv_dict['ships']
                self.EnemyShips.ships_count = self._recv_dict['ships_count']
                self.EnemyShips.die_ships = self._recv_dict['die_ships']
                self.EnemyShips.die_ships_count = self._recv_dict['die_ships_count']
                self.EnemyShips.die_blocks = self._recv_dict['die_blocks']
                log.debug(f'Event counts: {len(self._recv_dict["events"])}.')
                for event in self._recv_dict['events']:
                    event = DATA(event)
                    if event.type == GAME_EVENT_ATTACK:
                        block = event.block
                        result = self.Ships.KillBlock(block)
                        log.debug(f'Enemy attached block: {block}.')
                        if result is None:
                            log.debug('Enemy attack missed.')
                            self.MergeCondition(GAME_CONDITION_ATTACK)
                            self.parent.PlaySound(SOUND_TYPE_GAME, 'miss')
                        elif result is False:
                            log.debug('Wounded by enemy attack.')
                            self.MergeCondition(GAME_CONDITION_WAIT_AFTER_ATTACK)
                            self.parent.PlaySound(SOUND_TYPE_GAME, 'wound')
                        elif result is True:
                            log.debug('Killed by enemy attack.')
                            self.MergeCondition(GAME_CONDITION_WAIT_AFTER_ATTACK)
                            self.parent.PlaySound(SOUND_TYPE_GAME, 'kill')
                    elif event.type == GAME_EVENT_LEAVE_GAME:
                        log.debug('Enemy leave the Game.')
                        self.parent.AddNotification(self.parent.Language.PlayGameEnemyDisconnected)
                        self.MergeCondition(GAME_CONDITION_WIN)
                    elif event.type == GAME_EVENT_END:
                        self.Event(GAME_EVENT_END, {})
                        self.Send()
                        self.socket_activated = False
                        if self.Ships.SumShipsCount():
                            self.MergeCondition(GAME_CONDITION_WIN)
                        else:
                            self.MergeCondition(GAME_CONDITION_LOSE)
                if self._activate_enemy and self._recv_dict['condition'] > GAME_CONDITION_BUILD:
                    if not any(self.EnemyShips.ships.values()):
                        self.Send('SYNC.')
            except socket.timeout:
                self.Send('PING!.')
                self.socket.settimeout(GAME_EXTRA_PING_DELAY)
            except ConnectionResetError:
                log.debug('Enemy leave the Game.')
                self.parent.AddNotification(self.parent.Language.PlayGameEnemyDisconnected)
                self.MergeCondition(GAME_CONDITION_WIN)
            except UnicodeError:
                log.warning(f'UDP socket received unknown data: {data}.')
            except Exception as err:
                log.critical(err, stack_info=True, exc_info=True)
                self.parent.Report(err)
                self.Event(GAME_EVENT_LEAVE_GAME, {})

    def MergeCondition(self, condition):
        if condition != self.condition:
            log.debug(f'New condition: {condition}')
            self.parent.Foreground()
            self.condition = condition

    def Send(self, text=''):
        if text:
            self.socket.sendto(str(text).encode(), (self.enemy_host, self.enemy_port))
            return
        self._send_dict = {
            'ships': self.Ships.ships,
            'ships_count': self.Ships.ships_count,
            'die_ships': self.Ships.die_ships,
            'die_ships_count': self.Ships.die_ships_count,
            'die_blocks': self.Ships.die_blocks,
            'attacked_blocks': self.attacked_blocks,
            'condition': self.condition,
            'events': self.events,
            'count': self.send_messages
        }
        self.socket.sendto(str(self._send_dict).encode(), (self.enemy_host, self.enemy_port))
        if any(map(lambda e: e['type'] == GAME_EVENT_LEAVE_GAME, self._send_dict['events'])):
            self.EndGameButtonQuit.Function()
        self.events = []
        self.send_messages += 1

    def Event(self, event_type, dict_for_events: dict):
        event = {'type': event_type}
        event.update(zip(dict_for_events.keys(), dict_for_events.values()))
        log.debug(f'New event: {event}, condition: {self.condition}')
        self.events.append(event)

    def inBuild(self):
        if not self._random_place:
            self.BuildElements.update()
            self.BuildElements.draw(self.image)
        self.Ships.draw(self.image)
        if self.selected:
            if self.Ships.GetImaginaryShipStartCord():
                if self.Ships.GetImaginaryShipStartCord() != self.Ships.GetImaginaryShipEndCord() and not self._random_place:
                    if self.Ships.GetImaginaryShipDirection():
                        self.parent.cursor = pygame.SYSTEM_CURSOR_SIZENS
                    else:
                        self.parent.cursor = pygame.SYSTEM_CURSOR_SIZEWE
                if not self.Blocks.GetRect(self.selected).colliderect(
                        self.Blocks.GetShip(self.Ships.GetImaginaryShipCords())):
                    self.Ships.DrawShip((self.selected, self.selected), self.image, (0, 255, 0))
            else:
                self.parent.cursor = False
                if self.Ships.CollideShipEnv((self.selected, self.selected)):
                    if self.Ships.CollideShip((self.selected, self.selected)):
                        pass
                    else:
                        self.Ships.DrawShip((self.selected, self.selected), self.image, (255, 0, 0))
                else:
                    self.Ships.DrawShip((self.selected, self.selected), self.image, (0, 255, 0))
        if self.ClearMap.isCollide() and self.parent.mouse_left_release:
            log.debug('Clearing map.')
            self.ClearMap.Function()
        elif self.RandomPlacing.isCollide() and self.parent.mouse_left_release:
            self.RandomPlacing.Function()
            log.debug('Random placing.')
            self._random_place = True
        if self._random_place:
            if self.Ships.SumShipsMaxCount == self.Ships.SumShipsCount():
                self.MergeCondition(GAME_CONDITION_WAIT_AFTER_BUILD)
                self._activate_press = False
                log.debug('All is built by random.')
        elif self._activate_press:
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
                    log.debug(f'Start build ship, Start cord: {self.Ships.GetImaginaryShipStartCord()}.')
        else:
            if self.Ships.GetImaginaryShipStartCord() and self.Ships.GetImaginaryShipCords():
                log.debug(f'End build ship, End cord: {self.Ships.GetImaginaryShipEndCord()}, is hor direction: {self.Ships.GetImaginaryShipDirection()}, len: {self.Ships.GetImaginaryShipLen()}')
                error = self.Ships.EndBuildShip()
                if error:
                    log.debug(f'Error in build, error type: {error.type}.')
                    if error.type == 'rule':
                        self.parent.AddNotification(self.parent.Language.PlayGameRule.format(value=error.value))
                    elif error.type == 'count':
                        self.parent.AddNotification(self.parent.Language.PlayGameCount.format(value=error.value))
                    elif error.type == 'len':
                        self.parent.AddNotification(self.parent.Language.PlayGameLen.format(value=error.value))
                elif self.Ships.SumShipsMaxCount == self.Ships.SumShipsCount():
                    log.debug('All is built.')
                    self.MergeCondition(GAME_CONDITION_WAIT_AFTER_BUILD)

    def inGame(self):
        if self.condition == GAME_CONDITION_ATTACK:
            if not self._keyboard_input and self.selected:
                self.parent.cursor = False
            self.MoveLabel.value = self.parent.Language.PlayGameAttackBySelf
            self.MoveLabel.text_color = (200, 50, 100)
            self.MoveLabel.text_color_active = (200, 50, 100)
            self.EnemyShips.draw(self.image, alive=False)
            if self.selected:
                if self.EnemyShips.CollideDieShipEnv((self.selected, self.selected)):
                    if self.EnemyShips.CollideDieShip((self.selected, self.selected)):
                        self.parent.cursor = pygame.SYSTEM_CURSOR_NO
                    else:
                        self.Ships.DrawShip((self.selected, self.selected), self.image, (255, 255, 0))
                else:
                    self.Ships.DrawShip((self.selected, self.selected), self.image, (0, 255, 0))
            for point in self.attacked_blocks:
                if point not in self.EnemyShips.die_blocks:
                    pygame.draw.circle(self.image, (100, 100, 100), self.Ships.blocks.GetRect(point).center, self.Ships.blocks.block_size * 0.1)
            if self._activate_release:
                if self.selected and self.selected not in self.attacked_blocks:
                    self.attacked_blocks.append(self.selected)
                    result = self.EnemyShips.KillBlock(self.selected)
                    log.debug(f'Attached block {self.selected}.')
                    self.Event(GAME_EVENT_ATTACK, {'block': self.selected})
                    if result is None:
                        log.debug('attack is failed.')
                        self.parent.PlaySound(SOUND_TYPE_GAME, 'miss')
                        self.MergeCondition(GAME_CONDITION_WAIT_AFTER_ATTACK)
                    elif type(result) is int:
                        pass
                    else:
                        if result:
                            log.debug('Killed by attack.')
                            self.parent.PlaySound(SOUND_TYPE_GAME, 'kill')
                            if self.EnemyShips.SumShipsMaxCount == self.EnemyShips.SumDieShipCount():
                                self.Event(GAME_EVENT_END, {})
                        else:
                            log.debug('Wounded by attack.')
                            self.parent.PlaySound(SOUND_TYPE_GAME, 'wound')
                    self.Send()
        elif self.condition == GAME_CONDITION_WAIT_AFTER_ATTACK:
            if not self._keyboard_input and self.selected:
                self.parent.cursor = False
            self.MoveLabel.value = self.parent.Language.PlayGameAttackByNotSelf
            self.MoveLabel.text_color = (100, 50, 200)
            self.MoveLabel.text_color_active = (100, 50, 200)
            if self.selected:
                if self.Ships.CollideShip((self.selected, self.selected)):
                    if not self._keyboard_input:
                        self.parent.cursor = pygame.SYSTEM_CURSOR_CROSSHAIR
                else:
                    self.Ships.DrawShip((self.selected, self.selected), self.image, (255, 0, 0))
            for point in self._recv_dict['attacked_blocks']:
                if point not in self.Ships.die_blocks:
                    pygame.draw.circle(self.image, (255, 0, 0), self.Ships.blocks.GetRect(point).center, self.Ships.blocks.block_size * 0.1)
            self.Ships.draw(self.image)

    def inEnd(self):
        self.EndGameElements.update()
        self.EndGameElements.draw(self.image)
        if self.condition == GAME_CONDITION_WIN:
            self.EndGameLabel.value = self.parent.Language.PlayGameWin
            self.EndGameLabel.text_color = (100, 200, 255)
            self.EndGameLabel.text_color_active = (100, 100, 255)
        elif self.condition == GAME_CONDITION_LOSE:
            self.EndGameLabel.value = self.parent.Language.PlayGameLose
            self.EndGameLabel.text_color = (200, 200, 100)
            self.EndGameLabel.text_color_active = (200, 100, 155)
        if self.EndGameButtonQuit.isCollide() and self.parent.mouse_left_release:
            self.EndGameButtonQuit.Function()

    def update(self, active, args):
        if not active:
            return self.image
        self._activate_press = self.parent.mouse_left_press
        self._activate_release = self.parent.mouse_left_release
        for e in self.parent.events:
            if e.type == pygame.QUIT:
                self.Event(GAME_EVENT_LEAVE_GAME, {})
                break
        for event in self.parent.events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_SPACE):
                    self._activate_press = True
                    self._activate_release = False
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
                    self._activate_release = True
        if self._keyboard_input and self.parent.mouse_left_press:
            self._keyboard_input = False
        self.image.fill(self.parent.Colors.Background)
        self.selected = self.Blocks.GetCollide()
        self.GameElements.update()
        self.GameElements.draw(self.image)
        if self._keyboard_input:
            self.selected = self._keyboard_input
        if self.condition == GAME_CONDITION_WAIT:
            self.MoveLabel.value = self.parent.Language.PlayGameWaitEnemy
            if self.socket_activated:
                self.MergeCondition(GAME_CONDITION_BUILD)
        elif self.condition == GAME_CONDITION_BUILD:
            self.MoveLabel.value = self.parent.Language.PlayGameBuild
            self.DrawLines()
            self.inBuild()
        elif self.condition == GAME_CONDITION_WAIT_AFTER_BUILD:
            self.MoveLabel.value = self.parent.Language.PlayGameWait
            self.DrawLines()
            self.Ships.draw(self.image)
            self.parent.cursor = False
            if not self.send_messages:
                self.Send()
            if self.EnemyShips.SumShipsCount():
                if self._activate < self._activate_enemy:
                    self.MergeCondition(GAME_CONDITION_ATTACK)
                else:
                    self.MergeCondition(GAME_CONDITION_WAIT_AFTER_ATTACK)
        elif any(map(lambda cond: cond == self.condition, (GAME_CONDITION_ATTACK, GAME_CONDITION_WAIT_AFTER_ATTACK))):
            self.DrawLines()
            if self.EnemyShips.SumShipsMaxCount:
                self.inGame()
            if not self.recv_thread.is_alive():
                self.recv_thread = threading.Thread(target=self._socket_recv, daemon=True)
                self.recv_thread.start()
        elif any(map(lambda cond: cond == self.condition, (GAME_CONDITION_LOSE, GAME_CONDITION_WIN))):
            self.MoveLabel.value = ''
            self.inEnd()
        return self.image
