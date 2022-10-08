import winreg as reg
import argparse
APP_NAME = 'osw'


class Data:
    def __init__(self, value, data_type, error=None):
        self.data = value
        self.type = data_type
        self.error = error

    def __repr__(self):
        return self.data

    def __str__(self):
        return str(self.data)


def set_value(key, path, name, value):
    try:
        reg.CreateKey(key, path)
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_WRITE)
        reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, value)
        reg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


def get_value(key, path, name):
    try:
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_READ)
        value, regtype = reg.QueryValueEx(registry_key, name)
        reg.CloseKey(registry_key)
        return Data(value, regtype)
    except Exception as err:
        return Data(None, None, err)


def delete_key(key, path):
    try:
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_ALL_ACCESS)
        for x in range(reg.QueryInfoKey(registry_key)[0]):
            subkey = reg.EnumKey(registry_key, 0)
            try:
                reg.DeleteKey(registry_key, subkey)
            except Exception:
                delete_key(reg.HKEY_CLASSES_ROOT, fr'{path}\{subkey}')

        reg.DeleteKey(registry_key, "")
        registry_key.Close()
    except Exception as err:
        return err.args


def init_deep_links(path_exe):
    while True:
        if path_exe not in str(get_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None).data):
            set_value(reg.HKEY_CLASSES_ROOT, APP_NAME, None, 'Deep Links')
            set_value(reg.HKEY_CLASSES_ROOT, APP_NAME, 'URL Protocol', None)

            set_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\DefaultIcon', None, f'{path_exe}, 1')
            set_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None, f'{path_exe} --DeepLinksApi "%1"')
            break


def del_deep_link():
    while True:
        if get_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None):
            delete_key(reg.HKEY_CLASSES_ROOT, fr'{APP_NAME}')
            break


def createParser():
        parser = argparse.ArgumentParser()
        parser.add_argument('-l','--links', dest='links', action='store_false')
        parser.add_argument('-s','--size', dest='size')
        parser.add_argument('-t','--theme', dest='theme', action='store_true')
        parser.add_argument('-L','--lang', dest='lang', choices=['rus','eng'])
        parser.add_argument('--DeepLinksApi', dest='DeepLinksApi')
        return parser
