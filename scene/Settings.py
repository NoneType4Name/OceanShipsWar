import pygame.sprite

from Gui import *


def ButtonActivate(self, name, *args):
    if self.active_element == name:
        return
    self.active_element = name


def SlideValue(self):
    self.parent.parent.EditSettings(self.type_settings, self.name, self.value)
    self.parent.selected = self.name


def SlideDeactivate(self):
    self.parent.selected = None


def SwitchValue(self):
    self.parent.parent.EditSettings(self.type_settings, self.name, self.value)


def ListActivate(self):
    self.parent.selected = self.name


def ListDeactivate(self):
    self.parent.parent.EditSettings(self.type_settings, self.name, self.values[self.value])
    self.parent.selected = None


class Settings:
    def __init__(self, parent, input_scene, kwargs):
        self.type = SETTINGS
        self.parent = parent
        self.InputScene = input_scene
        self.image = pygame.Surface(self.parent.size, pygame.SRCALPHA)
        self.settings_elements = {}
        self.active_element = list(self.parent.Settings.keys())[0]
        self.selected = None

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
        self.elements = {'default':{None: pygame.sprite.Group(self.ButtonEsc)}}
        threading.Thread(target=self.LoadElements).start()

    def LoadElements(self):
        self.selected = None
        pad = SETTINGS_UPPER_MARGIN
        language = self.parent.Language.DefaultDict
        BaseRect = pygame.Rect(self.parent.size[0] * 0.24, self.parent.size[1] * pad, self.parent.size[0] * 0.52,
                               self.parent.size[1] * 0.027)
        for type_settings in self.parent.Settings:
            self.elements[type_settings] = pygame.sprite.Group()
            settings_elements = {}
            buttons_pad = pad = SETTINGS_UPPER_MARGIN
            self.elements['default'][type_settings] = pygame.sprite.Group()
            for _type_settings in self.parent.Settings:
                self.elements['default'][type_settings].add(Button(
                    self,
                    (self.parent.size[0] * 0.05, self.parent.size[1] * buttons_pad, BaseRect.h * 5, BaseRect.h),
                    (2, 2, BaseRect.h * 5 - 4, BaseRect.h - 4),
                    (2, 2, BaseRect.h * 5 - 4, BaseRect.h - 4),
                    language[_type_settings],
                    language[_type_settings],
                    *self.parent.Colors['ButtonActive' if type_settings == _type_settings else 'Button'], border=2, border_active=2, func=[ButtonActivate, self, _type_settings]))
                buttons_pad += BaseRect.h / self.parent.size[1] * 1.1
            for element in self.parent.Settings[type_settings]:
                BaseRect = pygame.Rect(self.parent.size[0] * 0.24, self.parent.size[1] * pad,
                                       self.parent.size[0] * 0.52, self.parent.size[1] * 0.027)
                settings_elements[element+'_label'] = Label(self, BaseRect, BaseRect, 0.15, language[type_settings+element],
                                                            *self.parent.Colors['Label'], border=1, border_active=1, radius=1, radius_active=1)
                if self.parent.Settings[type_settings][element]['type'] is Switch:
                    settings_elements[element] = Switch(self, (BaseRect.x + BaseRect.w - (BaseRect.h * 2 - BaseRect.h * 0.1) - 1, BaseRect.y + 1, BaseRect.h * 2 - BaseRect.h * 0.1, BaseRect.h - 2),
                                                        type_settings,
                                                        element,
                                                        self.parent.Settings[type_settings][element]['value'],
                                                        *self.parent.Colors['Switch'],
                                                        func=SwitchValue
                                                        )
                elif self.parent.Settings[type_settings][element]['type'] is List:
                    settings_elements[element] = List(self, (BaseRect.x + BaseRect.w - (BaseRect.h * 4 - BaseRect.h * 0.1) - 1, BaseRect.y + 1, BaseRect.h * 4 - BaseRect.h * 0.1, BaseRect.h - 2),
                                                      0.5,
                                                      list(self.parent.Settings[type_settings][element]['values'].values()),
                                                      list(self.parent.Settings[type_settings][element]['values'].keys()),
                                                      type_settings,
                                                      element,
                                                      list(self.parent.Settings[type_settings][element]['values'].keys()).index(self.parent.Settings[type_settings][element]['value']),
                                                      *self.parent.Colors['List'],
                                                      func_activate=ListActivate,
                                                      func_deactivate=ListDeactivate,
                                                      border=1, radius=1, border_active=1, radius_active=1)
                if self.parent.Settings[type_settings][element]['type'] is Slide:
                    settings_elements[element] = Slide(self, (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1, BaseRect.y + 1, (BaseRect.h - 2) * 10, BaseRect.h - 2),
                                                       0.5,
                                                       type_settings,
                                                       element,
                                                       self.parent.Settings[type_settings][element]['value'],
                                                       *self.parent.Colors['Slide'],
                                                       border=1,
                                                       border_active=1,
                                                       radius=1,
                                                       radius_active=1,
                                                       func_activate=SlideValue,
                                                       func_deactivate=SlideDeactivate)
                #     elif self.parent.Settings[type_settings][element]['type'] is Path:
                #         settings_elements[element] = Path(self.default_font,
                #                                      (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1,
                #                                       BaseRect.y + 1,
                #                                       (BaseRect.h - 2) * 10,
                #                                       BaseRect.h - 2),
                #                                      *set_of_settings['Path'], value=settings[type_settings][element],
                #                                      display=set_for_paths[element]['name'],
                #                                      name=f'{type_settings} {element}',
                #                                      multiple=set_for_paths[element]['multiple'],
                #                                      types=set_for_paths[element]['types'],
                #                                      typ=set_for_paths[element]['values'])
                #     else:
                #         print(type_settings, element, type(set_of_settings_type[type_settings][element]))
                #         raise Exception

                pad += BaseRect.h / self.parent.size[1] * 1.1
                self.elements[type_settings].add(settings_elements.values())
            self.settings_elements[type_settings] = {}
            self.settings_elements[type_settings] = settings_elements

    def update(self, active, args):
        self.image.fill(self.parent.Colors.Background)
        if active:
            self.elements['default'][None].update()
            self.elements['default'][None].draw(self.image)
            self.elements['default'][self.active_element].update()
            self.elements['default'][self.active_element].draw(self.image)
            if self.selected:
                self.settings_elements[self.active_element][self.selected].update()
            else:
                self.elements[self.active_element].update()
            self.elements[self.active_element].draw(self.image)
            if self.selected:
                pygame.sprite.Group(self.settings_elements[self.active_element][self.selected]).draw(self.image)

            for event in self.parent.events:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.ButtonEsc.Function()

            if self.parent.mouse_left_release:
                if self.ButtonEsc.isCollide():
                    self.ButtonEsc.Function()
                else:
                    for element in GetDeepData(self.elements):
                        if element.isCollide():
                            element.Function()

        return self.image
