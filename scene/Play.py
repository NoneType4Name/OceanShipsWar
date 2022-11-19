import time

from functions import *
from Gui import *
from Game import Game


class Blocks(DATA):
    def __init__(self, w_h: int, left_margin, upper_margin, block_size):
        blocks = {}
        for num_let in range(w_h):
            blocks[str(num_let)] = []
            for num in range(w_h):
                blocks[str(num_let)].append(
                    pygame.Rect(left_margin + num_let * block_size, upper_margin + num * block_size, block_size,
                                block_size))
        self.blocks = blocks
        super().__init__(self.blocks)


class PlayGame:
    def __init__(self, parent :Game, enemy:(str, int), **kwargs):
        self.type = PLAY
        self.parent = parent
        if kwargs.get('demo'):
            self.host = ''
            self.port = 0
        else:
            self.host = enemy[0]
            self.port = enemy[1]
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.image.fill(self.parent.Colors.Background)
        self.Lines = None
        self.Blocks = Blocks(10, (self.parent.size.w * 0.5 - self.parent.block_size * 5), (self.parent.size.h * 0.5 - self.parent.block_size * 5), self.parent.block_size)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', 61023))
        # nat = stun.get_nat_type(self.socket, '0.0.0.0', 61023, stun_host='stun.l.google.com', stun_port=19302)[1]
        # self.my_ip = nat['ExternalIP']
        # self.my_port = nat['ExternalPort']
        # print(self.my_ip, self.my_port, time.time() - s)

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

    # def GetData(self):
    #     self.

    def update(self, active, args):
        self.image.fill(self.parent.Colors.Background)
        self.DrawLines()
        return self.image


sz = (920, 540)


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


G = PlayGame(Exemplar(), (), demo=True)

pygame.init()
screen = pygame.display.set_mode(sz, pygame.SRCALPHA)
c = pygame.time.Clock()
run = True
while run:
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
    screen.blit(G.update(True, ev), (0, 0))
    pygame.display.flip()
    c.tick(60)



