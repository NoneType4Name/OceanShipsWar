try:
    import client
except Exception as err:
    import traceback
    import sys
    import pygame
    from datetime import datetime
    from ctypes import windll
    from report import *

    current_datetime = datetime.now()

    exc_type, exc_value, exc_tb = sys.exc_info()
    traceback_exception = ''.join(traceback.TracebackException(exc_type, exc_value, exc_tb).format())
    log.error(err.args, exc_info=True, stack_info=True)
    send_message(['alexkim0710@gmail.com'], f'ERROR {type(err)}',
                 f'{traceback_exception}'
                 f'\n\ntime:\t {current_datetime}'
                 f'\nis adm:\t {bool(windll.shell32.IsUserAnAdmin())}',
                 client.version, 'logs.txt')
    windll.user32.MessageBoxW(pygame.display.get_wm_info()['windows'] if pygame.display.get_init() else 0, traceback_exception,
                              "ERROR INFO", 0)
