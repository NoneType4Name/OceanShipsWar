from Gui import *


class CreateGame:
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
        self.Input = TextInput(self, (parent.size.w * 0.4, parent.size.h * 0.4, parent.size.w * 0.2,parent.size.h * 0.1),
                               parent.size.h * 0.01, 0.5, parent.Colors.Background, parent.Colors.Lines, (100, 0, 255, 100), 'white IP address')
        self.Elements = pygame.sprite.Group(self.ButtonEsc)

    def update(self, active, events):
        if active:
            self.image.fill(self.parent.Colors.Background)
            self.Input.update(events)
            self.Elements.update()
            for event in events:
                if event.key == pygame.K_ESCAPE:
                    self.ButtonEsc.Function()

            self.image.blit(self.Input.image, self.Input.rect.topleft)
            self.Elements.draw(self.image)
            if self.parent.mouse_left_release:
                if self.Input.isCollide():
                    if not self.Input.active:
                        self.Input.Activate()

                elif not self.Input.isCollide() and self.Input.active:
                    self.Input.return_value = True

                elif self.ButtonEsc.isCollide():
                    self.ButtonEsc.Function()

            if self.Input.return_value:
                self.Input.Deactivate()
                print(self.Input.value)

        return self.image

