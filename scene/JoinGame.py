from functions import *
from Gui import *


def IO(self):
    if ' ' not in self.value:
        print(self.value)
    else:
        self.Activate()


class JoinGame:
    def __init__(self, parent, input_scene, kwargs=None):
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
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
                                'ESC', 'ESC', *parent.Colors.Scene.Main.Button, border=border, border_active=border_active,
                                func=[EscActivate, self])
        rect_w, rect_h = parent.size.w * 0.2, parent.size.h * 0.1
        border = parent.size.h * 0.01
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.Input = TextInput(self, (parent.size.w * 0.4, parent.size.h * 0.4, rect_w, rect_h),
                               text_rect,
                               'White IP address',
                               '',
                               0.5,
                               *self.parent.Colors.TextInput,
                               border=border,
                               border_active=border,
                               radius=0.5,
                               radius_active=0.5,
                               func_deactivate=IO)
        self.Input.Activate()
        self.Elements = pygame.sprite.Group(self.ButtonEsc)

    def update(self, active, *args):
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

        return self.image

