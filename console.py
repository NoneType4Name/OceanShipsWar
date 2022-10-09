try:
    import sys
    from os import system
    from colorama import init

    system("title OceanShipsWar DebugConsole - wait input")
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    COLORS = {'RED': RED,
              'GREEN': GREEN,
              'YELLOW': YELLOW,
              'BLUE': BLUE,
              'MAGENTA': MAGENTA,
              'CYAN': CYAN,
              'WHITE': WHITE}
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"


    def colorize(message):
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD",  BOLD_SEQ)
        for k,v in COLORS.items():
            message = message.replace("$" + k,    COLOR_SEQ % (v+30)).replace("$BG" + k,  COLOR_SEQ % (v+40)).replace("$BG-" + k, COLOR_SEQ % (v+40))
            return message + RESET_SEQ


    init()
    for line in sys.stdin:
        system("title OceanShipsWar DebugConsole - work")
        sys.stdout.write(colorize(line))
        sys.stdout.flush()
    sys.exit(0)
except KeyboardInterrupt:
    system("title OceanShipsWar DebugConsole - stopped by user with KeyboardInterrupt")
    print('stopped by user with KeyboardInterrupt')
    sys.exit(0)
