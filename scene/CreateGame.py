import threading

from functions import *
from Gui import *


def IO(self):
    if ':' in self.value:
        self.parent.enemy_addr = self.value
        self.parent.ConditionLabel.value = self.parent.enemy_addr
    else:
        self.Activate()


def GetIP(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((self.source_ip, self.source_port))
    sock.settimeout(0.1)

    nat = stun.get_nat_type(sock, self.source_ip, self.source_port, stun_host='stun.l.google.com', stun_port=19302)[1]
    sock.close()
    if nat['ExternalIP']:
        self.external_ip = nat['ExternalIP']
        self.external_port = nat['ExternalPort']
        self.value = f'Ваш IP адрес:{self.external_ip}:{self.external_port}'
    else:
        self.source_port += 1
        GetIP([self])


def CopyIpToClipboard(self):
    text = ':'.join(self.value.split(':')[-2:])
    if ':' in self.value:
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode())
    self.parent.parent.AddNotification('IP address was copied to clipboard!.')


class CreateGame:
    def __init__(self, parent, input_scene, kwargs=None):
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
        self.enemy_addr = None
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)

        rect_w, rect_h = parent.block_size * 0.75, parent.block_size * 0.5
        border = rect_h * BORDER_ATTITUDE
        border = border if border > DEFAULT_BORDER else DEFAULT_BORDER
        border_active = rect_h * BORDER_ACTIVE_ATTITUDE
        border_active = border_active if border_active > DEFAULT_BORDER else DEFAULT_BORDER
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        text_rect_active = (border_active, border_active, rect_w - border_active * 2, rect_h - border_active * 2)
        self.ButtonEsc = Button(self,
                                (-1, -1,
                                 rect_w, rect_h),
                                text_rect, text_rect_active,
                                'ESC', 'ESC', *parent.Colors.Scene.Main.Button,
                                border=border, border_active=border_active,
                                func=[EscActivate, self])

        rect_w, rect_h = parent.size.w * 0.2, parent.size.h * 0.1
        border = parent.size.h * 0.01
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.MyIpLabel = Label(self, (parent.size.w * 0.4, parent.size.h * 0.6, rect_w * 0.5, rect_h * 0.5),
                               (parent.size.w * 0.4 + border, parent.size.h * 0.6 + border, rect_w * 0.5 - border * 2, rect_h * 0.5 - border * 2),
                               0.5,
                               'Загрузка...',
                               *parent.Colors.Label,
                               border=border, border_active=border_active, radius=1, radius_active=1,
                               func=CopyIpToClipboard
                               )
        self.ConditionLabel = Label(self, (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.9, rect_w, rect_h * 0.5),
                                    (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.9, rect_w, rect_h * 0.5),
                                    0.5,
                                    '',
                                    *parent.Colors.Scene.Load.Label
                                    )
        self.MyIpLabel.source_ip, self.MyIpLabel.source_port = '0.0.0.0', 9997
        threading.Thread(target=GetIP, args=[self.MyIpLabel]).start()
        self.Input = TextInput(self, (parent.size.w * 0.4, parent.size.h * 0.4, rect_w, rect_h),
                               text_rect,
                               'IP address:port',
                               '',
                               0.5,
                               *self.parent.Colors.TextInput,
                               border=border,
                               border_active=border,
                               radius=0.5,
                               radius_active=0.5,
                               func_deactivate=IO)
        self.Input.Activate()
        self.Elements = pygame.sprite.Group(self.ButtonEsc, self.MyIpLabel, self.ConditionLabel)

    def update(self, active, args):
        if active:
            self.image.fill(self.parent.Colors.Background)
            self.Elements.update()
            self.Input.update(self.parent.events)
            for event in self.parent.events:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.ButtonEsc.Function()

            self.image.blit(self.Input.image, self.Input.rect.topleft)
            self.Elements.draw(self.image)
            if self.parent.mouse_left_release:
                if self.ButtonEsc.isCollide():
                    self.ButtonEsc.Function()

                elif self.Input.isCollide() and not self.Input.active:
                    self.Input.Activate()

                elif not self.Input.isCollide() and self.Input.active:
                    self.Input.Deactivate()

                if self.MyIpLabel.isCollide():
                    self.MyIpLabel.Function()

        return self.image

