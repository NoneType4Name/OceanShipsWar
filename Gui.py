import string
import numpy
import pygame
import time
from constants import *

PUNCTUATION = string.punctuation+' '
ESCAPE_CHARS = '\n\a\b\f\r\t\v\x00'
ESCAPE_CHARS_TRANSLATER = str.maketrans(dict.fromkeys(list(ESCAPE_CHARS), None))

pygame.font.init()


# def FontRender(font, text, text_rect: pygame.Rect, color, background: None):
#     srf = pygame.font.Font(font, 1000).render(text, True, color, background)
#     return pygame.transform.smoothscale(srf, (text_rect.w, text_rect.h))

class MainFont:
    def __init__(self, font_path):
        self.font = pygame.font.Font(font_path, 256)

    def render(self, text: str, text_rect: pygame.Rect, antialias: bool, color: pygame.Color, background=None) -> pygame.Surface:
        srf = self.font.render(text, antialias, color, background)
        return pygame.transform.smoothscale(
            srf, numpy.array(srf.get_size()) / max(numpy.array(srf.get_size()) / numpy.array((text_rect.w, text_rect.h))))


Font = MainFont(FONT_PATH)


def EscActivate(self, **kwargs):
    self.parent.parent.SetScene(self.parent.InputScene, *kwargs)
    self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')


def GetDeepData(data):
    rtn = []
    if type(data) is dict:
        for val in data.values():
            if isinstance(val, dict):
                v = GetDeepData(val)
                for x in v:
                    rtn.append(x)
            elif isinstance(val, (list, set, tuple, frozenset)):
                rtn += val
            elif isinstance(val, pygame.sprite.Group):
                for x in val:
                    rtn.append(x)
            else:
                rtn.append(val)
    elif type(data) is list:
        for val in data:
            if isinstance(val, (list, set, tuple, frozenset)):
                rtn += val
            elif isinstance(val, dict):
                v = GetDeepData(val)
                for x in v:
                    rtn.append(x)
            else:
                rtn.append(val)
    return rtn


def draw_round_rect(rect, color, radius):
    rect = pygame.Rect(rect)
    color = pygame.Color(color)
    alpha = color.a
    color.a = 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return rectangle


def RoundedRect(rect: tuple, color: tuple, radius=0.4, gradient=False, gradient_start=(), gradient_end=(), border=0) -> pygame.Surface:
    """
    RoundedRect(rect, color, radius=0.4, width=0)

    rect    : rectangle:tuple
    color   : rgb or rgba:tuple
    radius  : 0 <= radius <= 1:float
    gradient   : tuple: (rgb or rgba end color: tuple, rgb or rgba start color: tuple, border)


    return  ->  rectangle image
    """
    rect = pygame.Rect(0, 0, rect[2], rect[3])
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    border = round(border)
    if gradient:
        gradient_start = pygame.Color(gradient_start)
        gradient_end = pygame.Color(gradient_end)
        r_step = (gradient_end.r - gradient_start.r) / border
        g_step = (gradient_end.g - gradient_start.g) / border
        b_step = (gradient_end.b - gradient_start.b) / border
        gradient_start_list = [gradient_start.r, gradient_start.g, gradient_start.b, gradient_start.a]
        for pix in range(border):
            surf.blit(draw_round_rect((0, 0, rect.w - pix * 2, rect.h - pix * 2), gradient_start, radius), (pix, pix))
            gradient_start_list[0] += r_step
            gradient_start_list[1] += g_step
            gradient_start_list[2] += b_step
            gradient_start = pygame.Color(*map(round, gradient_start_list))
    elif border:
        surf.blit(draw_round_rect(rect, gradient_start, radius), (0, 0))
    surf.blit(draw_round_rect((0, 0, rect.w - border * 2, rect.h - border * 2), color, radius), (border, border))
    return surf


class Button(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, text_rect_active, text, text_active,
                 color, color_active, text_color, text_color_active,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func=None, args=()):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.text_rect = pygame.Rect(text_rect)
        self.text_rect_active = pygame.Rect(text_rect_active)
        self.text = text
        self.text_active = text_active
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.color_act_text = pygame.Color(text_color_active)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.border_active = border
        self.radius = radius
        self.border = border_active
        self.radius_active = radius_active
        self.func = func if func else lambda s, a=(): s
        self.args = args

        # font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, text, self.text_rect))
        font = Font.render(self.text, self.text_rect, True, self.text_color)
        size = font.get_size()

        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius, self.gradient, self.gradient_start, self.gradient_end, self.border), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        # font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, text_active, self.text_rect_active))
        font = Font.render(self.text_active, self.text_rect_active, True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(RoundedRect(self.rect, self.color_active, self.radius_active, self.gradient_active, self.gradient_start_active, self.gradient_end_active, self.border_active), (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        self.collide = False

    def update(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide() and not self.collide:
            self.collide = True
            self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'active')
        elif not self.isCollide() and self.collide:
            self.collide = False

        if self.collide:
            self.image = self.image_active
            self.parent.parent.cursor = pygame.SYSTEM_CURSOR_HAND
        else:
            self.image = self.image_base

    def UpdateImage(self):
        font = Font.render(self.text, self.text_rect, True, self.text_color)
        size = font.get_size()

        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius, self.gradient, self.gradient_start, self.gradient_end, self.border), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        # font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, text_active, self.text_rect_active))
        font = Font.render(self.text_active, self.text_rect_active, True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(RoundedRect(self.rect, self.color_active, self.radius_active, self.gradient_active, self.gradient_start_active, self.gradient_end_active, self.border_active), (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

    def Function(self):
        if self.args:
            # threading.Thread(target=self.func, args=(self, *self.args)).start()
            self.func(self, *self.args)
        else:
            self.func(self)


class Switch(pygame.sprite.Sprite):
    def __init__(self, parent, rect,  type_settings, name, value, color, color_active, color_on, color_off, func=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.color_on = pygame.Color(color_on)
        self.color_off = pygame.Color(color_off)
        self.type_settings = type_settings
        self.name = name
        self.value = value
        self.func = func if func else lambda s: s

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.value:
            self.image.blit(RoundedRect(self.rect, self.color_active, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_on, (self.rect.w / 2 + self.rect.h * 0.55, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        elif not self.value:
            self.image.blit(RoundedRect(self.rect, self.color, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_off, (self.rect.w / 2 - self.rect.h / 2, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        if self.isCollide() and self.parent.parent.mouse_left_release:
            self.value = not self.value
            self.func(self)

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

    def Function(self):
        pass


class Label(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, left_padding, text,
                 color, color_active, text_color, text_color_active,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.text_rect = pygame.Rect(text_rect)
        self.left_padding = left_padding
        self.value = text
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.border = border
        self.border_active = border_active
        self.radius = radius
        self.radius_active = radius_active
        self.func = func if func else lambda s: s

    def update(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.isCollide():
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color_active,self.radius_active,
                                        self.gradient_active, self.gradient_start_active, self.gradient_end_active, self.border_active), (0, 0))
            font = Font.render(self.value, self.text_rect, True, self.text_color_active)
            size = font.get_size()
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, self.radius,
                                        self.gradient, self.gradient_start, self.gradient_end,
                                        self.border), (0, 0))
            font = Font.render(self.value, self.text_rect, True, self.text_color)
            size = font.get_size()
            self.image.blit(font,
                            (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        self.image.blit(font,
                        (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        return self.image

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    # def NewFont(self):
    #     self.font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.value, self.text_rect))
    #     self.size = self.font.size(self.value)

    def Function(self):
        self.func(self)


class Slide(pygame.sprite.Sprite):
    def __init__(self, parent, rect, slide_width, type_settings, name, value, color, color_active, slide_color, slide_color_active,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func_activate=None, func_deactivate=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect[0], rect[1], rect[2] * 1.1, rect[3])
        self.slide_rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3] * slide_width)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.type_settings, self.name = type_settings, name
        self.value = value
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.slide_color = pygame.Color(slide_color)
        self.slide_color_active = pygame.Color(slide_color_active)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.border = border
        self.border_active = border_active
        self.radius = radius
        self.radius_active = radius_active
        self.func_activate = func_activate if func_activate else lambda p: False
        self.func_deactivate = func_deactivate if func_deactivate else lambda p: False
        self.active = False

    def update(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image.blit(RoundedRect((0, 0, self.slide_rect.w * self.value + (self.rect.h * 1 if self.value else 0),
                                     self.slide_rect.h * 0.5), self.slide_color, self.radius, False), (0, (self.rect.h * 0.5) - (self.slide_rect.h * 0.26)))
        if self.isCollide() and not self.active:
            self.image.blit(RoundedRect(self.rect,
                                        self.color_active,
                                        self.radius_active,
                                        self.gradient_active, self.gradient_start_active, self.gradient_end_active), (0, 0))
            pygame.draw.circle(self.image, self.slide_color_active,
                               (self.slide_rect.w * self.value + (self.rect.h * 0.5), self.rect.h * 0.5),
                               self.rect.h * 0.5)
        elif self.active:
            self.image.blit(RoundedRect(self.rect,
                                        self.color_active,
                                        self.radius_active,
                                        self.gradient_active, self.gradient_start_active, self.gradient_end_active), (0, 0))
            pygame.draw.circle(self.image, self.slide_color_active,
                               (self.slide_rect.w * self.value + (self.rect.h * 0.5), self.rect.h * 0.5),
                               self.rect.h * 0.5)
        else:
            self.image.blit(RoundedRect(self.rect,
                                        self.color,
                                        self.radius,
                                        self.gradient, self.gradient_start, self.gradient_end), (0, 0))
            pygame.draw.circle(self.image, self.slide_color,
                               (self.slide_rect.w * self.value + (self.rect.h * 0.5), self.rect.h * 0.5),
                               self.rect.h * 0.5)
        if self.parent.parent.mouse_left_press and self.isCollide():
            if not self.active:
                self.active = True
        elif not self.parent.parent.mouse_left_press:
            if self.active:
                self.func_deactivate(self)
                self.active = False
        if self.active:
            if self.value != self.GetValue():
                self.value = self.GetValue()
            self.func_activate(self)

    def GetValue(self):
        rtn = round((pygame.mouse.get_pos()[0] - self.slide_rect.x) / self.slide_rect.w, 1)
        if 0 <= rtn <= 1:
            return rtn
        elif rtn < 0:
            return 0
        else:
            return 1

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

    def Function(self):
        pass


class Element(pygame.sprite.Sprite):
    def __init__(self, parent, rect, real_rect, value, color, text_color, text_color_active,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 border=0, radius=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.real_rect = pygame.Rect(real_rect)
        self.color = pygame.Color(color)
        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.border = border
        self.radius = radius
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.value = value
        self.font_active = Font.render(self.parent.texts[self.value], self.rect, True, self.text_color_active)
        self.font = Font.render(self.parent.texts[self.value], self.rect, True, self.text_color)
        # self.font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.parent.texts[self.value], self.parent.rect))
        # self.size = self.font.size(self.parent.texts[self.value])

    def update(self):
        if self.isCollide():
            self.image.blit(RoundedRect(self.rect, self.color,self.radius), (0, 0))
            self.image.blit(self.font_active,
                            (self.rect.w * self.parent.left_padding - self.font.get_size()[0] * 0.5,
                             self.rect.h * 0.5 - self.font.get_size()[1] * 0.5))
            if self.parent.parent.parent.mouse_left_release:
                self.parent.value = self.value
        else:
            self.image.blit(RoundedRect(self.rect, self.color, self.radius, self.gradient, self.gradient_start, self.gradient_end, self.border), (0, 0))
            self.image.blit(self.font,
                            (self.rect.w * self.parent.left_padding - self.font.get_size()[0] * 0.5,
                             self.rect.h * 0.5 - self.font.get_size()[1] * 0.5))

    def isCollide(self):
        return self.real_rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.real_rect.x += x
        self.real_rect.y += y


class List(pygame.sprite.Sprite):
    def __init__(self, parent, rect, left_padding, display_names: list, real_values, type_settings, name, value,
                 color, color_active,
                 text_color, text_color_active,
                 color_list,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 gradient_list=False, gradient_start_list=(), gradient_end_list=(),
                 gradient_list_active=False, gradient_list_start_active=(), gradient_list_end_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func_activate=None, func_deactivate=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.left_padding = left_padding
        self.texts = display_names
        self.values = real_values
        self.type_settings = type_settings
        self.name = name
        self.value = value
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.color_list = pygame.Color(color_list)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.gradient_list = gradient_list
        self.gradient_start_list = gradient_start_list
        self.gradient_end_list = gradient_end_list
        self.gradient_list_active = gradient_list_active
        self.gradient_start_list_active = gradient_list_start_active
        self.gradient_end_list_active = gradient_list_end_active
        self.border = border
        self.border_active = border_active
        self.radius = radius
        self.radius_active = radius_active
        self.func_activate = func_activate if func_activate else lambda p: False
        self.func_deactivate = func_deactivate if func_deactivate else lambda p: False
        self.active = False
        # self.font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.texts[self.value], self.rect))
        self.font_active = Font.render(self.texts[self.value], self.rect, True, self.text_color_active)
        self.font = Font.render(self.texts[self.value], self.rect, True, self.text_color)
        self.image = pygame.Surface(
            (self.rect.w, self.rect.h + self.font.get_size()[1] * len(self.texts) + self.font.get_size()[1] * 0.1 * len(self.texts)),
            pygame.SRCALPHA)
        self.elements = pygame.sprite.Group()
        for n in range(len(self.texts)):
            if n == self.value:
                self.elements.add(
                    Element(self, (0, rect[3] * (n + 1), rect[2], rect[3]),
                            (self.rect.x, self.rect.y + self.rect.h * (n + 1), self.rect.w, self.rect.h),
                            n,
                            self.color_list,
                            self.text_color_active,
                            self.text_color_active,
                            self.gradient_list_active, self.gradient_start_list_active, self.gradient_end_list_active,
                            self.gradient_list_active, self.gradient_start_list_active, self.gradient_end_list_active,
                            self.border_active,
                            self.radius_active))
            else:
                self.elements.add(
                    Element(self, (0, rect[3] * (n + 1), rect[2], rect[3]),
                            (self.rect.x, self.rect.y + self.rect.h * (n + 1), self.rect.w, self.rect.h),
                            n,
                            self.color_list,
                            self.text_color,
                            self.text_color_active,
                            self.gradient_list, self.gradient_start_list, self.gradient_end_list,
                            self.gradient_list_active, self.gradient_start_list_active, self.gradient_end_list_active,
                            self.border, self.radius))

    def update(self):
        self.image = pygame.Surface(
            (self.rect.w,
             self.rect.h + self.font.get_size()[1] * len(self.texts) + self.font.get_size()[1] * 0.1 * len(self.texts)),
            pygame.SRCALPHA)
        if self.active:
            self.image.blit(
                RoundedRect(self.rect, self.color_active, self.radius_active, self.gradient_active, self.gradient_start_active, self.gradient_end_active, self.border_active), (0, 0))
            self.image.blit(self.font_active, (self.rect.w * self.left_padding - self.font_active.get_size()[0] * 0.5, self.rect.h * 0.5 - self.font_active.get_size()[1] * 0.5))
        else:
            self.image.blit(RoundedRect(self.rect, self.color, self.radius, self.gradient, self.gradient_start, self.gradient_end, self.border), (0, 0))
            self.image.blit(self.font, (self.rect.w * self.left_padding - self.font_active.get_size()[0] * 0.5, self.rect.h * 0.5 - self.font_active.get_size()[1] * 0.5))
        if not self.active and self.parent.parent.mouse_left_release and self.isCollide():
            self.Activate()
        elif self.active:
            self.elements.update()
            self.elements.draw(self.image)
            if self.parent.parent.mouse_left_release:
                self.Deactivate()

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

        for p in self.elements.sprites():
            p.RectEdit(x, y)

    def Function(self):
        pass

    def Deactivate(self):
        self.active = False
        self.font_active = Font.render(self.texts[self.value], self.rect, True, self.text_color_active)
        self.font = Font.render(self.texts[self.value], self.rect, True, self.text_color)
        self.func_deactivate(self)

    def Activate(self):
        self.active = True
        self.func_activate(self)


class TextInput(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, default_text, text, left_padding: float,
                 color, color_active, text_color, text_color_active,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func_activate=None, func_deactivate=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)

        self.text_rect = pygame.Rect(text_rect)
        self.default = default_text
        self.text = text
        self.value = self.text if self.text else self.default
        self.left_padding = left_padding
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)

        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.gradient_end_active = gradient_end_active
        self.border = border
        self.radius = radius
        self.border_active = border_active
        self.radius_active = radius_active
        self.func_activate = func_activate if func_activate else lambda s: s
        self.func_deactivate = func_deactivate if func_deactivate else lambda s: s

        self.active = False
        self.collide = False
        self.pos = len(self.value)

    def update(self, events):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        font = Font.render(self.value, self.text_rect, True, self.text_color)
        font_active = Font.render(self.value, self.text_rect, True, self.text_color_active)
        size = font.get_size()
        if self.isCollide() and not self.collide:
            self.collide = True
        elif not self.isCollide() and self.collide:
            self.collide = False
        if self.active:
            if self.isCollide():
                self.parent.parent.cursor = pygame.SYSTEM_CURSOR_IBEAM
            self.image.blit(RoundedRect(self.rect, self.color_active, self.radius, self.gradient_active, self.gradient_start_active, self.gradient_end_active, self.border_active), (0, 0))
            if time.time() % 1 > 0.5:
                ft = Font.render(self.text[:self.pos], self.text_rect, True, (0, 0, 0))
                sz = ft.get_size()
                width = 2
                pygame.draw.line(self.image,
                                 (self.color_active.r - 100 if self.color_active.r - 100 > 0 else 100,
                                  self.color_active.g - 100 if self.color_active.g - 100 > 0 else 100,
                                  self.color_active.b - 100 if self.color_active.b - 100 > 0 else 100),
                                 ((self.text_rect.w * self.left_padding - size[0] * 0.5) - width + sz[0] + self.text_rect.x,
                                  self.text_rect.h * 0.5 - size[1] * 0.5 + self.text_rect.y),
                                 ((self.text_rect.w * self.left_padding - size[0] * 0.5) - width + sz[0] + self.text_rect.x,
                                  self.text_rect.h * 0.5 + size[1] * 0.5 + self.text_rect.y),
                                 width)
        else:
            if self.isCollide():
                self.parent.parent.cursor = pygame.SYSTEM_CURSOR_HAND
                self.image.blit(RoundedRect(self.rect, self.color, self.radius, self.gradient, self.gradient_start_active, self.gradient_end_active, self.border), (0, 0))
            else:
                self.image.blit(RoundedRect(self.rect, self.color, self.radius, self.gradient, self.gradient_start, self.gradient_end, self.border), (0, 0))
        if self.text:
            self.image.blit(font_active,
                            (self.rect.w * self.left_padding - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        else:
            self.image.blit(font,
                            (self.rect.w * self.left_padding - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

        if any(map(lambda e: e.type in (pygame.KEYDOWN, pygame.TEXTEDITING, pygame.TEXTINPUT), events)):
            for event in events:
                if self.active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            if self.pos:
                                if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                    for n, sim in enumerate(self.text[self.pos::-1]):
                                        if sim in PUNCTUATION:
                                            self.text = self.text[:self.pos - (n if n != 0 else 1)] + self.text[self.pos:]
                                            self.pos -= n if n != 0 else 1
                                            break
                                    else:
                                        self.text = self.text[self.pos:]
                                        self.pos = 0
                                else:
                                    self.text = self.text[:self.pos - 1] + self.text[self.pos:]
                                    self.pos -= 1
                        elif event.key == pygame.K_LEFT:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                for n, sim in enumerate(self.text[:self.pos][::-1]):
                                    if sim in PUNCTUATION:
                                        self.pos -= n if n != 0 else 1
                                        break
                                else:
                                    self.pos = 0
                            elif self.pos - 1 >= 0:
                                self.pos -= 1
                        elif event.key == pygame.K_RIGHT:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                for n, sim in enumerate(self.text[self.pos:]):
                                    if sim in PUNCTUATION:
                                        self.pos += n if n != 0 else 1
                                        break
                                else:
                                    self.pos = len(self.text)
                            elif self.pos + 1 <= len(self.text):
                                self.pos += 1
                        elif event.key == pygame.K_DELETE:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                for n, sim in enumerate(self.text[self.pos:]):
                                    if sim in PUNCTUATION:
                                        self.text = self.text[:self.pos] + self.text[self.pos + n if n != 0 else 1:]
                                        break
                                else:
                                    self.text = self.text[:self.pos]
                            else:
                                self.text = self.text[:self.pos] + self.text[self.pos + 1:]
                        elif event.key == pygame.K_HOME:
                            self.pos = 0
                        elif event.key == pygame.K_END:
                            self.pos = len(self.text)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL and not self.text:
                                self.text = self.default
                                self.pos = len(self.text)
                            else:
                                self.Deactivate()
                        elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
                            paste_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode().translate(ESCAPE_CHARS_TRANSLATER)
                            if paste_text:
                                self.text = self.text = self.text[:self.pos] + paste_text + self.text[self.pos:]
                                self.pos += len(paste_text)
                    elif event.type == pygame.TEXTINPUT:
                        self.text = self.text[:self.pos] + event.text + self.text[self.pos:]
                        self.pos += len(event.text)
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_ESCAPE:
                            self.Deactivate()
                    self.value = self.text if self.text else self.default
        return self.image

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def Activate(self):
        self.active = True
        self.pos = len(self.text)
        while not pygame.key.get_focused() or not pygame.key.get_repeat()[0]:
            pygame.key.start_text_input()
            pygame.key.set_repeat(500, 50)
        self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'active')
        self.func_activate(self)

    def Deactivate(self):
        self.active = False
        self.parent.parent.PlaySound(SOUND_TYPE_GAME, 'select')
        pygame.key.set_repeat(0, 0)
        self.func_deactivate(self)


class Notification(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text, background, around, font_color):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect[0], rect[1] - rect[3], rect[2], rect[3] * 3)
        self.NotificationRect = pygame.Rect(rect)
        self.StartRect = pygame.Rect(rect)
        self.NotificationRect.y = -rect[1]
        self.NotificationRect.x = 0
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.background = pygame.Color(background)
        self.background.a = 240
        self.around = pygame.Color(around)
        self.FontColor = pygame.Color(font_color)
        self.text = {}
        self.StartTime = None
        self.end = False
        self.height_font = 0
        self.step = self.StartRect.h // 8
        self.max = ''  # max(max(self.text.values()))
        self.draw_point = 0
        for n, element in enumerate(str(text).split('\t')):
            string_n = element.split(' ')
            self.text[n] = [' '.join(string_n[x:x + 5]) for x in range(0, len(string_n), 5)]
            self.height_font += len(self.text[n]) + 0.5
        for el in max(self.text.values()):
            if len(self.max) < len(el):
                self.max = el

        for s in range(0, 1000):
            self.font = pygame.font.Font(FONT_PATH, s)
            self.size = list(self.font.size(self.max))
            self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
            if self.size[0] >= self.NotificationRect.w * 0.9 or self.size[1] >= self.NotificationRect.h * 0.9:
                self.font = pygame.font.Font(FONT_PATH, s - 1)
                self.size = list(self.font.size(self.max))
                self.StartSize = self.font.size(self.max)
                self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
                break
        self.parent.PlaySound(SOUND_TYPE_NOTIFICATION, 'in')

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide():
            self.parent.cursor = pygame.SYSTEM_CURSOR_HAND
            if mouse:
                self.end = True
        if not self.StartTime and self.NotificationRect.y < self.StartRect.y:
            if self.NotificationRect.y + self.step >= self.StartRect.y:
                self.NotificationRect.y = self.StartRect.y
                self.StartTime = time.time()
            else:
                self.NotificationRect.y += self.step
        elif (time.time() - self.height_font >= self.StartTime and self.NotificationRect.y >= self.rect.y - self.StartRect.h and not self.isCollide()) or (self.end and self.NotificationRect.y >= self.rect.y - self.StartRect.h):
            if self.NotificationRect.y + self.NotificationRect.h + self.step >= self.rect.y + self.rect.h - self.StartRect.h:
                self.parent.PlaySound(SOUND_TYPE_NOTIFICATION, 'out')
            self.NotificationRect.y -= self.step
        elif (
                time.time() - self.height_font > self.StartTime and self.NotificationRect.y < self.rect.y - self.StartRect.h) or (
                self.NotificationRect.y <= self.rect.y - self.StartRect.h and self.end):
            self.kill()
            return True
        self.image.blit(RoundedRect(self.NotificationRect, self.background, 0.3), (0, self.NotificationRect.y))
        self.draw_point = 0
        for point in self.text:
            pygame.draw.circle(self.image, self.FontColor, (self.rect.w * 0.03,
                                                            self.NotificationRect.y + self.NotificationRect.h * 0.1 +
                                                            self.StartSize[1] * self.draw_point + self.StartSize[
                                                                1] // 2), self.StartSize[1] * 0.2)
            for text in self.text[point]:
                self.image.blit(self.font.render(text, True, self.FontColor), (
                    self.rect.w * 0.1,
                    self.NotificationRect.y + self.NotificationRect.h * 0.1 + self.StartSize[1] * self.draw_point))
                self.draw_point += 1
            self.draw_point += 0.5

    def isCollide(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.x <= mouse_pos[0] <= self.rect.x + self.rect.w and self.NotificationRect.y + self.rect.y <= \
                mouse_pos[1] <= self.NotificationRect.y + self.NotificationRect.h + self.rect.y:
            return True
        else:
            return False


class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, rect, around, progress_color, value):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.around = pygame.Color(around)
        self.progress_color = pygame.Color(progress_color)
        self.value = value
        self.wh = int((self.rect.w + self.rect.h) / 100)

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.around), (0, 0))
        self.image.blit(
            RoundedRect((0, 0, (self.rect.w - self.wh * 2) * self.value, self.rect.h - self.wh * 2),
                        self.progress_color), (self.wh, self.wh))


class Ticker(pygame.sprite.Sprite):
    def __init__(self, rect, text, left_padding, color, text_color):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.text = text
        self.left_padding = left_padding
        self.color = pygame.Color(color)
        self.text_color = pygame.Color(text_color)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image.fill(self.color)
        self.font = Font.render(self.text, self.rect, True, self.text_color)
        # self.font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.text, self.rect))
        # self.size = self.font.size(self.text)
        self.image.blit(self.font, (self.rect.w * self.left_padding - self.font.get_size()[0] * 0.5, self.rect.h * 0.5 - self.font.get_size()[1] * 0.5))

    def update(self):
        pass


# class Path(pygame.sprite.Sprite):
#     def __init__(self, default_font, rect, around, color, font_color, display, name, value, types, typ, multiple):
#         pygame.sprite.Sprite.__init__(self)
#         self.default_font = default_font
#         self.rect = pygame.Rect(rect)
#         wh = int(self.rect.w + self.rect.h) // 100
#         self.wh = wh if wh else 1
#         self.rect_inner = pygame.Rect(rect[0] + self.wh, rect[1] + self.wh, rect[2] - self.wh * 2,
#                                       rect[3] - self.wh * 2)
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         self.around_color = pygame.Color(around)
#         self.color = pygame.Color(color)
#         self.font_color = pygame.Color(font_color)
#         self.types = types
#         self.typ = typ
#         self.name = name
#         self.display = display
#         self.value = value
#         self.multiple = multiple
#         for s in range(1000):
#             self.font = pygame.font.Font(default_font, s)
#             self.size = self.font.size(self.value)
#             if self.size[0] > self.rect_inner.w or self.size[1] > self.rect_inner.h:
#                 self.font = pygame.font.Font(default_font, s - 1)
#                 self.size = self.font.size(self.value)
#                 break
#
#     def update(self, mouse):
#         if os.path.splitext(self.value)[1] in self.typ:
#             self.image.blit(RoundedRect(self.rect, self.around_color, 1, self.wh, self.color), (0, 0))
#         else:
#             self.image.blit(RoundedRect(self.rect, (255, 0, 0), 1, self.wh, self.color), (0, 0))
#         if '\\' in self.value:
#             sep = '\\'
#         elif '/' in self.value:
#             sep = '/'
#         val = f'.../{"/".join(self.value.split(sep)[-3:])}'
#         for s in range(1000):
#             self.font = pygame.font.Font(self.default_font, s)
#             self.size = self.font.size(val)
#             if self.size[0] >= self.rect_inner.w or self.size[1] >= self.rect_inner.h:
#                 self.font = pygame.font.Font(self.default_font, s - 1)
#                 self.size = self.font.size(val)
#                 break
#
#         self.image.blit(self.font.render(val, True, self.font_color), (self.rect_inner.w / 2 - self.size[0] / 2,
#                                                                        self.rect_inner.h / 2 - self.size[1] / 2))
#         if mouse and self.rect.collidepoint(pygame.mouse.get_pos()):
#             # os.chdir()
#             window = win32ui.CreateFileDialog(1, "", "", 0, "*.ttf|*.ttf|")
#             # value = win32ui.CreateFileDialog(1, ".txt", "default.txt", 0, "Font files (*.ttf)|*.ttf|All Files (*.*)|*.*|")
#             window.DoModal()
#             value = window.GetPathName()
#             # value = easygui.fileopenbox(filetypes=self.types, multiple=self.multiple, title=self.display)
#             if value:
#                 if os.path.splitext(value)[1] in self.typ:
#                     self.value = value
#                     return {self.name: self.value}
#                 else:
#                     self.value = value
