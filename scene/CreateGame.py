from functions import *
from Gui import *


def StartGame(self: TextInput):
    split = self.value.replace('/', '').split(':')
    if '/' not in self.value:
        try:
            if self.value.count(':') > 1:
                socket.inet_pton(socket.AF_INET6, split[:-1])
                enemy = (':'.join(split[:-1]), int(split[-1]))
            elif self.value.count(':'):
                socket.inet_pton(socket.AF_INET, split[0])
                enemy = (split[0], int(split[1]))
            else:
                raise OSError
        except OSError:
            self.Activate()
            self.parent.ConditionLabel.value = self.parent.parent.Language.CreateGameWrongIP
            return
    else:
        enemy = (':'.join(split[:-1]), int(split[-1]))
    self.parent.ConditionLabel.value = self.parent.parent.Language.CreateGameConnect
    self.parent.parent.SetScene(PLAY, socket=self.parent.socket, enemy=enemy)


def _GetIP(self, link):
    nat = stun.get_nat_type(self.parent.socket, self.parent.source_ip, self.parent.source_port, stun_host='stun.l.google.com', stun_port=19302)[1]
    if nat['ExternalIP']:
        self.external_ip = nat['ExternalIP']
        self.external_port = nat['ExternalPort']
        if link:
            self.text = self.parent.parent.Language.CreateGameYouLink
            self.text_active = self.parent.parent.Language.CreateGameYouLink
        else:
            self.text = self.parent.parent.Language.CreateGameYouIP.format(ip=self.external_ip,
                                                                           port=self.external_port)
            self.text_active = self.parent.parent.Language.CreateGameYouIP.format(ip=self.external_ip,
                                                                                  port=self.external_port)
        self.UpdateImage()
        return
    while self.parent.parent.RUN:
        self.parent.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.parent.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.parent.socket.bind((self.parent.source_ip, self.parent.source_port))
        self.parent.socket.settimeout(0.01)
        nat = stun.get_nat_type(self.parent.socket, self.parent.source_ip, self.parent.source_port, stun_host='stun.l.google.com', stun_port=19302)[1]
        if nat['ExternalIP']:
            self.external_ip = nat['ExternalIP']
            self.external_port = nat['ExternalPort']
            if link:
                self.text = self.parent.parent.Language.CreateGameYouLink
                self.text_active = self.parent.parent.Language.CreateGameYouLink
            else:
                self.text = self.parent.parent.Language.CreateGameYouIP.format(ip=self.external_ip,
                                                                               external_ipport=self.external_port)
                self.text_active = self.parent.parent.Language.CreateGameYouIP.format(ip=self.external_ip,
                                                                                      port=self.external_port)
            self.UpdateImage()
            return
        else:
            self.parent.source_port += 1
            self.parent.socket.close()


def CopyIpToClipboard(self, link):
    text = f'{self.external_ip}:{self.external_port}'
    if link:
        text = f'{GITHUB_PAGE_URL}?{API_METHOD_CONNECT}={text}'
    pygame.scrap.put(pygame.SCRAP_TEXT, text.encode())
    self.parent.parent.AddNotification(self.parent.parent.Language.CreateGameYouIPCopied)


def EscActivate(self, **kwargs):
    self.parent.socket.close()
    self.parent.parent.SetScene(self.parent.InputScene, *kwargs)
    self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')


class CreateGame:
    def __init__(self, parent, input_scene, kwargs):
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)

        self.source_ip = GAME_HOST
        self.source_port = GAME_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.source_ip, self.source_port))
        self.socket.settimeout(0.01)

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
                                self.parent.Language.Esc, self.parent.Language.Esc, *parent.Colors.Scene.Main.Button,
                                border=border, border_active=border_active,
                                func=EscActivate)

        rect_w, rect_h = parent.size.w * 0.2, parent.size.h * 0.1
        border = parent.size.h * 0.01
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.MyIpButton = Button(
            self,
            (parent.size.w * 0.4 - rect_w * 0.4, parent.size.h * 0.6 - rect_h * 0.25, rect_w * 0.8, rect_h * 0.5),
            (parent.size.w * 0.4 + border, parent.size.h * 0.6 + border, rect_w * 0.8 - border * 2, rect_h * 0.5 - border * 2),
            (parent.size.w * 0.4 + border, parent.size.h * 0.6 + border, rect_w * 0.8 - border * 2, rect_h * 0.5 - border * 2),
            self.parent.Language.CreateGameYouIPDefault,
            self.parent.Language.CreateGameYouIPDefault,
            *parent.Colors.Button,
            border=border, border_active=border_active, radius=1, radius_active=1,
            func=CopyIpToClipboard, args=[0]
            )
        self.MyLinkButton = Button(
            self,
            (parent.size.w * 0.6 - rect_w * 0.4, parent.size.h * 0.6 - rect_h * 0.25, rect_w * 0.8, rect_h * 0.5),
            (parent.size.w * 0.4 + border, parent.size.h * 0.6 + border, rect_w * 0.8 - border * 2, rect_h * 0.5 - border * 2),
            (parent.size.w * 0.4 + border, parent.size.h * 0.6 + border, rect_w * 0.8 - border * 2, rect_h * 0.5 - border * 2),
            self.parent.Language.CreateGameYouLinkDefault,
            self.parent.Language.CreateGameYouLinkDefault,
            *parent.Colors.Button,
            border=border, border_active=border_active, radius=1, radius_active=1,
            func=CopyIpToClipboard, args=[1]
            )
        self.ConditionLabel = Label(self, (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.9, rect_w, rect_h * 0.5),
                                    (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.9, rect_w, rect_h * 0.5),
                                    0.5,
                                    self.parent.Language.CreateGameConditionDefault,
                                    *parent.Colors.Scene.Load.Label
                                    )
        threading.Thread(target=_GetIP, args=[self.MyIpButton, 0]).start()
        threading.Thread(target=_GetIP, args=[self.MyLinkButton, 1]).start()
        self.Input = TextInput(self, (parent.size.w * 0.4, parent.size.h * 0.4, rect_w, rect_h),
                               text_rect,
                               self.parent.Language.CreateGameInputDefault,
                               '',
                               0.5,
                               *self.parent.Colors.TextInput,
                               border=border,
                               border_active=border,
                               radius=0.5,
                               radius_active=0.5,
                               func_deactivate=StartGame)
        self.Input.Activate()
        self.Elements = pygame.sprite.Group(self.ButtonEsc, self.MyIpButton, self.MyLinkButton, self.ConditionLabel)

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

                elif self.MyIpButton.isCollide():
                    self.MyIpButton.Function()
                elif self.MyLinkButton.isCollide():
                    self.MyLinkButton.Function()

                elif self.Input.isCollide() and not self.Input.active:
                    self.Input.Activate()

                elif not self.Input.isCollide() and self.Input.active:
                    self.Input.Deactivate()

        return self.image

