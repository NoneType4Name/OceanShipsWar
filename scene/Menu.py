import pygame

from Gui import *
import threading


class MainScene:
    def __init__(self, parent, input_scene=INIT, kwargs=None):
        self.UpdateThread = threading.Thread(target=lambda: False)
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.Events = []
        default_border = 2
        border_atr = 0.1
        border_active_atr = 0.2

        rect_w, rect_h = parent.block_size * 2, parent.block_size * 0.5
        border = rect_h * border_atr
        border = border if border > default_border else default_border
        border_active = rect_h * border_active_atr
        border_active = border_active if border_active > default_border else default_border
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        self.ButtonUpdate = Button(self,
                                   (-1, parent.size.h - parent.block_size * 0.5,
                                    rect_w, rect_h),
                                   text_rect, text_rect,
                                   parent.Language.DefaultDict.Version, parent.Language.DefaultDict.Version, *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)
        rect_w, rect_h = parent.block_size * 0.75, parent.block_size * 0.5
        border = rect_h * border_atr
        border = border if border > default_border else default_border
        border_active = rect_h * border_active_atr
        border_active = border_active if border_active > default_border else default_border
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        text_rect_active = (border_active, border_active, rect_w - border_active * 2, rect_h - border_active * 2)
        self.ButtonEsc = Button(self,
                                (-1, -1,
                                 rect_w, rect_h),
                                text_rect, text_rect_active,
                                'ESC', 'ESC', *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)

        rect_w, rect_h = parent.size.w * 0.16, parent.size.h * 0.1
        border = rect_h * border_atr
        border = border if border > default_border else default_border
        border_active = rect_h * border_active_atr
        border_active = border_active if border_active > default_border else default_border
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        text_rect_active = (border_active, border_active, rect_w - border_active * 2, rect_h - border_active * 2)
        self.ButtonCreateGame = Button(self,
            (parent.size.w * 0.42, parent.size.h * 0.2,
             rect_w, rect_h),
            text_rect, text_rect_active,
            parent.Language.DefaultDict.StartGame, parent.Language.DefaultDict.StartGame, *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)
        self.ButtonJoinGame = Button(self,
            (parent.size.w * 0.42, parent.size.h * 0.4,
             rect_w, rect_h),
            text_rect, text_rect_active,
            parent.Language.DefaultDict.JoinGame, parent.Language.DefaultDict.JoinGame,  *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)
        self.ButtonSettings = Button(self,
            (parent.size.w * 0.42, parent.size.h * 0.6,
             rect_w, rect_h),
            text_rect, text_rect_active,
            parent.Language.DefaultDict.Settings, parent.Language.DefaultDict.Settings, *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)

        rect_w, rect_h = parent.block_size, parent.block_size
        border = rect_h * border_atr
        border = border if border > default_border else default_border
        border_active = rect_h * border_active_atr
        border_active = border_active if border_active > default_border else default_border
        text_rect = (border, border, rect_w - border * 2, rect_h - border * 2)
        text_rect_active = (border_active, border_active, rect_w - border_active * 2, rect_h - border_active * 2)
        self.ButtonTheme = Button(self,
            (parent.size.w - parent.block_size * 1.5, parent.size.h - parent.block_size * 1.5,
             rect_w, rect_h),
            text_rect, text_rect,
            parent.Language.DefaultDict.ThemeLight if parent.Settings.Graphic.Theme is THEME_LIGHT else parent.Language.DefaultDict.ThemeDark,
            parent.Language.DefaultDict.ThemeLight if parent.Settings.Graphic.Theme is THEME_LIGHT else parent.Language.DefaultDict.ThemeDark,
            *parent.Colors.Scene.Main.Button, border=border, border_active=border)
        self.ButtonQuit = Button(self,
            (parent.size.w - parent.block_size + 1, -1,
             rect_w, rect_h),
            text_rect, text_rect_active,
            parent.Language.DefaultDict.Exit, parent.Language.DefaultDict.Exit,
            *parent.Colors.Scene.Main.Button, border=border, border_active=border_active)

        self.Elements = pygame.sprite.Group(self.ButtonUpdate, self.ButtonEsc, self.ButtonCreateGame, self.ButtonJoinGame,
                                            self.ButtonSettings, self.ButtonTheme, self.ButtonQuit)

    def update(self, event=False):
        self.image.fill(self.parent.Colors.Background)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.Elements.update()
        self.Elements.draw(self.image)
        if event:
            if self.parent.mouse_left_release:
                if self.ButtonUpdate.isCollide():
                    if not self.UpdateThread.is_alive():
                        self.PlaySound(SOUND_TYPE_GAME, 'select')
                        self.UpdateThread = threading.Thread(target=self.parent.GetUpdate)
                        self.UpdateThread.start()
                    else:
                        self.PlaySound(SOUND_TYPE_GAME, 'denied')
                elif self.ButtonEsc.isCollide():
                    pass
                elif self.ButtonCreateGame.isCollide():
                    pass
                elif self.ButtonJoinGame.isCollide():
                    pass
                elif self.ButtonSettings.isCollide():
                    pass
                elif self.ButtonTheme.isCollide():
                    pass
                elif self.ButtonQuit.isCollide():
                    self.parent.RUN = False
        return self.image

    def PlaySound(self, sound_type, sound_name, loops=0, maxtime=0, fade_ms=0):
        self.parent.PlaySound(sound_type, sound_name, loops, maxtime, fade_ms)
