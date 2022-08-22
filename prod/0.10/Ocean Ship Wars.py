import json
import math
import os.path
import random
import socket
import subprocess
import time
import pygame
import requests
import threading
from screeninfo import get_monitors
from io import BytesIO
# from Buttons import *
import pyperclip

PUNCTUATION = list('''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ''')
pygame.font.init()


def RoundedRect(rect, color, radius=0.4) -> pygame.Surface:
    """
    RoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect = pygame.Rect(0, 0, rect[2], rect[3])
    color = pygame.Color(*color)
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


class button(pygame.sprite.Sprite):
    def __init__(self, rect, text, color1, color2, text_color, color1_act, color2_act, color_act_text):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color1 = pygame.Color(color1)
        self.color2 = pygame.Color(color2)
        self.color1_act = pygame.Color(color1_act)
        self.color2_act = pygame.Color(color2_act)
        self.text_color = pygame.Color(text_color)
        self.color_act_text = pygame.Color(color_act_text)
        self.text = text
        for s in range(1000):
            self.font = pygame.font.SysFont('notosans', s)
            self.size = self.font.size(self.text)
            if self.size[0] >= self.rect.w - self.rect.h * 0.1 * 4 or self.size[
                1] >= self.rect.h - self.rect.h * 0.1 * 4:
                self.font = pygame.font.SysFont('notosans', s - 1)
                self.size = self.font.size(self.text)
                break

    def update(self):
        if self.isCollide():
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color1_act), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rect.w - self.rect.h * 0.1, self.rect.h - self.rect.h * 0.1),
                            self.color2_act), (self.rect.h * 0.06, self.rect.h * 0.06))
            self.image.blit(self.font.render(self.text, True, self.color_act_text),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color1), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rect.w - self.rect.h * 0.1, self.rect.h - self.rect.h * 0.1),
                            self.color2), (self.rect.h * 0.06, self.rect.h * 0.06))
            self.image.blit(self.font.render(self.text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))

    def isCollide(self):
        if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                pygame.mouse.get_pos()[
                    1] < self.rect.y + self.rect.height:
            return True
        else:
            return False


class switch(pygame.sprite.Sprite):
    def __init__(self, rect, color_on, color_off, background, name, power=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color_on = pygame.Color(color_on)
        self.color_off = pygame.Color(color_off)
        self.background = pygame.Color(background)
        self.name = name
        self.power = power

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.power:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            # self.image.blit(RoundedRect((0,0,self.rect.w-self.rect.w*0.2,self.rect.h-self.rect.h*0.2),self.background,1),(self.rect.w*0.1,self.rect.h*0.1))
            pygame.draw.circle(self.image, self.color_on, (self.rect.w / 2 + self.rect.h * 0.55, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        elif not self.power:
            # self.image.blit(RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.background, 1),(self.rect.w * 0.1, self.rect.h * 0.1))
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_off, (self.rect.w / 2 - self.rect.h / 2, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        if self.isCollide() and mouse:
            self.power = not self.power
            return self.name


class label(pygame.sprite.Sprite):
    def __init__(self, rect, text, color, text_color, center=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.text = text
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color = pygame.Color(color)
        self.text_color = pygame.Color(text_color)
        self.center = center
        if self.center:
            for s in range(1000):
                self.font = pygame.font.SysFont('notosans', s)
                self.size = self.font.size(self.text)
                if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                    self.font = pygame.font.SysFont('notosans', s - 1)
                    self.size = self.font.size(self.text)
                    break
        else:
            for s in range(1000):
                self.font = pygame.font.SysFont('notosans', s)
                self.size = self.font.size(self.text)
                if self.size[0] > self.rect.w - self.rect.w * 0.1 or self.size[1] > self.rect.h:
                    self.font = pygame.font.SysFont('notosans', s - 1)
                    self.size = self.font.size(self.text)
                    break

    def update(self):
        if self.size != self.font.size(self.text):
            if self.center:
                for s in range(1000):
                    self.font = pygame.font.SysFont('notosans', s)
                    self.size = self.font.size(self.text)
                    if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                        self.font = pygame.font.SysFont('notosans', s - 1)
                        self.size = self.font.size(self.text)
                        break
            else:
                for s in range(1000):
                    self.font = pygame.font.SysFont('notosans', s)
                    self.size = self.font.size(self.text)
                    if self.size[0] > self.rect.w - self.rect.w * 0.1 or self.size[1] > self.rect.h:
                        self.font = pygame.font.SysFont('notosans', s - 1)
                        self.size = self.font.size(self.text)
                        break
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, 1), (0, 0))
        self.image.blit(self.font.render(self.text, True, self.text_color),
                        (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))


class Slide(pygame.sprite.Sprite):
    def __init__(self, rect, slide_color, background, base_data, name):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.slide_color = pygame.Color(slide_color)
        self.background = pygame.Color(background)
        self.base_data = base_data
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.name = name

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
        self.image.blit(RoundedRect((0, 0, self.rect.w * self.base_data, self.rect.h),
                                    (255 - self.background[0], 255 - self.background[1], 255 - self.background[2]), 1),
                        (0, 0))
        pygame.draw.circle(self.image, self.slide_color,
                           (self.rect.w * self.base_data - self.rect.h / 2, self.rect.h / 2), self.rect.h / 2, 0)
        if mouse and self.isCollide():
            self.base_data = self.isCollide()
            return self.name, self.base_data
        return False

    def isCollide(self):
        if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.w and self.rect.y < pygame.mouse.get_pos()[1] < self.rect.y + self.rect.h:
            return round((pygame.mouse.get_pos()[0] - self.rect.x) / self.rect.w, 1)
        else:
            return False


class List(pygame.sprite.Sprite):
    def __init__(self, rect, base_text, texts, text_color, background, bg_list, name):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.name = str(name)
        self.base_text = str(base_text)
        self.texts = texts
        self.text_color = text_color
        self.bg_list = bg_list
        self.background = background
        self.active = False
        for s in range(1000):
            self.font = pygame.font.SysFont('notosans', s)
            self.size = self.font.size(self.base_text)
            if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                self.font = pygame.font.SysFont('notosans', s - 1)
                self.size = self.font.size(self.base_text)
                break
        self.image = pygame.Surface(
            (self.rect.w, self.rect.h + self.size[1] * len(self.texts) + self.size[1] * 0.1 * len(self.texts)),
            pygame.SRCALPHA)

    def update(self, mouse):
        if mouse and self.isCollide():
            if self.active:
                a = f'{self.name}:{self.isCollide()}'
                self.active = not self.active
                return a
            else:
                self.active = not self.active
        self.image = pygame.Surface(
            (self.rect.w, self.rect.h + self.size[1] * len(self.texts)),
            pygame.SRCALPHA)
        if self.active:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            self.image.blit(self.font.render(self.base_text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
            # self.image.blit(RoundedRect((0,0,self.rect.w,self.size[1] * len(self.texts)),self.bg_list,0.5),(0,self.rect.h))
            for n, tx in enumerate(self.texts):
                tx = str(tx)
                self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), (255, 255, 255), 0.5),
                                (0, self.rect.h + self.rect.h * n))
                self.image.blit(
                    RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.bg_list,
                                0.5), (self.rect.w * 0.06, (self.rect.h + self.rect.h * n) + self.rect.h * 0.05))
                self.image.blit(self.font.render(tx, True, self.text_color), (self.rect.w // 2 - self.size[0] // 2,
                                                                              self.rect.h + self.rect.h * n + 1 - self.rect.h // 2 - self.rect.h * 0.05 +
                                                                              self.size[1] // 2))
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            self.image.blit(self.font.render(self.base_text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))

    def isCollide(self):
        if self.active:
            for n, rc in enumerate(self.texts):
                if self.rect.bottomleft[0] < pygame.mouse.get_pos()[0] < self.rect.bottomright[0] and \
                        self.rect.bottomleft[1] + \
                        self.size[1] * n < pygame.mouse.get_pos()[1] < self.rect.bottomright[1] + self.size[1] * (
                        n + 1):
                    return rc
                elif self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                        pygame.mouse.get_pos()[
                            1] < self.rect.y + self.rect.height:
                    return self.base_text
            else:
                return False
        else:
            if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                    pygame.mouse.get_pos()[
                        1] < self.rect.y + self.rect.height:
                return True
            else:
                return False


class TextInput(pygame.sprite.Sprite):
    def __init__(self, rect, background, around, text_color, name, base_text='', text=''):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.rectInner = pygame.Rect(self.rect.h * 0.04, self.rect.h * 0.04, self.rect.w - self.rect.h * 0.1,
                                     self.rect.h - self.rect.h * 0.1)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.background = pygame.Color(background)
        self.around = pygame.Color(around)
        self.text_color = pygame.Color(text_color)
        self.base_text = base_text
        self.text = text
        self.active = False
        self.cursor = 0
        self.name = name
        for s in range(0, 1000):
            self.font = pygame.font.SysFont('notosans', s)
            self.size = self.font.size(self.text if self.text else self.base_text)
            if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
                1] >= self.rectInner.h * 0.8 - self.rectInner.y:
                self.font = pygame.font.SysFont('notosans', s - 1)
                self.size = self.font.size(self.text if self.text else self.base_text)
                break

    def update(self, event):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and not self.active:
            if event.button == 1:
                self.active = True
                pygame.key.start_text_input()
                pygame.key.set_repeat(500, 50)
        elif not self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and self.active:
            if event.button == 1:
                self.active = False
                pygame.key.set_repeat(0, 0)
                pygame.key.stop_text_input()
                return f'{self.name}:{self.text}'
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and self.cursor:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[::-1]):
                            if sim in PUNCTUATION:
                                self.text = self.text[:self.cursor - (n if n != 0 else 1)] + self.text[self.cursor:]
                                self.cursor -= n if n != 0 else 1
                                break
                        else:
                            self.text = ''
                            self.cursor = 0
                    else:
                        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                        self.cursor -= 1
                elif event.key == pygame.K_LEFT:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[:self.cursor][::-1]):
                            if sim in PUNCTUATION:
                                self.cursor -= n if n != 0 else 1
                                break
                        else:
                            self.cursor = 0
                    elif self.cursor - 1 >= 0:
                        self.cursor -= 1
                elif event.key == pygame.K_RIGHT:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[self.cursor:]):
                            if sim in PUNCTUATION:
                                self.cursor += n if n != 0 else 1
                                break
                        else:
                            self.cursor = len(self.text)
                    elif self.cursor + 1 <= len(self.text):
                        self.cursor += 1
                elif event.key == pygame.K_DELETE:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[self.cursor:]):
                            if sim in PUNCTUATION:
                                self.text = self.text[:self.cursor] + self.text[self.cursor + n if n != 0 else 1:]
                                break
                        else:
                            self.text = self.text[:self.cursor]
                    else:
                        self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
                elif event.key == pygame.K_HOME:
                    self.cursor = 0
                elif event.key == pygame.K_END:
                    self.cursor = len(self.text)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # or event.key == pygame.K_ESCAPE
                    self.active = False
                    pygame.key.set_repeat(0, 0)
                    pygame.key.stop_text_input()
                    return f'{self.name}:{self.text}'
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    paste_text = pyperclip.paste()
                    if paste_text:
                        self.text = self.text = self.text[:self.cursor] + paste_text + self.text[self.cursor:]
                        self.cursor += len(paste_text)
            if event.type == pygame.TEXTINPUT:
                self.text = self.text[:self.cursor] + event.text + self.text[self.cursor:]
                self.cursor += 1 if event.text else 0
            for s in range(0, 1000):
                self.font = pygame.font.SysFont('notosans', s)
                self.size = self.font.size(self.text if self.text else self.base_text)
                if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
                    1] >= self.rectInner.h * 0.8 - self.rectInner.y:
                    self.font = pygame.font.SysFont('notosans', s - 1)
                    self.size = self.font.size(self.text if self.text else self.base_text)
                    break
        if self.active:
            self.image.blit(RoundedRect(self.rect, (0, 255, 0), .5), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rectInner.w + self.rectInner.x, self.rectInner.h + self.rectInner.y),
                            self.background, .5),
                (self.rectInner.x, self.rectInner.y))
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.around, .5), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rectInner.w + self.rectInner.x, self.rectInner.h + self.rectInner.y),
                            self.background, .5),
                (self.rectInner.x, self.rectInner.y))

        if self.text:
            self.image.blit(self.font.render(self.text, True, self.text_color),
                            (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(
                self.font.render(self.base_text, True, (self.text_color.r - 100 if self.text_color.r - 100 > 0 else 100,
                                                        self.text_color.g - 100 if self.text_color.g - 100 > 0 else 100,
                                                        self.text_color.b - 100 if self.text_color.b - 100 > 0 else 100)),
                (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))

        if self.active:
            pygame.draw.line(self.image,
                             (self.background.r - 100 if self.background.r - 100 > 0 else 100,
                              self.background.g - 100 if self.background.g - 100 > 0 else 100,
                              self.background.b - 100 if self.background.b - 100 > 0 else 100),

                             (self.rect.h * 0.05 + self.font.size(self.text[:self.cursor])[0] +
                              self.font.size(self.text[:self.cursor])[1] * 0.1,
                              (self.rect.h // 2 - self.size[1] // 2)),
                             (self.rect.h * 0.05 + self.font.size(self.text[:self.cursor])[0] +
                              self.font.size(self.text[:self.cursor])[1] * 0.1,
                              (self.rect.h // 2 - self.size[1] // 2) + (
                                          self.rect.h - (self.rect.h // 2 - self.size[1] // 2) * 2)),
                             int(self.font.size(self.text[:self.cursor])[1] * 0.1))

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False


class Notification(pygame.sprite.Sprite):
    def __init__(self, rect, text, background, around, font_color):
        pygame.sprite.Sprite.__init__(self)
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
        self.step = self.StartRect.h // 4
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
            self.font = pygame.font.SysFont('notosans', s)
            self.size = list(self.font.size(self.max))
            self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
            if self.size[0] >= self.NotificationRect.w * 0.9 or self.size[1] >= self.NotificationRect.h * 0.9:
                self.font = pygame.font.SysFont('notosans', s - 1)
                self.size = list(self.font.size(self.max))
                self.StartSize = self.font.size(self.max)
                self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
                break

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide():
            if mouse:
                self.end = True
        if not self.StartTime and self.NotificationRect.y < self.StartRect.y:
            if self.NotificationRect.y + self.step >= self.StartRect.y:
                self.NotificationRect.y = self.StartRect.y
                self.StartTime = time.time()
            else:
                self.NotificationRect.y += self.step
        elif (time.time() - self.height_font > self.StartTime and self.NotificationRect.y >= self.rect.y - self.StartRect.h and not self.isCollide()) or (
                self.end and self.NotificationRect.y >= self.rect.y - self.StartRect.h):
            self.NotificationRect.y -= self.step
        elif (time.time() - self.height_font > self.StartTime and self.NotificationRect.y < self.rect.y - self.StartRect.h) or (
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
                self.rect.w * 0.1, self.NotificationRect.y + self.NotificationRect.h * 0.1 + self.StartSize[1] * self.draw_point))
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

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.around), (0, 0))
        self.image.blit(
            RoundedRect((0, 0, (self.rect.w - self.rect.h * 0.1) * self.value, self.rect.h - self.rect.h * 0.1),
                        self.progress_color), (self.rect.h * 0.06, self.rect.h * 0.06))


clock = pygame.time.Clock()

run = True
sock = None
mouse_left_press = False
NotificationLeftPress = False
key_esc = False
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass
pygame.font.init()
size = [get_monitors()[0].width, get_monitors()[0].height]
global_size = size
attitude = list(map(lambda x: x//math.gcd(*size), size))
screen = pygame.Surface(size, pygame.SRCALPHA)
scrn = pygame.display.set_mode(pygame.display.list_modes()[0], pygame.FULLSCREEN, pygame.HWSURFACE)
pygame.display.set_caption('Ocean Ship Wars')
ico = b"\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xe3\xe3\xe3\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff"
pygame.display.set_icon(pygame.image.fromstring(ico, (70,70), 'RGBA'))
KILLED_SHIP = (60, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
theme = 0
version = 0.10
FromGitVersion = requests.get('https://raw.githubusercontent.com/AlexKim0710/OceanShipsWar/main/version').text[:-1]
bsize = size[0] // 27.428571428571427
ships_wh = int(bsize // 7)
left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
font = pygame.font.SysFont('notosans', int(bsize / 1.5))
infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
blocks = {}
build_ship = False
build_y = False
ship = 0
doSelect = True
create_ship = None
ships = {1: {}, 2: {}, 3: {}, 4: {}}
ships_env = []
quadro_ship = 1
trio_ship = 2
duo_ship = 3
solo_ship = 4
great_build = False
ERRORS = []
LegitBuild = True
block_block_num = False
quadro_ship_rect = None
quadro_ship_env = None
DrawCursor = True
BUILD = True
killed_enemy = False
is_adm = None
room = True
create_game = False
join_game = False
settings = False
game = False
end_game = False
Sounds = {}
MaxStartLoad = 0
StartLoaded = 0
FineLoadGame = True
ConditionOfLoad = False
solo, duo, trio, quadro = 0, 0, 0, 0
send_data = {'ships': {1: {}, 2: {}, 3: {}, 4: {}},
             'count': 0,
             'selects': [],
             'killed': {'blocks': [], 'ships': []},
             'die': {'blocks': [], 'ships': []},
             'move': 'build',
             'end game': False,
             'pass': False,
             'event': []}
input_data = send_data
GameSettings = {'Sound': True,
                'Notification Sound': True,
                'Notification SoundVol': 1,
                'Game Sound': True,
                'Game SoundVol': 1,
                'Language': 'rus',
                'Window size': size,
                'my socket': ['', 0],
                'enemy socket': ['', 0]}

if os.path.exists('settings.json'):
    try:
        with open('settings.json') as f:
            GameSettings = json.loads(f.read())
            GameSettings['my socket'], GameSettings['enemy socket'] = [['', 0]]*2
    except json.decoder.JSONDecodeError as err:
        ERRORS.append(f'Ошибка инициализации json конфига\tСтрока:{err.lineno}, столбец:{err.colno}, символ:{err.pos}|ошибка:{err.msg}')

SettingsButtons = pygame.sprite.Group()
Switches = pygame.sprite.Group()
Lists = pygame.sprite.Group()
Slides = pygame.sprite.Group()
settings_upper_margin = 0.2
settings_wheel = settings_upper_margin
sprites = pygame.sprite.Group()
SystemButtons = pygame.sprite.Group()
CreateGameButtons = pygame.sprite.Group()
JoinGameButtons = pygame.sprite.Group()
Notifications = pygame.sprite.Group()
LoadGameGroup = pygame.sprite.Group()
letters = []

# import pyperclip
#
# PUNCTUATION = list('''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ''')
#
#
# def RoundedRect(rect, color, radius=0.4) -> pygame.Surface:
#     """
#     RoundedRect(surface,rect,color,radius=0.4)
#
#     surface : destination
#     rect    : rectangle
#     color   : rgb or rgba
#     radius  : 0 <= radius <= 1
#     """
#
#     rect = pygame.Rect(0, 0, rect[2], rect[3])
#     color = pygame.Color(*color)
#     alpha = color.a
#     color.a = 0
#     rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)
#
#     circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
#     pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
#     circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)
#
#     radius = rectangle.blit(circle, (0, 0))
#     radius.bottomright = rect.bottomright
#     rectangle.blit(circle, radius)
#     radius.topright = rect.topright
#     rectangle.blit(circle, radius)
#     radius.bottomleft = rect.bottomleft
#     rectangle.blit(circle, radius)
#
#     rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
#     rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))
#
#     rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
#     rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)
#
#     return rectangle
#
#
# class button(pygame.sprite.Sprite):
#     def __init__(self, rect, text, color1, color2, text_color, color1_act, color2_act, color_act_text):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
#         self.color1 = pygame.Color(color1)
#         self.color2 = pygame.Color(color2)
#         self.color1_act = pygame.Color(color1_act)
#         self.color2_act = pygame.Color(color2_act)
#         self.text_color = pygame.Color(text_color)
#         self.color_act_text = pygame.Color(color_act_text)
#         self.text = text
#         for s in range(1000):
#             self.font = pygame.font.SysFont('notosans', s)
#             self.size = self.font.size(self.text)
#             if self.size[0] >= self.rect.w - self.rect.h * 0.1 * 4 or self.size[
#                 1] >= self.rect.h - self.rect.h * 0.1 * 4:
#                 self.font = pygame.font.SysFont('notosans', s - 1)
#                 self.size = self.font.size(self.text)
#                 break
#
#     def update(self):
#         if self.isCollide():
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color1_act), (0, 0))
#             self.image.blit(
#                 RoundedRect((0, 0, self.rect.w - self.rect.h * 0.1, self.rect.h - self.rect.h * 0.1),
#                             self.color2_act), (self.rect.h * 0.06, self.rect.h * 0.06))
#             self.image.blit(self.font.render(self.text, True, self.color_act_text),
#                             (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
#         else:
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color1), (0, 0))
#             self.image.blit(
#                 RoundedRect((0, 0, self.rect.w - self.rect.h * 0.1, self.rect.h - self.rect.h * 0.1),
#                             self.color2), (self.rect.h * 0.06, self.rect.h * 0.06))
#             self.image.blit(self.font.render(self.text, True, self.text_color),
#                             (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
#
#     def isCollide(self):
#         if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
#                 pygame.mouse.get_pos()[
#                     1] < self.rect.y + self.rect.height:
#             return True
#         else:
#             return False
#
#
# class switch(pygame.sprite.Sprite):
#     def __init__(self, rect, color_on, color_off, background, name, power=False):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
#         self.color_on = pygame.Color(color_on)
#         self.color_off = pygame.Color(color_off)
#         self.background = pygame.Color(background)
#         self.name = name
#         self.power = power
#
#     def isCollide(self):
#         if self.rect.collidepoint(pygame.mouse.get_pos()):
#             return True
#         else:
#             return False
#
#     def update(self, mouse):
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         if self.power:
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
#             # self.image.blit(RoundedRect((0,0,self.rect.w-self.rect.w*0.2,self.rect.h-self.rect.h*0.2),self.background,1),(self.rect.w*0.1,self.rect.h*0.1))
#             pygame.draw.circle(self.image, self.color_on, (self.rect.w / 2 + self.rect.h * 0.55, self.rect.h / 2),
#                                self.rect.h / 2 - self.rect.h * 0.1)
#         elif not self.power:
#             # self.image.blit(RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.background, 1),(self.rect.w * 0.1, self.rect.h * 0.1))
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
#             pygame.draw.circle(self.image, self.color_off, (self.rect.w / 2 - self.rect.h / 2, self.rect.h / 2),
#                                self.rect.h / 2 - self.rect.h * 0.1)
#         if self.isCollide() and mouse:
#             self.power = not self.power
#             return self.name
#
#
# class label(pygame.sprite.Sprite):
#     def __init__(self, rect, text, color, text_color, center=False):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.text = text
#         self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
#         self.color = pygame.Color(color)
#         self.text_color = pygame.Color(text_color)
#         self.center = center
#         if self.center:
#             for s in range(1000):
#                 self.font = pygame.font.SysFont('notosans', s)
#                 self.size = self.font.size(self.text)
#                 if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
#                     self.font = pygame.font.SysFont('notosans', s - 1)
#                     self.size = self.font.size(self.text)
#                     break
#         else:
#             for s in range(1000):
#                 self.font = pygame.font.SysFont('notosans', s)
#                 self.size = self.font.size(self.text)
#                 if self.size[0] > self.rect.w - self.rect.w * 0.1 or self.size[1] > self.rect.h:
#                     self.font = pygame.font.SysFont('notosans', s - 1)
#                     self.size = self.font.size(self.text)
#                     break
#
#     def update(self):
#         if self.size != self.font.size(self.text):
#             if self.center:
#                 for s in range(1000):
#                     self.font = pygame.font.SysFont('notosans', s)
#                     self.size = self.font.size(self.text)
#                     if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
#                         self.font = pygame.font.SysFont('notosans', s - 1)
#                         self.size = self.font.size(self.text)
#                         break
#             else:
#                 for s in range(1000):
#                     self.font = pygame.font.SysFont('notosans', s)
#                     self.size = self.font.size(self.text)
#                     if self.size[0] > self.rect.w - self.rect.w * 0.1 or self.size[1] > self.rect.h:
#                         self.font = pygame.font.SysFont('notosans', s - 1)
#                         self.size = self.font.size(self.text)
#                         break
#         self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
#         self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, 1), (0, 0))
#         self.image.blit(self.font.render(self.text, True, self.text_color),
#                         (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
#
#
# class Slide(pygame.sprite.Sprite):
#     def __init__(self, rect, slide_color, background, base_data, name):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.slide_color = pygame.Color(slide_color)
#         self.background = pygame.Color(background)
#         self.base_data = base_data
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         self.name = name
#
#     def update(self, mouse):
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
#         self.image.blit(RoundedRect((0, 0, self.rect.w * self.base_data, self.rect.h),
#                                     (255 - self.background[0], 255 - self.background[1], 255 - self.background[2]), 1),
#                         (0, 0))
#         pygame.draw.circle(self.image, self.slide_color,
#                            (self.rect.w * self.base_data - self.rect.h / 2, self.rect.h / 2), self.rect.h / 2, 0)
#         if mouse and self.isCollide():
#             self.base_data = self.isCollide()
#             return self.name, self.base_data
#         return False
#
#     def isCollide(self):
#         if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.w and self.rect.y < pygame.mouse.get_pos()[1] < self.rect.y + self.rect.h:
#             return round((pygame.mouse.get_pos()[0] - self.rect.x) / self.rect.w, 1)
#         else:
#             return False
#
#
# class List(pygame.sprite.Sprite):
#     def __init__(self, rect, base_text, texts, text_color, background, bg_list, name):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.name = name
#         self.base_text = base_text
#         self.texts = texts
#         self.text_color = text_color
#         self.bg_list = bg_list
#         self.background = background
#         self.active = False
#         for s in range(1000):
#             self.font = pygame.font.SysFont('notosans', s)
#             self.size = self.font.size(self.base_text)
#             if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
#                 self.font = pygame.font.SysFont('notosans', s - 1)
#                 self.size = self.font.size(self.base_text)
#                 break
#         self.image = pygame.Surface(
#             (self.rect.w, self.rect.h + self.size[1] * len(self.texts) + self.size[1] * 0.1 * len(self.texts)),
#             pygame.SRCALPHA)
#
#     def update(self, mouse):
#         if mouse and self.isCollide():
#             if self.active:
#                 a = f'{self.name}:{self.isCollide()}'
#                 self.active = not self.active
#                 return a
#             else:
#                 self.active = not self.active
#         self.image = pygame.Surface(
#             (self.rect.w, self.rect.h + self.size[1] * len(self.texts)),
#             pygame.SRCALPHA)
#         if self.active:
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
#             self.image.blit(self.font.render(self.base_text, True, self.text_color),
#                             (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
#             # self.image.blit(RoundedRect((0,0,self.rect.w,self.size[1] * len(self.texts)),self.bg_list,0.5),(0,self.rect.h))
#             for n, tx in enumerate(self.texts):
#                 self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), (255, 255, 255), 0.5),
#                                 (0, self.rect.h + self.rect.h * n))
#                 self.image.blit(
#                     RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.bg_list,
#                                 0.5), (self.rect.w * 0.06, (self.rect.h + self.rect.h * n) + self.rect.h * 0.05))
#                 self.image.blit(self.font.render(tx, True, self.text_color), (self.rect.w // 2 - self.size[0] // 2,
#                                                                               self.rect.h + self.rect.h * n + 1 - self.rect.h // 2 - self.rect.h * 0.05 +
#                                                                               self.size[1] // 2))
#         else:
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
#             self.image.blit(self.font.render(self.base_text, True, self.text_color),
#                             (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
#
#     def isCollide(self):
#         if self.active:
#             for n, rc in enumerate(self.texts):
#                 if self.rect.bottomleft[0] < pygame.mouse.get_pos()[0] < self.rect.bottomright[0] and \
#                         self.rect.bottomleft[1] + \
#                         self.size[1] * n < pygame.mouse.get_pos()[1] < self.rect.bottomright[1] + self.size[1] * (
#                         n + 1):
#                     return rc
#                 elif self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
#                         pygame.mouse.get_pos()[
#                             1] < self.rect.y + self.rect.height:
#                     return self.base_text
#             else:
#                 return False
#         else:
#             if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
#                     pygame.mouse.get_pos()[
#                         1] < self.rect.y + self.rect.height:
#                 return True
#             else:
#                 return False
#
#
# class TextInput(pygame.sprite.Sprite):
#     def __init__(self, rect, background, around, text_color, name, base_text='', text=''):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.rectInner = pygame.Rect(self.rect.h * 0.04, self.rect.h * 0.04, self.rect.w - self.rect.h * 0.1,
#                                      self.rect.h - self.rect.h * 0.1)
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         self.background = pygame.Color(background)
#         self.around = pygame.Color(around)
#         self.text_color = pygame.Color(text_color)
#         self.base_text = base_text
#         self.text = text
#         self.active = False
#         self.cursor = 0
#         self.name = name
#         for s in range(0, 1000):
#             self.font = pygame.font.SysFont('notosans', s)
#             self.size = self.font.size(self.text if self.text else self.base_text)
#             if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
#                 1] >= self.rectInner.h * 0.8 - self.rectInner.y:
#                 self.font = pygame.font.SysFont('notosans', s - 1)
#                 self.size = self.font.size(self.text if self.text else self.base_text)
#                 break
#
#     def update(self, event):
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         if self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and not self.active:
#             if event.button == 1:
#                 self.active = True
#                 pygame.key.start_text_input()
#                 pygame.key.set_repeat(500, 50)
#         elif not self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and self.active:
#             if event.button == 1:
#                 self.active = False
#                 pygame.key.set_repeat(0, 0)
#                 pygame.key.stop_text_input()
#                 return f'{self.name}:{self.text}'
#         if self.active:
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_BACKSPACE and self.cursor:
#                     if pygame.key.get_mods() & pygame.KMOD_LCTRL:
#                         for n, sim in enumerate(self.text[::-1]):
#                             if sim in PUNCTUATION:
#                                 self.text = self.text[:self.cursor - (n if n != 0 else 1)] + self.text[self.cursor:]
#                                 self.cursor -= n if n != 0 else 1
#                                 break
#                         else:
#                             self.text = ''
#                             self.cursor = 0
#                     else:
#                         self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
#                         self.cursor -= 1
#                 elif event.key == pygame.K_LEFT:
#                     if pygame.key.get_mods() & pygame.KMOD_LCTRL:
#                         for n, sim in enumerate(self.text[:self.cursor][::-1]):
#                             if sim in PUNCTUATION:
#                                 self.cursor -= n if n != 0 else 1
#                                 break
#                         else:
#                             self.cursor = 0
#                     elif self.cursor - 1 >= 0:
#                         self.cursor -= 1
#                 elif event.key == pygame.K_RIGHT:
#                     if pygame.key.get_mods() & pygame.KMOD_LCTRL:
#                         for n, sim in enumerate(self.text[self.cursor:]):
#                             if sim in PUNCTUATION:
#                                 self.cursor += n if n != 0 else 1
#                                 break
#                         else:
#                             self.cursor = len(self.text)
#                     elif self.cursor + 1 <= len(self.text):
#                         self.cursor += 1
#                 elif event.key == pygame.K_DELETE:
#                     if pygame.key.get_mods() & pygame.KMOD_LCTRL:
#                         for n, sim in enumerate(self.text[self.cursor:]):
#                             if sim in PUNCTUATION:
#                                 self.text = self.text[:self.cursor] + self.text[self.cursor + n if n != 0 else 1:]
#                                 break
#                         else:
#                             self.text = self.text[:self.cursor]
#                     else:
#                         self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
#                 elif event.key == pygame.K_HOME:
#                     self.cursor = 0
#                 elif event.key == pygame.K_END:
#                     self.cursor = len(self.text)
#                 elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # or event.key == pygame.K_ESCAPE
#                     self.active = False
#                     pygame.key.set_repeat(0, 0)
#                     pygame.key.stop_text_input()
#                     return f'{self.name}:{self.text}'
#                 elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_LCTRL:
#                     paste_text = pyperclip.paste()
#                     if paste_text:
#                         self.text = self.text = self.text[:self.cursor] + paste_text + self.text[self.cursor:]
#                         self.cursor += len(paste_text)
#             if event.type == pygame.TEXTINPUT:
#                 self.text = self.text[:self.cursor] + event.text + self.text[self.cursor:]
#                 self.cursor += 1 if event.text else 0
#             for s in range(0, 1000):
#                 self.font = pygame.font.SysFont('notosans', s)
#                 self.size = self.font.size(self.text if self.text else self.base_text)
#                 if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
#                     1] >= self.rectInner.h * 0.8 - self.rectInner.y:
#                     self.font = pygame.font.SysFont('notosans', s - 1)
#                     self.size = self.font.size(self.text if self.text else self.base_text)
#                     break
#         if self.active:
#             self.image.blit(RoundedRect(self.rect, (0, 255, 0), .5), (0, 0))
#             self.image.blit(
#                 RoundedRect((0, 0, self.rectInner.w + self.rectInner.x, self.rectInner.h + self.rectInner.y),
#                             self.background, .5),
#                 (self.rectInner.x, self.rectInner.y))
#         else:
#             self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.around, .5), (0, 0))
#             self.image.blit(
#                 RoundedRect((0, 0, self.rectInner.w + self.rectInner.x, self.rectInner.h + self.rectInner.y),
#                             self.background, .5),
#                 (self.rectInner.x, self.rectInner.y))
#
#         if self.text:
#             self.image.blit(self.font.render(self.text, True, self.text_color),
#                             (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))
#         else:
#             self.image.blit(
#                 self.font.render(self.base_text, True, (self.text_color.r - 100 if self.text_color.r - 100 > 0 else 100,
#                                                         self.text_color.g - 100 if self.text_color.g - 100 > 0 else 100,
#                                                         self.text_color.b - 100 if self.text_color.b - 100 > 0 else 100)),
#                 (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))
#
#         if self.active:
#             pygame.draw.line(self.image,
#                              (self.background.r - 100 if self.background.r - 100 > 0 else 100,
#                               self.background.g - 100 if self.background.g - 100 > 0 else 100,
#                               self.background.b - 100 if self.background.b - 100 > 0 else 100),
#
#                              (self.rect.h * 0.05 + self.font.size(self.text[:self.cursor])[0] +
#                               self.font.size(self.text[:self.cursor])[1] * 0.1,
#                               (self.rect.h // 2 - self.size[1] // 2)),
#                              (self.rect.h * 0.05 + self.font.size(self.text[:self.cursor])[0] +
#                               self.font.size(self.text[:self.cursor])[1] * 0.1,
#                               (self.rect.h // 2 - self.size[1] // 2) + (
#                                           self.rect.h - (self.rect.h // 2 - self.size[1] // 2) * 2)),
#                              int(self.font.size(self.text[:self.cursor])[1] * 0.1))
#
#     def isCollide(self):
#         if self.rect.collidepoint(pygame.mouse.get_pos()):
#             return True
#         else:
#             return False
#
#
# class Notification(pygame.sprite.Sprite):
#     def __init__(self, rect, text, background, around, font_color):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect[0], rect[1] - rect[3], rect[2], rect[3] * 3)
#         self.NotificationRect = pygame.Rect(rect)
#         self.StartRect = pygame.Rect(rect)
#         self.NotificationRect.y = -rect[1]
#         self.NotificationRect.x = 0
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         self.background = pygame.Color(background)
#         self.background.a = 240
#         self.around = pygame.Color(around)
#         self.FontColor = pygame.Color(font_color)
#         self.text = {}
#         self.StartTime = None
#         self.end = False
#         self.height_font = 0
#         self.step = self.StartRect.h // 4
#         self.max = ''  # max(max(self.text.values()))
#         self.draw_point = 0
#         for n, element in enumerate(str(text).split('\t')):
#             string_n = element.split(' ')
#             self.text[n] = [' '.join(string_n[x:x + 5]) for x in range(0, len(string_n), 5)]
#             self.height_font += len(self.text[n]) + 0.5
#         for el in max(self.text.values()):
#             if len(self.max) < len(el):
#                 self.max = el
#
#         for s in range(0, 1000):
#             self.font = pygame.font.SysFont('notosans', s)
#             self.size = list(self.font.size(self.max))
#             self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
#             if self.size[0] >= self.NotificationRect.w * 0.9 or self.size[1] >= self.NotificationRect.h * 0.9:
#                 self.font = pygame.font.SysFont('notosans', s - 1)
#                 self.size = list(self.font.size(self.max))
#                 self.StartSize = self.font.size(self.max)
#                 self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
#                 break
#
#     def update(self, mouse):
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         if self.isCollide():
#             if mouse:
#                 self.end = True
#         if not self.StartTime and self.NotificationRect.y < self.StartRect.y:
#             if self.NotificationRect.y + self.step >= self.StartRect.y:
#                 self.NotificationRect.y = self.StartRect.y
#                 self.StartTime = time.time()
#             else:
#                 self.NotificationRect.y += self.step
#         elif (time.time() - self.height_font > self.StartTime and self.NotificationRect.y >= self.rect.y - self.StartRect.h and not self.isCollide()) or (
#                 self.end and self.NotificationRect.y >= self.rect.y - self.StartRect.h):
#             self.NotificationRect.y -= self.step
#         elif (time.time() - self.height_font > self.StartTime and self.NotificationRect.y < self.rect.y - self.StartRect.h) or (
#                 self.NotificationRect.y <= self.rect.y - self.StartRect.h and self.end):
#             self.kill()
#             return True
#         self.image.blit(RoundedRect(self.NotificationRect, self.background, 0.3), (0, self.NotificationRect.y))
#         self.draw_point = 0
#         for point in self.text:
#             pygame.draw.circle(self.image, self.FontColor, (self.rect.w * 0.03,
#                                                             self.NotificationRect.y + self.NotificationRect.h * 0.1 +
#                                                             self.StartSize[1] * self.draw_point + self.StartSize[
#                                                                 1] // 2), self.StartSize[1] * 0.2)
#             for text in self.text[point]:
#                 self.image.blit(self.font.render(text, True, self.FontColor), (
#                 self.rect.w * 0.1, self.NotificationRect.y + self.NotificationRect.h * 0.1 + self.StartSize[1] * self.draw_point))
#                 self.draw_point += 1
#             self.draw_point += 0.5
#
#     def isCollide(self):
#         mouse_pos = pygame.mouse.get_pos()
#         if self.rect.x <= mouse_pos[0] <= self.rect.x + self.rect.w and self.NotificationRect.y + self.rect.y <= \
#                 mouse_pos[1] <= self.NotificationRect.y + self.NotificationRect.h + self.rect.y:
#             return True
#         else:
#             return False
#
#
# class ProgressBar(pygame.sprite.Sprite):
#     def __init__(self, rect, around, progress_color, value):
#         pygame.sprite.Sprite.__init__(self)
#         self.rect = pygame.Rect(rect)
#         self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         self.around = pygame.Color(around)
#         self.progress_color = pygame.Color(progress_color)
#         self.value = value
#
#     def update(self):
#         self.image.blit(RoundedRect(self.rect, self.around), (0, 0))
#         self.image.blit(
#             RoundedRect((0, 0, (self.rect.w - self.rect.h * 0.1) * self.value, self.rect.h - self.rect.h * 0.1),
#                         self.progress_color), (self.rect.h * 0.06, self.rect.h * 0.06))


def re_lang(lang='rus'):
    global GameLanguage
    if lang == 'rus':
        GameLanguage = {'start game': 'Создать игру',
                        'join game': 'Присоеденится к игре',
                        'settings': 'Настройки',
                        'theme light': 'Яркая',
                        'theme dark': 'Тёмная',
                        'Settings Sound': 'Звук',
                        'Settings Game Sound': 'Звуки игры',
                        'Settings Notification Sound': 'Звуки уведомлений',
                        'Settings Sound Slide': 'Громкость',
                        'Settings Language': 'Язык',
                        'Exit': 'Выход',
                        'version': f'Версия {version}'}
    else:
        GameLanguage = {'start game': 'Create game',
                        'join game': 'Join to game',
                        'settings': 'Settings',
                        'theme light': 'Light',
                        'theme dark': 'Dark',
                        'Settings Sound': 'Sound',
                        'Settings Game Sound': 'Game Sound',
                        'Settings Notification Sound': 'Notifications Sound',
                        'Settings Sound Slide': 'Volume',
                        'Settings Language': 'Language',
                        'Exit': 'Exit',
                        'version': f'Version {version}'}


re_lang()


def GetRect(cords: tuple) -> pygame.Rect:
    if cords:
        return pygame.Rect(blocks[cords[0]][cords[1]])
    else:
        return False


def GetShip(cords: tuple) -> pygame.Rect:
    if cords:
        cords0 = GetRect(cords[0])
        cords1 = GetRect(cords[1])
        if cords0[1] == cords1[1]:
            return pygame.Rect(*cords0.topleft, cords1.x - cords0.x + bsize, bsize)
        else:
            return pygame.Rect(*cords0.topleft, bsize, cords1.y - cords0.y + bsize)

    else:
        return False


def GetShipEnv(cords: tuple) -> pygame.Rect:
    if cords:
        return pygame.Rect(cords[0] - bsize, cords[1] - bsize, cords[2] + bsize * 2, cords[3] + bsize * 2)
    else:
        return cords


def GetShipBlocks(cords: tuple) -> list:
    if cords:
        cord = []
        if cords[0][0] == cords[1][0]:
            for pos in range(cords[0][1], cords[1][1] + 1):
                cord.append((cords[0][0], pos))
        else:
            for pos in range(cords[0][0], cords[1][0] + 1):
                cord.append((pos, cords[0][1]))
        return cord


def re_theme():
    global ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, EscButton, SettingsMainLabel, RoomQuit, \
        CreateGameMainLabel, TextInputCr, TextInputJn, CreateGameWaitUser, JoinGameMainLabel, JoinGameWaitUser, BACKGROUND, LINES, KILLED_SHIP, Update, \
        StartLoadProgress, StartLoadLabel, StartLoadLabel2
    if theme:
        KILLED_SHIP = (200, 200, 200)
        LINES = pygame.Color(24, 24, 24)
        BACKGROUND = (227, 227, 227)
        ButtonsCl1 = (177, 220, 237)
        ButtonsCl2 = (255, 255, 255)
        ButtonsTxtColor = (64, 64, 64)
        ButtonsAtcCol1 = (255, 255, 255)
        ButtonsAtcCol2 = (127, 127, 127)
        ButtonsClActT = (0, 0, 0)
        TextInputArCl = (0, 255, 255)
        TextInputTxCl = (0, 0, 0)
    else:
        KILLED_SHIP = (60, 60, 60)
        LINES = pygame.Color(255, 255, 255)
        BACKGROUND = (24, 24, 24)
        ButtonsCl1 = (255, 255, 255)
        ButtonsCl2 = (0, 0, 0)
        ButtonsTxtColor = (255, 255, 255)
        ButtonsAtcCol1 = (255, 255, 255)
        ButtonsAtcCol2 = (127, 127, 127)
        ButtonsClActT = (0, 0, 0)
        TextInputArCl = (0, 0, 100)
        TextInputTxCl = (255, 255, 255)
    StartLoadProgress = ProgressBar(
        (size[0]//2-size[0]*0.2/2,size[1]*0.7,size[0]*0.2,size[1]*0.05), LINES, (0, 255, 0), 0)
    StartLoadLabel = label((size[0]//2-size[0]*0.2/2,size[1]*0.6,size[0]*0.2,size[1]*0.05),'0 %',(0,0,0,0),(0,255,0), True)
    StartLoadLabel2 = label((size[0]//2-size[0]*0.2/2,size[1]*0.65,size[0]*0.2,size[1]*0.05),'',(0,0,0,0),(0,255,0), True)
    Update = button((-1, size[1] - bsize // 2, bsize * 2, bsize // 2), str(GameLanguage['version']), ButtonsCl1,
                    ButtonsCl2, ButtonsTxtColor,
                    ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    TextInputCr = TextInput(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
         size[1] * 0.1), BACKGROUND, TextInputArCl, TextInputTxCl, 'create', '192.168.1.1',
        GameSettings['my socket'][0])
    TextInputJn = TextInput(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
         size[1] * 0.1), BACKGROUND, TextInputArCl, TextInputTxCl, 'join', '192.168.1.1',
        GameSettings['my socket'][0])
    CreateGameWaitUser = label(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
         size[1] * 0.1), f'Ждем соперника... Ваш адрес: {GameSettings["my socket"][0]}:{GameSettings["my socket"][1]}', BACKGROUND, (0, 255, 255))
    JoinGameWaitUser = label(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
         size[1] * 0.1), f'Ждем соперника... Адрес будущего соперника: {GameSettings["enemy socket"][0]}:{GameSettings["enemy socket"][1]}', BACKGROUND,
        (255, 0, 255))
    SettingsMainLabel = label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                              GameLanguage['settings'], BACKGROUND, LINES)
    CreateGameMainLabel = label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                GameLanguage['start game'], BACKGROUND, LINES)
    JoinGameMainLabel = label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                              GameLanguage['join game'], BACKGROUND, LINES)
    RoomQuit = button((size[0] - bsize + 1, -1, bsize, bsize),
                      GameLanguage['Exit'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                      ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    EscButton = button((-1, -1, (bsize + bsize * 0.5) // 2, bsize // 2), 'ESC', ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                       ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonAdm = button(
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.3 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['start game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonClient = button(
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['join game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonSettings = button(
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.7 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['settings'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonTheme = button((size[0] - bsize - bsize // 2, size[1] - bsize - bsize // 2, bsize, bsize),
                         GameLanguage['theme light'] if theme else GameLanguage['theme dark'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                         ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    sprites.empty()
    SystemButtons.empty()
    CreateGameButtons.empty()
    JoinGameButtons.empty()
    LoadGameGroup.empty()
    SystemButtons.add(EscButton, SettingsMainLabel, CreateGameMainLabel, CreateGameWaitUser, JoinGameMainLabel,
                      JoinGameWaitUser)
    CreateGameButtons.add(TextInputCr)
    JoinGameButtons.add(TextInputJn)
    sprites.add(ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, RoomQuit, Update)
    LoadGameGroup.add(StartLoadProgress,StartLoadLabel, StartLoadLabel2)


re_theme()
# easygui.fileopenbox(filetypes=["*.json"], multiple=True)
SOLO = 4
DUO = 3
TRIO = 2
QUADRO = 1


def draw_ship_count(ships_count, max_ships=[SOLO,DUO,TRIO,QUADRO]):
    mid = [size[0] // 2 + size[0] // 2 // 2, size[1] // 2 - size[1] // 2 // 1.5]
    for type_ship in range(len(ships_count)):
        counter_block_num = 0
        for num_block in range(((max_ships[type_ship] * (type_ship + 1)) * 2 - 1) if max_ships[type_ship] > 1 else max_ships[type_ship] * type_ship + 1):
            if counter_block_num < type_ship+1:
                if ships_count[type_ship]:
                    color = LINES
                else:
                    color = KILLED_SHIP
                counter_block_num += 1
            else:
                color = BACKGROUND
                counter_block_num = 0
                ships_count[type_ship] -= 1 if ships_count[type_ship] else 0
            pygame.draw.rect(screen, color, (mid[0] + num_block * (bsize // 2), mid[1] + bsize * (type_ship+1), bsize // 2, bsize // 2), ships_wh//3)


def draw():
    global letters
    if GameSettings['Language'] == 'eng':
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    elif GameSettings['Language'] == 'rus':
        letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И']
    for it in range(11):
        # Hor grid1
        pygame.draw.line(screen, LINES, (left_margin, upper_margin + it * bsize),
                         (left_margin + 10 * bsize, upper_margin + it * bsize), 1)
        # Vert grid1
        pygame.draw.line(screen, LINES, (left_margin + it * bsize, upper_margin),
                         (left_margin + it * bsize, upper_margin + 10 * bsize), 1)
        if it < 10:
            num = font.render(str(it + 1), True, LINES)
            letter = font.render(letters[it], True, LINES)
            num_ver_width = num.get_width()
            num_ver_height = num.get_height()
            letters_hor_width = letter.get_width()

            # Ver num grid1
            screen.blit(num, (left_margin - (bsize // 2 + num_ver_width // 2),
                              upper_margin + it * bsize + (bsize // 2 - num_ver_height // 2)))
            # Hor letters grid1
            screen.blit(letter, (left_margin + it * bsize + (bsize //
                                                             2 - letters_hor_width // 2),
                                 upper_margin - font.size(letters[it])[1] * 1.2))


draw()

for num_let in range(len(letters)):
    blocks[num_let] = []
    for num in range(len(letters)):
        blocks[num_let].append(pygame.Rect(left_margin + num_let * bsize, upper_margin + num * bsize, bsize, bsize))


def re_settings_button():
    global settings_pad
    set_of_settings = {
        'up margin': 0,
        'down margin': 1.9,
        'label': ((0, 255, 255),(0, 0, 0)),
        'switches': ((0, 255, 0), (255, 255, 255), (64, 64, 64)),
        'slides':((255, 255, 255), (24, 24, 24)),
        'lists':((255, 255, 255), (255, 0, 255), (0, 0, 0)),
    }
    pad = settings_wheel
    SettingsButtons.empty()
    Switches.empty()
    Lists.empty()
    Slides.empty()
    if 0 < pad < 1.9:
        SoundOnOffButton = label(
            (size[0] // 2 - size[0] // 1.92 // 2, size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
            GameLanguage['Settings Sound'],
            *set_of_settings['label'])
        SwitchSoundOnOff = switch(
            (SoundOnOffButton.rect.x + SoundOnOffButton.rect.w - (
                    SoundOnOffButton.rect.h * 2 - SoundOnOffButton.rect.h * 0.1) - 1,
             SoundOnOffButton.rect.y + 1,
             SoundOnOffButton.rect.h * 2 - SoundOnOffButton.rect.h * 0.1,
             SoundOnOffButton.rect.h - 2), *set_of_settings['switches'],
            'Sound', GameSettings['Sound'])
        Switches.add(SwitchSoundOnOff)
        SettingsButtons.add(SoundOnOffButton)
    pad += 0.1
    if GameSettings['Sound']:
        if 0 < pad < 1.9:
            NotificationOnOffButton = label((size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.1,
                                                     size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                                                    GameLanguage['Settings Notification Sound'], *set_of_settings['label'])
            SwitchNotificationOnOff = switch(
                (NotificationOnOffButton.rect.x + NotificationOnOffButton.rect.w - (
                        NotificationOnOffButton.rect.h * 2 - NotificationOnOffButton.rect.h * 0.1) - 1,
                 NotificationOnOffButton.rect.y + 1,
                 NotificationOnOffButton.rect.h * 2 - NotificationOnOffButton.rect.h * 0.1,
                 NotificationOnOffButton.rect.h - 2), *set_of_settings['switches'], 'Notification Sound', GameSettings['Notification Sound'])
            SettingsButtons.add(NotificationOnOffButton)
            Switches.add(SwitchNotificationOnOff)
        pad += 0.1
        if GameSettings['Notification Sound']:
            if 0 < pad < 1.9:
                NotificationSlideButton = label(
                    (size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.2,
                     size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                    GameLanguage['Settings Sound Slide'], *set_of_settings['label'])
                SlideNotification = Slide((
                    NotificationSlideButton.rect.x + NotificationSlideButton.rect.w - NotificationSlideButton.rect.h * 10 - 1,
                    NotificationSlideButton.rect.y + 1,
                    (NotificationSlideButton.rect.h * 10),
                    NotificationSlideButton.rect.h - 2),
                    *set_of_settings['slides'], GameSettings['Notification SoundVol'],
                    'Notification SoundVol')
                Slides.add(SlideNotification)
                SettingsButtons.add(NotificationSlideButton)
            pad += 0.1
        if 0 < pad < 1.9:
            GameSoundOnOffButton = label((size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.1,
                                                  size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                                                 GameLanguage['Settings Game Sound'],
                                                 *set_of_settings['label'])
            SwitchGameSoundOnOff = switch(
                (GameSoundOnOffButton.rect.x + GameSoundOnOffButton.rect.w - (
                        GameSoundOnOffButton.rect.h * 2 - GameSoundOnOffButton.rect.h * 0.1) - 1,
                 GameSoundOnOffButton.rect.y + 1,
                 GameSoundOnOffButton.rect.h * 2 - GameSoundOnOffButton.rect.h * 0.1,
                 GameSoundOnOffButton.rect.h - 2), *set_of_settings['switches'], 'Game Sound', GameSettings['Game Sound'])
            SettingsButtons.add(GameSoundOnOffButton)
            Switches.add(SwitchGameSoundOnOff)
        pad += 0.1
        if GameSettings['Game Sound']:
            if 0 < pad < 1.9:
                GameSoundSlideButton = label((size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.2,
                                                      size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                                                     GameLanguage['Settings Sound Slide'], *set_of_settings['label'])
                SlideGameSound = Slide((
                    GameSoundSlideButton.rect.x + GameSoundSlideButton.rect.w - GameSoundSlideButton.rect.h * 10 - 1,
                    GameSoundSlideButton.rect.y + 1,
                    (GameSoundSlideButton.rect.h * 10),
                    GameSoundSlideButton.rect.h - 2),
                    *set_of_settings['slides'], GameSettings['Game SoundVol'],
                    'Game SoundVol')
                SettingsButtons.add(GameSoundSlideButton)
                Slides.add(SlideGameSound)
            pad += 0.1
    if 0 < pad < 1.9:
        LanguageSettings = label(
            (size[0] // 2 - size[0] // 1.92 // 2, size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
            GameLanguage['Settings Language'],
            *set_of_settings['label'])
        LanguageSettingsList = List(
            (LanguageSettings.rect.x + LanguageSettings.rect.w - (
                    LanguageSettings.rect.h * 4 - LanguageSettings.rect.h * 0.1) - 1,
             LanguageSettings.rect.y + 1,
             LanguageSettings.rect.h * 4 - LanguageSettings.rect.h * 0.1,
             LanguageSettings.rect.h - 2),
            GameSettings['Language'], ['eng', 'rus'], *set_of_settings['lists'], 'Language')
        SettingsButtons.add(LanguageSettings)
        Lists.add(LanguageSettingsList)
    pad += 0.1

    if 0 < pad < 1.9:
        ResizeWindow = label(
            (size[0] // 2 - size[0] // 1.92 // 2, size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
            'Размер окна',
            *set_of_settings['label'])
        ResizeWindowList = List(
            (ResizeWindow.rect.x + ResizeWindow.rect.w - (
                    ResizeWindow.rect.h * 4 - ResizeWindow.rect.h * 0.1) - 1,
             ResizeWindow.rect.y + 1,
             ResizeWindow.rect.h * 4 - ResizeWindow.rect.h * 0.1,
             ResizeWindow.rect.h - 2),
            size, pygame.display.list_modes(), *set_of_settings['lists'], 'Window size')
        SettingsButtons.add(ResizeWindow)
        Lists.add(ResizeWindowList)
    for i in range(100):
        if 0 < pad < 1.9:
            SoundOnOffButton = label(
                (size[0] // 2 - size[0] // 1.92 // 2, size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                GameLanguage['Settings Sound'],
                *set_of_settings['label'])
            SwitchSoundOnOff = switch(
                (SoundOnOffButton.rect.x + SoundOnOffButton.rect.w - (
                        SoundOnOffButton.rect.h * 2 - SoundOnOffButton.rect.h * 0.1) - 1,
                 SoundOnOffButton.rect.y + 1,
                 SoundOnOffButton.rect.h * 2 - SoundOnOffButton.rect.h * 0.1,
                 SoundOnOffButton.rect.h - 2), *set_of_settings['switches'],
                'Sound', GameSettings['Sound'])
            Switches.add(SwitchSoundOnOff)
            SettingsButtons.add(SoundOnOffButton)
        else:
            pass
        pad += 0.1

    settings_pad = pad


re_settings_button()


def update_game(ver):
    global run
    mb = 0
    file = requests.get(f'https://github.com/AlexKim0710/OceanShipsWar/releases/download/alpha/OceanShipsWar.{ver}.exe',
                        stream=True)
    with open(f'OceanShipsWar {ver}.exe', 'wb') as f:
        for chunk in file.iter_content(1024 * 1024):
            f.write(chunk)
            mb += 1
    subprocess.Popen(f'OceanShipsWar {ver}.exe')
    run = False


def StartGame():
    global FineLoadGame, Sounds, StartLoaded, MaxStartLoad, ConditionOfLoad
    if pygame.mixer.get_init():
        Sounds = {}
        MaxStartLoad = 0
        StartLoaded = 0
        FineLoadGame = False
        ConditionOfLoad = False
        list_of_load = {
            "info_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/info.wav?raw=true'},
            "killed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/killed.ogg?raw=true'},
            "missed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            "wounded_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/wounded.ogg?raw=true'}
            # "mied_sund":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misd_sund":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss67edsnd":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mis0sesound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missd_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mised_sou678nd":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missedound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_und":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mise_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_o678und":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mssed_sund":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misse_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mssedund":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misdound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mssedsoud":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mid_sond":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misdsound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misses78ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misse87d_ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed367_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misd_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misse ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mised_54sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mssed_und":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misd_s ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misse5d_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed6snd":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "msed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "m issed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed _sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss87d_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss ed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss_0 sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mis9s_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mi 79sed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mis5s_ sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misd6_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misse4d_und":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mis ed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_s ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "msedound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "ssesound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss3_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misund":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "md_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missedsound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mi sd_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "md_sond":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mis_2sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "misseound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "md_so un3d":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss d_so23und":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_s34ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_s3ound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "miss234 ed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mi1 sed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mi 2sed_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_so53und":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missed_23nd":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "missund":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "mis1_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true'},
            # "wounded_sound":{"url":'https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/wounded.ogg?raw=true'}
                        }
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        for var in list_of_load:
            list_of_load[var]['object'] = requests.get(list_of_load[var]['url'], stream=True, timeout=5)
            MaxStartLoad += int(list_of_load[var]['object'].headers['content-length'])/4194304 + 1
            StartLoaded += 1
            ConditionOfLoad = f'Init: ..{("/".join(list_of_load[var]["url"].split("/")[6:]))[:-9]}'

        for var in list_of_load:
            content = b''
            ConditionOfLoad = f'Load: ..{("/".join(list_of_load[var]["url"].split("/")[6:]))[:-9]}'
            for chunk in list_of_load[var]['object'].iter_content(4194304):
                content += chunk
                StartLoaded += len(chunk)/4194304
            Sounds[var] = pygame.mixer.Sound(BytesIO(content))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        FineLoadGame = True
    else:
        GameSettings['Sound'] = False
        ERRORS.append('Ошибка инициализации звука.')
    if version < float(FromGitVersion):
        ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
        threading.Thread(target=update_game, args=[FromGitVersion]).start()
    elif version > float(FromGitVersion):
        ERRORS.append(f'\tПриветствуем участника бетатестирования!.\t')
    return


threading.Thread(target=StartGame).start()


while run:
    key_esc = False
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if create_game:
            for s in CreateGameButtons.sprites():
                u = s.update(event)
                u: str
                if u:
                    u = u.split(':', 1)
                    if u[0] == 'create':
                        try:
                            if ':' in u[1]:
                                u = u[1].split(':', 1)
                                GameSettings['my socket'] = [u[0], int(u[1])]
                            else:
                                GameSettings['my socket'] = [u[1], 9998]
                            me = 'main'
                            not_me = 'client'
                            Enemy_socket = None
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                            sock.bind((GameSettings['my socket'][0], GameSettings['my socket'][1]))
                            sock.setblocking(False)
                            sock.listen(1)
                            re_theme()
                        except Exception as err:
                            ERRORS.append(f'Введите общедоступный IP адрес или хостинг!.\t{err}')
                            GameSettings['my socket'] = ['', 0]
                            re_theme()
        elif join_game:
            for s in JoinGameButtons.sprites():
                u = s.update(event)
                if u:
                    u = u.split(':', 1)
                    if u[0] == 'join':
                        if ':' in u[1]:
                            u = u[1].split(':', 1)
                            GameSettings['my socket'] = [u[0], int(u[1])]
                        else:
                            GameSettings['my socket'] = [u[1], 9998]
        # if event.type == pygame.WINDOWRESIZED:
        #     if event.x != size[0]:
        #         size = (event.x, event.x/attitude[0] * attitude[1])
        #     else:
        #         size = (event.y / attitude[1] * attitude[0], event.y)
        #     screen = pygame.Surface(size, pygame.SRCALPHA)
        #     scrn = pygame.display.set_mode(size, pygame.RESIZABLE)
        #     bsize = size[0] // 27.428571428571427
        #     ships_wh = int(bsize // 7)
        #     left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
        #     font = pygame.font.SysFont('notosans', int(bsize / 1.5))
        #     infoSurface = pygame.Surface(size, pygame.SRCALPHA)
        #     re_theme()
        #     re_settings_button()
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_left_press = True
                NotificationLeftPress = True
            if event.button == 4 and settings_wheel <= settings_upper_margin and settings_wheel - 0.1 >= settings_wheel - settings_pad + 1.8:
                settings_wheel = round(settings_wheel - 0.1, 1)
                re_settings_button()
            if event.button == 5 and settings_wheel + 0.1 <= settings_upper_margin:
                settings_wheel = round(settings_wheel + 0.1, 1)
                re_settings_button()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_press = False
                NotificationLeftPress = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                key_esc = True
    if not FineLoadGame:
        screen.fill(BACKGROUND)
        if ConditionOfLoad:
            StartLoadProgress.value = StartLoaded/MaxStartLoad
            StartLoadLabel2.text = ConditionOfLoad
            StartLoadLabel.text = f'{int(StartLoaded/MaxStartLoad*100)} %'
        else:
            StartLoadProgress.value = 0
            StartLoadLabel.text = 'Подключение...'
        LoadGameGroup.update()
        LoadGameGroup.draw(screen)

    elif room:
        screen.fill(BACKGROUND)
        sprites.update()
        RoomQuit.update()
        if ButtonTheme.isCollide() and mouse_left_press:
            theme = not theme
            re_theme()
            mouse_left_press = False
        elif ButtonSettings.isCollide() and mouse_left_press:
            mouse_left_press = False
            settings = True
            room = False
            re_settings_button()
            ERRORS.append('Настройки пока работают не исправно!.\tПростите.')
        elif RoomQuit.isCollide() and mouse_left_press:
            run = False
        elif ButtonAdm.isCollide() and mouse_left_press:
            mouse_left_press = False
            room = False
            create_game = True
            TextInputCr.active = True
        elif ButtonClient.isCollide() and mouse_left_press:
            mouse_left_press = False
            room = False
            join_game = True
            TextInputJn.active = True
        elif Update.isCollide() and mouse_left_press:
            FromGitVersion = requests.get(
                'https://raw.githubusercontent.com/AlexKim0710/OceanShipsWar/main/version').text[:-1]
            if version < float(FromGitVersion):
                ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
                threading.Thread(target=update_game, args=[FromGitVersion]).start()
            else:
                ERRORS.append('Актуальная версия.')
        sprites.draw(screen)
    elif settings:
        screen.fill(BACKGROUND)
        SettingsButtons.update()
        SettingsMainLabel.update()
        EscButton.update()
        if EscButton.isCollide() and NotificationLeftPress or key_esc:
            settings = False
            room = True
        for s in Switches.sprites():
            if s.update(mouse_left_press):
                GameSettings[s.update(mouse_left_press)] = not GameSettings[s.update(mouse_left_press)]
                mouse_left_press = False
                re_settings_button()
        for l in Lists.sprites():
            u = l.update(mouse_left_press)
            if u:
                if ':' in str(u):
                    if 'Language' in u:
                        re_lang(str(u).split(':')[1])
                        re_theme()
                    GameSettings[str(u).split(':')[0]] = str(u).split(':')[1]
                    re_settings_button()
                mouse_left_press = False
            elif not Slides.sprites():
                mouse_left_press = False
        count_sl = 0
        for s in Slides.sprites():
            u = s.update(mouse_left_press)
            if u:
                GameSettings[u[0]] = u[1]
            else:
                count_sl += 1
            if count_sl == len(Slides.sprites()):
                mouse_left_press = False

        SettingsButtons.draw(screen)
        Switches.draw(screen)
        Lists.draw(screen)
        Slides.draw(screen)
        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
    elif create_game:
        screen.fill(BACKGROUND)
        EscButton.update()
        CreateGameMainLabel.update()
        if EscButton.isCollide() and mouse_left_press or key_esc:
            GameSettings['my socket'] = ['', 0]
            sock = None
            re_theme()
            create_game = False
            room = True
        if GameSettings['my socket'][0]:
            try:
                Enemy_socket, addr = sock.accept()
                GameSettings['enemy socket'] = [addr[0], addr[1]]
                create_game = False
                game = True
                is_adm = True
            except BlockingIOError:
                pass
            CreateGameWaitUser.update()
        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
        CreateGameButtons.draw(screen)
    elif join_game:
        screen.fill(BACKGROUND)
        EscButton.update()
        JoinGameMainLabel.update()
        if EscButton.isCollide() and mouse_left_press or key_esc:
            GameSettings['my socket'] = ['', 0]
            sock = None
            join_game = False
            room = True
            re_theme()

        if GameSettings['my socket'][0]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(1)
                sock.connect(
                    (GameSettings['my socket'][0], 9998 if not GameSettings['my socket'][1] else GameSettings['my socket'][1]))
                is_adm = False
                game = True
                join_game = False
                me = 'client'
                not_me = 'main'
            except Exception as err:
                ERRORS.append(f'Введите общедоступный IP адрес или хостинг!. \t{err}')
                GameSettings['my socket'] = ['', 0]
                re_theme()

        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
        JoinGameButtons.draw(screen)
    elif game:
        run_game = False
        if is_adm:
            if Enemy_socket:
                try:
                    input_data = eval(Enemy_socket.recv(1024 * 2).decode())
                    Enemy_socket.send(str(send_data).encode())
                    run_game = True
                except BlockingIOError:
                    pass
                except OSError:
                    pass
                except (ConnectionAbortedError, SyntaxError, ConnectionResetError, socket.timeout):
                    ERRORS.append('Противник отключился.')
                    game = False
                    room = True
                    sock.close()
                    sock = None
                    GameSettings['my socket'] = ['', 0]
                    GameSettings['enemy socket'] = ['', 0]
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            try:
                sock.send(str(send_data).encode())
                input_data = eval(sock.recv(1024 * 2).decode())
                run_game = True
            except (ConnectionResetError, socket.timeout):
                ERRORS.append('Противник отключился.')
                game = False
                room = True
                sock.close()
                sock = None
                GameSettings['my socket'] = ['', 0]
                GameSettings['enemy socket'] = ['', 0]
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if end_game:
            run_game = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            screen.fill(BACKGROUND)
            EscButton.update()
            l = label((size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.3 // 2, size[0] * 0.2, size[1] * 0.3), 'Вы проиграли!.' if send_data['end game'] == me else 'Вы выйграли!.', BACKGROUND,(0, 255, 255))
            l.update()
            screen.blit(l.image, l.rect)
            screen.blit(EscButton.image, EscButton.rect)
            if EscButton.isCollide() and mouse_left_press or key_esc:
                game = False
                end_game = False
                room = True
                end_game_alpha = 0
                sock.close()
                sock = None
                GameSettings['my socket'] = ['', 0]
                GameSettings['enemy socket'] = ['', 0]

        if run_game:
            screen.fill(BACKGROUND)
            draw()
            RunCycle = True
            mouse_on_block = False
            for letter in blocks:
                if RunCycle:
                    for num, block in enumerate(blocks[letter]):
                        if block.collidepoint(mouse_pos):
                            mouse_on_block = (letter, num)
                            RunCycle = False
                            break
                else:
                    break
            if BUILD:
                LegitBuild = True
                RunCycle = True
                DrawCursor = True
                for type_s in ships:
                    if RunCycle:
                        for rc in ships[type_s].values():
                            rc = rc['ship']
                            rect = GetShip(rc)
                            if GetShipEnv(rect).collidepoint(mouse_pos):
                                LegitBuild = False
                                if GetShip(rc).collidepoint(mouse_pos):
                                    DrawCursor = False
                                RunCycle = False
                                break
                    else:
                        break

                if not solo_ship and not duo_ship and not trio_ship and not quadro_ship:
                    BUILD = False
                    send_data['ships'] = ships
                    send_data['count'] = ship
                    if send_data['move'] == 'build':
                        send_data['move'] = 'fin build'
                if mouse_left_press and mouse_on_block and LegitBuild:
                    if solo_ship or duo_ship or trio_ship or quadro_ship:
                        DrawCursor = False
                        great_build = False
                        if not build_ship:
                            start_build = mouse_on_block
                            index_of_len_ship = 2
                            build_ship = True
                            doSelect = True
                        else:
                            if start_build == mouse_on_block:
                                create_ship = (start_build, mouse_on_block)
                            else:
                                if doSelect:
                                    if GetRect(start_build).x < GetRect(mouse_on_block).x:
                                        doSelect = False
                                        left_to_right = True
                                        right_to_left, up_to_down, down_to_up = False, False, False

                                    elif GetRect(start_build).x > GetRect(mouse_on_block).x:
                                        doSelect = False
                                        right_to_left = True
                                        left_to_right, up_to_down, down_to_up = False, False, False

                                    elif GetRect(start_build).y < GetRect(mouse_on_block).y:
                                        doSelect = False
                                        up_to_down = True
                                        left_to_right, right_to_left, down_to_up = False, False, False

                                    elif GetRect(start_build).y > GetRect(mouse_on_block).y:
                                        doSelect = False
                                        down_to_up = True
                                        left_to_right, right_to_left, up_to_down = False, False, False

                                else:
                                    if left_to_right:
                                        if GetRect(mouse_on_block).x - GetRect(start_build).x > 0:
                                            create_ship = (start_build, (mouse_on_block[0], start_build[1]))
                                            index_of_len_ship = 2
                                        else:
                                            doSelect = True

                                    elif right_to_left:
                                        if GetRect(start_build).x - GetRect(mouse_on_block).x > 0:
                                            create_ship = ((mouse_on_block[0], start_build[1]), start_build)
                                            index_of_len_ship = 2
                                        else:
                                            doSelect = True

                                    elif up_to_down:
                                        if GetRect(mouse_on_block).y - GetRect(start_build).y > 0:
                                            create_ship = (start_build, (start_build[0], mouse_on_block[1]))
                                            index_of_len_ship = 3
                                        else:
                                            doSelect = True

                                    elif down_to_up:
                                        if GetRect(start_build).y - GetRect(mouse_on_block).y > 0:
                                            create_ship = ((start_build[0], mouse_on_block[1]), start_build)
                                            index_of_len_ship = 3
                                        else:
                                            doSelect = True
                            if create_ship:
                                pygame.draw.rect(screen, LINES, GetShip(create_ship), ships_wh)

                else:
                    if build_ship and create_ship:
                        mouse_left_press = False
                        RunCycle = True
                        for type_s in ships:
                            if RunCycle:
                                for rc in ships[type_s].values():
                                    rect = GetShip(rc['ship'])
                                    if GetShipEnv(GetShip(create_ship)).colliderect(rect):
                                        create_ship = None
                                        build_ship = False
                                        ERRORS.append('Не по правилам!.')
                                        RunCycle = False
                                        break
                            else:
                                break
                        else:
                            if GetShip(create_ship)[index_of_len_ship] / bsize > 4:
                                ERRORS.append('Максимальная длина корабля 4 клетки!.')
                                create_ship = None
                                build_ship = False
                                doSelect = True
                                DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 4:
                                if quadro_ship:
                                    quadro_ship -= 1
                                    ships[4][quadro] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    #                     send_data['ships'][4][quadro] = {}
                                    #                     for l in range(4):
                                    #                         if index_of_len_ship == 3:
                                    #                             My_ships_blocks[4][quadro].append([create_ship[0], create_ship[1] + bsize * l,
                                    #                                                                create_ship[0] + bsize,
                                    #                                                                create_ship[1] + bsize + bsize * l])
                                    #                         elif index_of_len_ship == 2:
                                    #                             My_ships_blocks[4][quadro].append([create_ship[0] + bsize * l, create_ship[1],
                                    #                                                                create_ship[0] + bsize + bsize * l,
                                    #                                                                create_ship[1] + bsize])
                                    #                         bl.append([
                                    #                             get_cords_block([My_ships_blocks[4][0][l][0], My_ships_blocks[4][0][l][1]])[0],
                                    #                             get_cords_block([My_ships_blocks[4][0][l][0], My_ships_blocks[4][0][l][1]])[1]
                                    #                         ])
                                    #
                                    #                     great_build = True
                                    #                     ships[4][quadro] = create_ship
                                    #                     send_data['ships'][4][quadro]['ship'] = [
                                    #                         [get_cords_block(
                                    #                             [My_ships_blocks[4][quadro][0][0], My_ships_blocks[4][quadro][0][1]])[
                                    #                              0],
                                    #                          get_cords_block(
                                    #                              [My_ships_blocks[4][quadro][0][0], My_ships_blocks[4][quadro][0][1]])[
                                    #                              1]],
                                    #                         [get_cords_block(
                                    #                             [My_ships_blocks[4][quadro][3][0], My_ships_blocks[4][quadro][3][1]])[
                                    #                              0],
                                    #                          get_cords_block(
                                    #                              [My_ships_blocks[4][quadro][3][0], My_ships_blocks[4][quadro][3][1]])[
                                    #                              1]]]
                                    #                     send_data['ships'][4][quadro]['blocks'] = bl
                                    quadro += 1
                                    great_build = True
                                else:
                                    ERRORS.append('4-х палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 3:
                                if trio_ship:
                                    trio_ship -= 1
                                    #                     bl = []
                                    #                     send_data['ships'][3][trio] = {}
                                    #                     My_ships_blocks[3][trio] = []
                                    #                     for l in range(3):
                                    #                         if index_of_len_ship == 3:
                                    #                             My_ships_blocks[3][trio].append([create_ship[0], create_ship[1] + bsize * l,
                                    #                                                              create_ship[0] + bsize,
                                    #                                                              create_ship[1] + bsize + bsize * l])
                                    #                         elif index_of_len_ship == 2:
                                    #                             My_ships_blocks[3][trio].append([create_ship[0] + bsize * l, create_ship[1],
                                    #                                                              create_ship[0] + bsize + bsize * l,
                                    #                                                              create_ship[1] + bsize])
                                    #                         bl.append([
                                    #                             get_cords_block(
                                    #                                 [My_ships_blocks[3][trio][l][0], My_ships_blocks[3][trio][l][1]])[
                                    #                                 0],
                                    #                             get_cords_block(
                                    #                                 [My_ships_blocks[3][trio][l][0], My_ships_blocks[3][trio][l][1]])[1]
                                    #                         ])
                                    #                     send_data['ships'][3][trio]['ship'] = [
                                    #                         [get_cords_block([My_ships_blocks[3][trio][0][0], My_ships_blocks[3][trio][0][1]])[
                                    #                              0],
                                    #                          get_cords_block([My_ships_blocks[3][trio][0][0], My_ships_blocks[3][trio][0][1]])[
                                    #                              1]],
                                    #                         [get_cords_block([My_ships_blocks[3][trio][2][0], My_ships_blocks[3][trio][2][1]])[
                                    #                              0],
                                    #                          get_cords_block([My_ships_blocks[3][trio][2][0], My_ships_blocks[3][trio][2][1]])[
                                    #                              1]]]
                                    #                     send_data['ships'][3][trio]['blocks'] = bl
                                    ships[3][trio] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    trio += 1
                                    great_build = True
                                else:
                                    ERRORS.append('3-х палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 2:
                                if duo_ship:
                                    duo_ship -= 1
                                    #                     My_ships_blocks[2][duo] = []
                                    #                     bl = []
                                    #                     send_data['ships'][2][duo] = {}
                                    #                     for l in range(2):
                                    #                         if index_of_len_ship == 3:
                                    #                             My_ships_blocks[2][duo].append([create_ship[0], create_ship[1] + bsize * l,
                                    #                                                             create_ship[0] + bsize,
                                    #                                                             create_ship[1] + bsize + bsize * l])
                                    #                         elif index_of_len_ship == 2:
                                    #
                                    #                             My_ships_blocks[2][duo].append([create_ship[0] + bsize * l, create_ship[1],
                                    #                                                             create_ship[0] + bsize + bsize * l,
                                    #                                                             create_ship[1] + bsize])
                                    #                         bl.append([
                                    #                             get_cords_block([My_ships_blocks[2][duo][l][0], My_ships_blocks[2][duo][l][1]])[
                                    #                                 0],
                                    #                             get_cords_block([My_ships_blocks[2][duo][l][0], My_ships_blocks[2][duo][l][1]])[
                                    #                                 1]
                                    #                         ])
                                    #                     send_data['ships'][2][duo]['ship'] = [
                                    #                         [get_cords_block([My_ships_blocks[2][duo][0][0], My_ships_blocks[2][duo][0][1]])[0],
                                    #                          get_cords_block([My_ships_blocks[2][duo][0][0], My_ships_blocks[2][duo][0][1]])[
                                    #                              1]],
                                    #                         [get_cords_block([My_ships_blocks[2][duo][1][0], My_ships_blocks[2][duo][1][1]])[0],
                                    #                          get_cords_block([My_ships_blocks[2][duo][1][0], My_ships_blocks[2][duo][1][1]])[
                                    #                              1]]]
                                    #                     send_data['ships'][2][duo]['blocks'] = bl
                                    ships[2][duo] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    duo += 1
                                    great_build = True
                                else:
                                    ERRORS.append('2-х палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 1:
                                if solo_ship:
                                    solo_ship -= 1
                                    #                     My_ships_blocks[1][solo] = []
                                    #                     bl = []
                                    #                     send_data['ships'][1][solo] = {}
                                    #                     for l in range(1):
                                    #                         if index_of_len_ship == 3:
                                    #                             My_ships_blocks[1][solo].append([create_ship[0], create_ship[1] + bsize * l,
                                    #                                                              create_ship[0] + bsize,
                                    #                                                              create_ship[1] + bsize + bsize * l])
                                    #                         elif index_of_len_ship == 2:
                                    #                             My_ships_blocks[1][solo].append([create_ship[0] + bsize * l, create_ship[1],
                                    #                                                              create_ship[0] + bsize + bsize * l,
                                    #                                                              create_ship[1] + bsize])
                                    #                         bl.append([
                                    #                             get_cords_block(
                                    #                                 [My_ships_blocks[1][solo][l][0], My_ships_blocks[1][solo][l][1]])[
                                    #                                 0],
                                    #                             get_cords_block(
                                    #                                 [My_ships_blocks[1][solo][l][0], My_ships_blocks[1][solo][l][1]])[1]
                                    #                         ])
                                    #                     send_data['ships'][1][solo]['ship'] = [
                                    #                         [get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                    #                              0],
                                    #                          get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                    #                              1]],
                                    #                         [get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                    #                              0],
                                    #                          get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                    #                              1]]]
                                    #                     send_data['ships'][1][solo]['blocks'] = bl
                                    ships[1][solo] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    solo += 1
                                    great_build = True
                                else:
                                    ERRORS.append('1-о палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                        #             elif ships[ship][index_of_len_ship] / bsize == 0:
                        #                 create_ship = None
                        #                 build_ship = False
                        #                 doSelect = True
                        if great_build:
                            great_build = False
                            build_ship = False
                            doSelect = True
                            DrawCursor = True
                            ship += 1
                            create_ship = None
                            left_to_right, right_to_left, up_to_down, down_to_up = False, False, False, False
                for type_s in ships:
                    for rc in ships[type_s].values():
                        pygame.draw.rect(screen, LINES, GetShip(rc['ship']), ships_wh)
                if LegitBuild:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                if LegitBuild and mouse_on_block and DrawCursor:
                    pygame.draw.rect(screen, GREEN, GetRect(mouse_on_block), ships_wh)
                elif not LegitBuild and mouse_on_block and DrawCursor:
                    pygame.draw.rect(screen, RED, GetRect(mouse_on_block), ships_wh)

                draw_ship_count([solo_ship, duo_ship, trio_ship, quadro_ship])

            if not BUILD:
                # for n, ev in enumerate(send_data['event']):
                # if 'update' in ev:
                #     send_data['ships'] = eval(ev.split('|')[1])
                #     send_data['selects'] = eval(ev.split('|')[2])
                #     send_data['die'] = eval(ev.split('|')[3])
                #     del send_data['event'][n]
                # if 'lose' in ev:
                #     ERRORS.append('LOSE!.')
                #     game = False
                #     room = True
                send_data['event'] = []
                for n, event in enumerate(input_data['event']):
                    try:
                        if event['type'] == 'sound':
                            exec(event['event'])
                    except Exception:
                        pass
                try:
                    for type_ship in send_data['ships']:
                        for num_of_ship in send_data['ships'][type_ship]:
                            for num_of_block, block in enumerate(send_data['ships'][type_ship][num_of_ship]['blocks']):
                                if block in input_data['killed']['blocks']:
                                    del send_data['ships'][type_ship][num_of_ship]['blocks'][num_of_block]
                                    send_data['die']['blocks'].append(block)
                                    if not send_data['ships'][type_ship][num_of_ship]['blocks']:
                                        send_data['die']['ships'].append(send_data['ships'][type_ship][num_of_ship]['ship'])
                                        del send_data['ships'][type_ship][num_of_ship]
                                    break
                except RuntimeError:
                    pass

                if is_adm:
                    if send_data['move'] == not_me and input_data['pass']:
                        send_data['move'] = me
                    elif send_data['move'] == me and send_data['pass']:
                        send_data['move'] = not_me
                    if send_data['move'] == not_me and send_data['pass']:
                        send_data['pass'] = False
                    move = send_data['move']
                else:
                    if input_data['move'] == not_me and send_data['pass']:
                        send_data['pass'] = False
                    move = input_data['move']
                if move == me:
                    if len(input_data['die']['ships']) == input_data['count']:
                        send_data['end game'] = not_me
                        ERRORS.append('Выйгрыш!.')
                        end_game = True
                    elif len(send_data['die']['ships']) == send_data['count']:
                        send_data['end game'] = me
                        ERRORS.append('Проигрыш!.')
                        end_game = True
                    txt = font.render('Ваш удар!.', True, (0, 255, 0))
                    screen.blit(txt, (size[0] // 2 - txt.get_rect()[2] // 2, size[1] - txt.get_rect()[3] - bsize // 2))
                    if mouse_on_block and mouse_left_press:
                        if mouse_on_block not in send_data['selects'] and mouse_on_block not in send_data['killed'][
                            'blocks']:
                            mouse_left_press = False
                            killed_enemy = False
                            final_killed_enemy = False
                            RunCycle = True
                            for type_ship in input_data['ships']:
                                if RunCycle:
                                    for num_of_ship in input_data['ships'][type_ship]:
                                        if RunCycle:
                                            for num_of_block, block in enumerate(
                                                    input_data['ships'][type_ship][num_of_ship]['blocks']):
                                                RectBlock = GetRect(block)
                                                if RectBlock.collidepoint(mouse_pos):
                                                    send_data['killed']['blocks'].append(block)
                                                    del input_data['ships'][type_ship][num_of_ship]['blocks'][
                                                        num_of_block]
                                                    killed_enemy = True
                                                    final_killed_enemy = False
                                                    if not len(input_data['ships'][type_ship][num_of_ship]['blocks']):
                                                        final_killed_enemy = True
                                                        killed_enemy = True
                                                        send_data['killed']['ships'].append(
                                                            input_data['ships'][type_ship][num_of_ship]['ship'])
                                                    #    input_data['die']['ships'].append(input_data['ships'][type_ship][num_of_ship]['ship'])
                                                    #    input_data['ships'][type_ship][num_of_ship]['ship'] = []
                                                    # send_data['event'].append(
                                                    #     f'update|{str(input_data["ships"])}|{str(input_data["selects"])}|{str(input_data["die"])}')
                                                    RunCycle = False
                                                    break
                                        else:
                                            break
                                else:
                                    break
                            if killed_enemy:
                                if final_killed_enemy:
                                    if GameSettings['Game Sound'] and GameSettings['Sound']:
                                        Sounds['killed_sound'].set_volume(GameSettings['Game SoundVol'])
                                        Sounds['killed_sound'].play()
                                        send_data['event'].append({'type': 'sound', 'event': 'Sounds["killed_sound"].play()'})
                                else:
                                    if GameSettings['Game Sound'] and GameSettings['Sound']:
                                        Sounds['wounded_sound'].set_volume(GameSettings['Game SoundVol'])
                                        Sounds['wounded_sound'].play()
                                        send_data['event'].append({'type': 'sound', 'event': 'Sounds["wounded_sound"].play()'})
                                send_data['pass'] = False
                            else:
                                if GameSettings['Game Sound'] and GameSettings['Sound']:
                                    Sounds['missed_sound'].set_volume(GameSettings['Game SoundVol'])
                                    Sounds['missed_sound'].play()
                                    send_data['event'].append({'type':'sound','event':'Sounds["missed_sound"].play()'})
                                send_data['pass'] = True
                                send_data['selects'].append(mouse_on_block)
                    for rc in input_data['die']['blocks']:
                        pygame.draw.line(screen, RED, GetRect(rc).topleft, GetRect(rc).bottomright)
                        pygame.draw.line(screen, RED, GetRect(rc).topright, GetRect(rc).bottomleft)

                    for rc in input_data['die']['ships']:
                        pygame.draw.rect(screen, RED, GetShip(rc), ships_wh)

                    for rc in send_data['selects']:
                        pygame.draw.circle(screen, RED, GetRect(rc).center, bsize / 100 * 10)
                    if mouse_on_block not in send_data['selects'] and mouse_on_block not in send_data['killed']['blocks']:
                        if mouse_on_block:
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                            pygame.draw.rect(screen, BLUE, GetRect(mouse_on_block), ships_wh)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                        pygame.draw.rect(screen, RED, GetRect(mouse_on_block), ships_wh)

                elif move == not_me:
                    if len(input_data['die']['ships']) == input_data['count']:
                        send_data['end game'] = not_me
                        ERRORS.append('Выйгрыш!.')
                        end_game = True
                    elif len(send_data['die']['ships']) == send_data['count']:
                        send_data['end game'] = me
                        ERRORS.append('Проигрыш!.')
                        end_game = True
                    txt = font.render('Ждем...', True, (255, 255, 0))
                    screen.blit(txt, (size[0] // 2 - txt.get_rect()[2] // 2, size[1] - txt.get_rect()[3] - bsize // 2))
                    for type_s in range(1, max(send_data['ships'].keys()) + 1):
                        for sp in send_data['ships'][type_s].values():
                            pygame.draw.rect(screen, LINES, GetShip(sp['ship']), ships_wh)
                    for block in send_data['die']['blocks']:
                        block = GetRect(block)
                        pygame.draw.line(screen, tuple(map(lambda c: c - 100 if c > 100 else 100, LINES)),
                                         block.topright, block.midbottom)
                        pygame.draw.line(screen, tuple(map(lambda c: c - 100 if c > 100 else 100, LINES)), block.midtop,
                                         block.bottomleft)
                    for rc in send_data['die']['ships']:
                        pygame.draw.rect(screen, tuple(map(lambda c: c - 100 if c > 100 else 100, LINES)),
                                         GetShip(rc), ships_wh)
                    for rc in input_data['selects']:
                        pygame.draw.circle(screen, RED, GetRect(rc).center, bsize / 100 * 10)

                elif input_data['move'] == 'build':
                    for type_s in range(1, max(send_data['ships'].keys()) + 1):
                        for sp in send_data['ships'][type_s].values():
                            pygame.draw.rect(screen, LINES, GetShip(sp['ship']), ships_wh)
                elif send_data['move'] == 'fin build' or input_data['move'] == 'fin build':
                    if is_adm:
                        send_data['move'] = random.choice([me, not_me])
                    else:
                        send_data['move'] = None
    for n, er in enumerate(ERRORS):
        if GameSettings['Notification Sound'] and GameSettings['Sound']:
            Sounds['info_sound'].set_volume(GameSettings['Notification SoundVol'])
            Sounds['info_sound'].play()
        Notifications.add(Notification(
            (size[0] // 2 - size[0] * 0.4 // 2, size[1] * 0.07, size[0] * 0.4, size[1] * 0.1),
            er, (86, 86, 86), (0, 0, 0), (255, 255, 255)))
        del ERRORS[n]
    for n, s in enumerate(reversed(Notifications.sprites())):
        if not n:
            if s.update(NotificationLeftPress):
                NotificationLeftPress = False
        else:
            if s.update(False):
                NotificationLeftPress = False
    Notifications.draw(screen)
    scrn.blit(screen,(0,0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
if sock:
    sock.close()