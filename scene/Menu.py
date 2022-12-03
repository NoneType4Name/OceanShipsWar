from Gui import *
import threading


class MainScene:
    def __init__(self, parent, input_scene=INIT, kwargs=None):
        self.UpdateThread = threading.Thread(target=lambda: False)
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)

        rect_w, rect_h = parent.block_size * 2, parent.block_size * 0.5
        border = rect_h * BORDER_ATTITUDE
        border = border if border > DEFAULT_BORDER else DEFAULT_BORDER
        border_active = rect_h * BORDER_ACTIVE_ATTITUDE
        border_active = border_active if border_active > DEFAULT_BORDER else DEFAULT_BORDER
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.ButtonUpdate = Button(self,
                                   (-1, parent.size.h - parent.block_size * 0.5,
                                    rect_w, rect_h),
                                   text_rect, text_rect,
                                   parent.Language.Version.format(version=self.parent.VERSION),
                                   parent.Language.Version.format(version=self.parent.VERSION), *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)

        rect_w, rect_h = parent.size.w * 0.24, parent.size.h * 0.15
        border = rect_h * BORDER_ATTITUDE * 2
        border = border if border > DEFAULT_BORDER else DEFAULT_BORDER
        border_active = rect_h * BORDER_ACTIVE_ATTITUDE * 1.3
        border_active = border_active if border_active > DEFAULT_BORDER else DEFAULT_BORDER
        text_rect = (border * 2, border, rect_w - border * 2, rect_h - border * 2)
        text_rect_active = (border_active, border_active, rect_w - border_active * 2, rect_h - border_active * 2)
        self.ButtonCreateGame = Button(self,
                                       (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.4 - rect_h * 0.5,
                                        rect_w, rect_h),
                                       text_rect, text_rect_active,
                                       parent.Language.StartGame, parent.Language.StartGame, *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)
        self.ButtonSettings = Button(self,
                                     (parent.size.w * 0.5 - rect_w * 0.5, parent.size.h * 0.6 - rect_h * 0.5,
                                         rect_w, rect_h),
                                     text_rect, text_rect_active,
                                     parent.Language.Settings, parent.Language.Settings, *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)

        rect_w, rect_h = parent.block_size, parent.block_size
        border = rect_h * BORDER_ATTITUDE
        border = border if border > DEFAULT_BORDER else DEFAULT_BORDER
        border_active = rect_h * BORDER_ACTIVE_ATTITUDE
        border_active = border_active if border_active > DEFAULT_BORDER else DEFAULT_BORDER
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        text_rect_active = (border_active, border_active, rect_w - border_active * 2, rect_h - border_active * 2)
        # self.ButtonTheme = Button(self,
        #     (parent.size.w - parent.block_size * 1.5, parent.size.h - parent.block_size * 1.5,
        #      rect_w, rect_h),
        #     text_rect, text_rect,
        #     parent.Language.ThemeLight if parent.Settings.Graphic.Theme is THEME_LIGHT else parent.Language.ThemeDark,
        #     parent.Language.ThemeLight if parent.Settings.Graphic.Theme is THEME_LIGHT else parent.Language.ThemeDark,
        #     *parent.Colors.Scene.Main.Button, border=border, border_active=border)
        self.ButtonQuit = Button(self,
            (parent.size.w - parent.block_size + 1, -1,
             rect_w, rect_h),
            text_rect, text_rect_active,
            parent.Language.Exit, parent.Language.Exit,
            *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)

        self.Elements = pygame.sprite.Group(self.ButtonUpdate, self.ButtonCreateGame, self.ButtonSettings, self.ButtonQuit)

    def update(self, active, *args):
        if active:
            self.image.fill(self.parent.Colors.Background)
            self.Elements.update()
            self.Elements.draw(self.image)
            if self.parent.mouse_left_release:
                if self.ButtonUpdate.isCollide():
                    if not self.UpdateThread.is_alive():
                        self.parent.PlaySound(SOUND_TYPE_GAME, 'select')
                        self.UpdateThread = threading.Thread(target=self.parent.GetUpdate, daemon=True)
                        self.UpdateThread.start()
                    else:
                        self.parent.PlaySound(SOUND_TYPE_GAME, 'denied')
                elif self.ButtonCreateGame.isCollide():
                    self.parent.SetScene(CREATE)
                    self.parent.PlaySound(SOUND_TYPE_GAME, 'select')
                    self.parent.PlaySound(SOUND_TYPE_GAME, 'select')
                elif self.ButtonSettings.isCollide():
                    self.parent.SetScene(SETTINGS)
                    self.parent.PlaySound(SOUND_TYPE_GAME, 'select')
                elif self.ButtonQuit.isCollide():
                    self.parent.RUN = False
        return self.image
