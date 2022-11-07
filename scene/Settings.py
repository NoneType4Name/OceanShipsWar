# from Gui import *
#
#
# class Settings:
#     def __init__(self, settings, set_of_settings, set_of_settings_type, set_for_lists, set_for_paths, game_language, size, surface):
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
