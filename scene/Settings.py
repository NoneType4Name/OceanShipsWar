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
            self.settings_elements[type_settings] = {}
            self.settings_elements[type_settings] = settings_elements
            self.elements[type_settings] = pygame.sprite.Group(settings_elements.values())

    def update(self, active, args):
        self.image.fill(self.parent.Colors.Background)
        if active:
            self.elements['default'][None].update()
            self.elements['default'][None].draw(self.image)
            try:
                self.elements['default'][self.active_element].update()
                self.elements['default'][self.active_element].draw(self.image)
                if self.selected:
                    self.settings_elements[self.active_element][self.selected].update()
                else:
                    self.elements[self.active_element].update()
                self.elements[self.active_element].draw(self.image)
                if self.selected:
                    pygame.sprite.Group(self.settings_elements[self.active_element][self.selected]).draw(self.image)
            except KeyError:
                pass

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
#         settings = copy.deepcopy(settings)
#         self.all_settings = {}
#         self.default_font = settings['Graphic']['Font']
#         self.set_of_settings = set_of_settings
#         self.set_of_settings_type = set_of_settings
#         self.set_for_lists = set_of_settings_type
#         self.set_for_paths = set_for_paths
#         self.settings = settings
#         self.active_settings = list(self.settings.keys())[0]
#         self.active_element = None
#         self.upper = pad = buttons_pad = set_of_settings['up margin']
#         self.game_language = game_language
#         self.surface = surface
#         self.mouse = False
#         BaseRect = pygame.Rect(size[0] // 2 - size[0] // 1.92 // 2, size[1] * pad, size[0] // 1.92, size[1] // 36)
#         SettingsButtons = []
#         for type_settings in settings:
#             pad = self.upper
#             temp_g = []
#             SettingsElements = []
#             Labels = []
#             SettingsButtons.append(
#                 Button(self.default_font, (size[0] * 0.05, size[1] * buttons_pad, BaseRect.h * 5, BaseRect.h),
#                        game_language[type_settings],
#                        *set_of_settings[
#                            'buttons active' if type_settings == self.active_element else 'buttons'],
#                        1, ))
#             for element in settings[type_settings]:
#                 BaseRect = pygame.Rect(size[0] // 2 - size[0] // 1.92 // 2, size[1] * pad, size[0] // 1.92,
#                                        size[1] // 36)
#                 if set_of_settings_type[type_settings][element] is Switch:
#                     SettingsElements.append(
#                         Switch((BaseRect.x + BaseRect.w - (BaseRect.h * 2 - BaseRect.h * 0.1) - 1,
#                                 BaseRect.y + 1,
#                                 BaseRect.h * 2 - BaseRect.h * 0.1,
#                                 BaseRect.h - 2),
#                                *set_of_settings['switches'],
#                                name=f'{type_settings} {element}',
#                                power=settings[type_settings][element]))
#                 elif set_of_settings_type[type_settings][element] is List:
#                     temp_g.append(
#                         List(self.default_font, (BaseRect.x + BaseRect.w - (BaseRect.h * 4 - BaseRect.h * 0.1) - 1,
#                                                  BaseRect.y + 1,
#                                                  BaseRect.h * 4 - BaseRect.h * 0.1,
#                                                  BaseRect.h - 2),
#                              set_for_lists[element][settings[type_settings][element]],
#                              settings[type_settings][element],
#                              [v for v in set_for_lists[element].values()],
#                              [v for v in set_for_lists[element].keys()],
#                              *set_of_settings['lists'],
#                              f'{type_settings} {element}'))
#                 elif set_of_settings_type[type_settings][element] is Slide:
#                     SettingsElements.append(Slide(self.default_font,
#                                                   (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1,
#                                                    BaseRect.y + 1,
#                                                    (BaseRect.h - 2) * 10,
#                                                    BaseRect.h - 2),
#                                                   *set_of_settings['slides'],
#                                                   base_data=settings[type_settings][element],
#                                                   name=f'{type_settings} {element}'))
#                 elif set_of_settings_type[type_settings][element] is Path:
#                     SettingsElements.append(Path(self.default_font,
#                                                  (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1,
#                                                   BaseRect.y + 1,
#                                                   (BaseRect.h - 2) * 10,
#                                                   BaseRect.h - 2),
#                                                  *set_of_settings['path'], value=settings[type_settings][element],
#                                                  display=set_for_paths[element]['name'],
#                                                  name=f'{type_settings} {element}',
#                                                  multiple=set_for_paths[element]['multiple'],
#                                                  types=set_for_paths[element]['types'],
#                                                  typ=set_for_paths[element]['values']))
#                 else:
#                     print(type_settings, element, type(set_of_settings_type[type_settings][element]))
#                     raise SystemError
#                 Labels.append(
#                     Label(self.default_font, BaseRect, game_language[f'{type_settings} {element}'], *set_of_settings['label'], False))
#                 pad += BaseRect.h / size[1] * 1.1
#             buttons_pad += (BaseRect.h / size[1] * 1.1)
#             for el in reversed(temp_g):
#                 SettingsElements.append(el)
#             self.all_settings[type_settings] = {}
#             self.all_settings[type_settings]['labels'] = Labels
#             self.all_settings[type_settings]['buttons'] = SettingsButtons
#             self.all_settings[type_settings]['elements'] = SettingsElements
#
#     def update(self, mouse, events):
#         self.mouse = mouse
#         for label in self.all_settings[self.active_settings]['labels']:
#             if self.active_element:
#                 label.update(self.game_language[self.active_element])
#             else:
#                 label.update()
#             self.surface.blit(label.image, label.rect)
#
#         sett = self.all_settings[self.active_settings]
#         for sprite in sett['buttons']:
#             sprite.update()
#             if sprite.isCollide() and self.mouse:
#                 for n, i in enumerate(self.game_language.values()):
#                     if i == sprite.text:
#                         break
#                 el = list(self.game_language.keys())[n]
#                 self.active_settings = el
#                 self.mouse = False
#             self.surface.blit(sprite.image, sprite.rect)
#
#         for n, sprite in enumerate(sett['elements']):
#             self.surface.blit(sprite.image, sprite.rect)
#             if not self.active_element:
#                 name = sprite.name.split(' ')
#                 if sprite.value != self.settings[name[0]][name[1]]:
#                     sprite.value = self.settings[name[0]][name[1]]
#                 SpriteUpdate: dict = sprite.update(self.mouse)
#                 if SpriteUpdate:
#                     if type(SpriteUpdate) is bool:
#                         self.active_element = sprite.name
#                     elif type(SpriteUpdate) is int:
#                         self.active_element = sprite.name
#                         self.mouse = False
#                     elif type(SpriteUpdate) is dict:
#                         temp = tuple(SpriteUpdate.keys())[0]
#                         if temp:
#                             temp2 = temp.split(' ')
#                             self.settings[temp2[0]][temp2[1]] = SpriteUpdate[temp]
#                             self.all_settings[self.active_settings]['elements'][n].value = SpriteUpdate[temp]
#                         self.mouse = False
#             else:
#                 if sprite.name != self.active_element:
#                     sprite.update(False)
#                 else:
#                     SpriteUpdate: dict = sprite.update(self.mouse)
#                     if SpriteUpdate:
#                         if type(SpriteUpdate) != bool:
#                             temp = tuple(SpriteUpdate.keys())[0]
#                             temp2 = temp.split(' ')
#                             self.settings[temp2[0]][temp2[1]] = SpriteUpdate[temp]
#                             self.all_settings[self.active_settings]['elements'][n].value = SpriteUpdate[temp]
#                             self.active_element = None
#                             self.mouse = False
#                         else:
#                             self.active_element = None
#                             self.mouse = False
#
#
