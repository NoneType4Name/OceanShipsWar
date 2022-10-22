import win32file
fileHandle = win32file.CreateFile(r"\\.\pipe\osw",
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)

win32file.WriteFile(fileHandle, b'hell', None)
