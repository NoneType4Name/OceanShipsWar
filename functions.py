import ctypes
import os
import log
import sys
import glob
import copy
import json
import stun
import time
import numpy
import select
import socket
import psutil
import pygame
import random
import argparse
import win32api
import win32gui
import requests
import itertools
import threading
import traceback
from Gui import *
import Reg as reg
import subprocess
import win32process
import win32com.client
from constants import *
from ctypes import windll
import comtypes.client as cc
from ast import literal_eval
from report import send_message
from screeninfo import get_monitors
import comtypes.gen.TaskbarLib as tb
from urllib.parse import urlparse, parse_qs
from netifaces import interfaces, ifaddresses, AF_INET
from log import log, consoleHandler, fileHandler
cc.GetModule(f'{DATAS_FOLDER_NAME}/taskbarlib.tlb')
taskbar=cc.CreateObject('{56FDF344-FD6D-11d0-958A-006097C9A090}',interface=tb.ITaskbarList3)


class DATA(dict):
    def __init__(self, data: dict):
        [data.update({name: self._wrap(value)}) for name, value in data.items()]
        super().__init__(data)
        self.__dict__.update(data)

    def __setitem__(self, key, value):
        wrapt = self._wrap(value)
        super().__setitem__(key, wrapt)
        self.__dict__.update(super().items())

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value


class SIZE(tuple):
    def __init__(self, data):
        self.w = data[0]
        self.h = data[1]


def read_dictionary(exemplar_dict, dictionary):
    for key in dictionary:
        exemplar_dict[key] = dictionary[key]
    return exemplar_dict


def replace_str_var(dictionary, self=None):
    str_dict = str(dictionary)
    if '$' in str_dict:
        split_by_md = str_dict.split('$')
        for md in split_by_md:
            if '%' in md:
                md = md.split('%')[0]
                try:
                    if self is not None:
                        str_dict = str_dict.replace(f'${md}%', getattr(self, md))
                    else:
                        str_dict = str_dict.replace(f'${md}%', eval(md))
                except NameError:
                    log.error(f'UNKNOWN VARIABLE: {self}.{md}')
    return literal_eval(str_dict)


def settings_set_values(settings:DATA, dict_with_only_values:dict):
    for key in settings.keys():
        for sub_key in settings[key].keys():
            d = dict_with_only_values[key][sub_key]
            settings[key][sub_key].value = d if type(d) is not list else tuple(d)
    return settings


def settings_get_values(settings:DATA):
    dict_with_only_values = {}
    for key in settings.keys():
        dict_with_only_values[key] = {}
        for sub_key in settings[key].keys():
            dict_with_only_values[key][sub_key] = settings[key][sub_key].value
    return dict_with_only_values


class Language(DATA):
    def __init__(self, dict_of_all_languages: dict, default_language):
        langs_dict = {}
        for language in dict_of_all_languages:
            dictionary = dict_of_all_languages[language]
            exemplar_dict = copy.deepcopy(DEFAULT_DICTIONARY)
            for key in dictionary:
                exemplar_dict[key] = dictionary[key]
            else:
                langs_dict[language] = exemplar_dict
        super().__init__(langs_dict[default_language])
        self.Languages = langs_dict
        self.LanguageList = list(dict_of_all_languages.keys())
        self.Language = default_language

    def SetLanguage(self, lang):
        lng = self.Languages
        lng_l = self.LanguageList
        self.update(self.Languages[lang])
        self.Languages = lng
        self.LanguageList = lng_l
        self.Language = lang


class Color(DATA):
    def __init__(self, dict_of_all_colors: dict, default_color):
        super().__init__(dict_of_all_colors[default_color])
        self.Colors = dict_of_all_colors
        self.ColorsList = list(dict_of_all_colors.keys())
        self.Color = default_color

    def SetColor(self, color):
        cls = self.Colors
        cls_l = self.ColorsList
        self.update(self.Colors[color])
        self.Colors = cls
        self.ColorsList = cls_l
        self.Color = color


def get_hwnd_by_pid(pid):
    hwnd = []
    win32gui.EnumWindows(lambda hw, null: hwnd.append(hw if ((win32process.GetWindowThreadProcessId(hw)[1] == pid) and (win32gui.IsWindowVisible(hw))) else 0), None)
    return [i for i in hwnd if i]


def get_pid_by_hwnd(hwnd):
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def WindowSetProgressState(hwnd, tbpFlags):
    return taskbar.SetProgressState(hwnd, tbpFlags)


def WindowSetProgressValue(hwnd, ullCompleted, ullTotal):
    return taskbar.SetProgressValue(hwnd, ullCompleted, ullTotal)


def GetIP(sock, ip, port):
    nat = stun.get_nat_type(sock, ip, port, stun_host='stun.l.google.com', stun_port=19302)[1]
    if nat['ExternalIP']:
        return sock, nat['ExternalIP'], nat['ExternalPort'], ip, port
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((ip, port))
        sock.settimeout(0.1)
        nat = stun.get_nat_type(sock, ip, port, stun_host='stun.l.google.com', stun_port=19302)[1]
        if nat['ExternalIP']:
            return sock, nat['ExternalIP'], nat['ExternalPort'], ip, port
        else:
            port += 1
            sock.shutdown(0)
            sock.close()


def GetIpFromTuple(tpl):
    return '{}:{}'.format(*tpl)


def GetIpFromString(st):
    st = st.split(':')
    return ':'.join(st[:-1]), int(st[-1])
