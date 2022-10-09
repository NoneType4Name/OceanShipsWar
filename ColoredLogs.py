import pickle
import logging
import logging.handlers
import socketserver
import struct


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING'  : YELLOW,
    'INFO'     : GREEN,
    'DEBUG'    : CYAN,
    'CRITICAL' : YELLOW,
    'ERROR'    : RED,
    'RED'      : RED,
    'GREEN'    : GREEN,
    'YELLOW'   : YELLOW,
    'BLUE'     : BLUE,
    'MAGENTA'  : MAGENTA,
    'CYAN'     : CYAN,
    'WHITE'    : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ  = "\033[1m"


class ColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color = COLOR_SEQ % (30 + COLORS[levelname])
        message = logging.Formatter.format(self, record)
        message = message.replace("$RESET", RESET_SEQ)\
                         .replace("$BOLD",  BOLD_SEQ)\
                         .replace("$COLOR", color)
        for k,v in COLORS.items():
            message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
                             .replace("$BG" + k,  COLOR_SEQ % (v+40))\
                             .replace("$BG-" + k, COLOR_SEQ % (v+40))
        return message + RESET_SEQ


logging.ColorFormatter = ColorFormatter
logFormatter = logging.Formatter(fmt='%(levelname)s  [%(asctime)s.%(msecs)03d]  [%(filename)s:%(lineno)d:%(funcName)s]  %(message)s', datefmt='%H:%M:%S')
ConsoleLogFormatter = logging.ColorFormatter(
    fmt='[$COLOR%(levelname)s$RESET]  [%(filename)s:%(lineno)d:%(funcName)s]  [%(asctime)s.%(msecs)03d] %(message)s',
    datefmt='%H:%M:%S')

consoleHandler = logging.handlers.SocketHandler('localhost', 9999)
consoleHandler.setFormatter(ConsoleLogFormatter)
consoleHandler.setLevel(logging.NOTSET)
