from functions import *
from Gui import *


def StartGame(self: TextInput):
    split = self.value.replace('/', '').split(':')
    lnk = False
    if 'dummy' in self.value:
        enemy = ('', 0)
        lnk = self.parent.around_nat_socket
    elif '||' not in self.value:
        try:
            if self.value.count(':') > 1:
                socket.inet_pton(socket.AF_INET6, split[:-1])
                enemy = (':'.join(split[:-1]), int(split[-1]))
            elif self.value.count(':'):
                socket.inet_pton(socket.AF_INET, split[0])
                enemy = (split[0], int(split[1]))
            else:
                raise Exception
        except Exception:
            self.Activate()
            self.parent.ConditionLabel.value = self.parent.parent.Language.CreateGameWrongIP
            return
    else:
        enemy = (':'.join(split[:-1]), int(split[-1]))
    log.debug(f'Start game, enemy addr: {enemy}, inputted value: {self.value}.')
    self.parent.ConditionLabel.value = self.parent.parent.Language.CreateGameConnect
    self.parent.parent.SetScene(PLAY, socket=self.parent.socket, enemy=enemy, link=lnk)


def _GetIP(ip_button, link_button):
    link_button.parent.around_nat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    link_button.parent.around_nat_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    log.debug('Connect to TCP server.')
    while True:
        try:
            link_button.parent.around_nat_socket.connect((AROUND_NAT_SERVER_IP, AROUND_NAT_SERVER_PORT))
            break
        except ConnectionRefusedError:
            pass
    log.debug('Connected to TCP server.')
    link_button.parent.around_nat_socket.send('mine.'.encode())
    ip_button.external_tcp_ip, ip_button.external_tcp_port = link_button.external_tcp_ip, link_button.external_tcp_port = GetIpFromString(link_button.parent.around_nat_socket.recv(1024).decode())
    log.debug(f'external tcp addr: {GetIpFromTuple((ip_button.external_tcp_ip, ip_button.external_tcp_port))}.')
    st_tm = ip_button.parent.socket.gettimeout()
    ip_button.parent.socket.shutdown(0)
    ip_button.parent.socket.close()
    while ip_button.parent.parent.RUN:
        ip_button.parent.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_button.parent.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ip_button.parent.socket.bind((ip_button.parent.source_ip, ip_button.parent.source_port))
        ip_button.parent.socket.settimeout(0.1)
        nat = stun.get_nat_type(ip_button.parent.socket, ip_button.parent.source_ip, ip_button.parent.source_port, stun_host='stun.l.google.com', stun_port=19302)[1]
        if nat['ExternalIP']:
            ip_button.external_ip = nat['ExternalIP']
            ip_button.external_port = nat['ExternalPort']
            ip_button.text = ip_button.parent.parent.Language.CreateGameYouIP.format(ip=ip_button.external_ip,
                                                                                     port=ip_button.external_port)
            ip_button.text_active = ip_button.parent.parent.Language.CreateGameYouIP.format(ip=ip_button.external_ip,
                                                                                            port=ip_button.external_port)

            link_button.external_ip = nat['ExternalIP']
            link_button.external_port = nat['ExternalPort']
            link_button.text = link_button.parent.parent.Language.CreateGameYouLink
            link_button.text_active = link_button.parent.parent.Language.CreateGameYouLink
            link_button.UpdateImage()
            ip_button.UpdateImage()
            ip_button.parent.socket.settimeout(st_tm)
            log.debug(f'external udp addr: {GetIpFromTuple((ip_button.external_ip, ip_button.external_port))}.')
            log.debug(f'hosted udp addr: {GetIpFromTuple((ip_button.parent.source_ip, ip_button.parent.source_port))}.')
            return
        else:
            ip_button.parent.source_port += 1
            link_button.parent.source_port += 1
            ip_button.parent.socket.shutdown(0)
            ip_button.parent.socket.close()


def CopyIpToClipboard(self, link):
    if hasattr(self, 'external_ip'):
        text = f'{self.external_ip}:{self.external_port}'
        if link:
            text = f'{GITHUB_PAGE_URL}?{API_METHOD_CONNECT}={self.external_tcp_ip}:{self.external_tcp_port}|{text}'
            self.parent.parent.AddNotification(self.parent.parent.Language.CreateGameYouLinkCopied)
            self.parent.Input.value = 'dummy'
            self.parent.Input.Deactivate()
        else:
            self.parent.parent.AddNotification(self.parent.parent.Language.CreateGameYouIPCopied)
        log.debug(f'Copied text:$BOLD$GREEN\t{text}$RESET.\tButton value:{self.parent.Input.value}.')
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode())


def EscActivate(self, **kwargs):
    self.parent.socket.shutdown(0)
    self.parent.around_nat_socket.shutdown(0)
    self.parent.around_nat_socket.close()
    self.parent.socket.close()
    log.debug(f'Close scene {self.parent.type}, args:{kwargs}, socket: {self.parent.socket}.')
    self.parent.parent.SetScene(self.parent.InputScene, *kwargs)
    self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')


class CreateGame:
    def __init__(self, parent, input_scene, kwargs):
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        log.debug(f'New Scene: {self.type}, last {self.InputScene}, dict:{kwargs}.')

        self.source_ip = GAME_HOST
        self.source_port = GAME_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.source_ip, self.source_port))
        self.socket.settimeout(0.01)
        log.debug(f'Created socket: {self.socket}')

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
        threading.Thread(target=_GetIP, args=[self.MyIpButton, self.MyLinkButton], daemon=True).start()
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

