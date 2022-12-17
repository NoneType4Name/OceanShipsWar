import select
import socket
import log


def GetIpFromTuple(tpl):
    return '{}:{}'.format(*tpl)


def GetIpFromString(st):
    st = st.split(':')
    return ':'.join(st[:-1]), st[-1]


def handle(u_s, u_ad):
    try:
        data: bytes = u_s.recv(1024)
    except ConnectionError:
        log.info(f"Client {u_ad} suddenly closed while receiving.")
        return False
    if not data:
        log.info(f"Disconnected by {u_ad}.")
        return False
    else:
        try:
            data: str = data.decode()
            log.debug(f'Recv {u_ad} > {data}.')
        except UnicodeError:
            log.critical(f'Unicode Error, received data: {data}.')
            log.info(f'Forced termination of connection with {u_ad}.')
            return False
        if 'ConnectAroundNAT' in data:
            expect = data.replace('ConnectAroundNAT', '').split('|')
            if expect[0] in connected:
                connected[expect[0]].send(f'ConnectAroundNATInbound{expect[1]}'.encode())
                data = ''
            else:
                data = 'ConnectAroundNATInboundError'
        elif 'mine.' in data:
            data = GetIpFromTuple(u_ad)
        else:
            log.warning(f'unknown request: {data}.')
    if data:
        try:
            log.debug(f'Send {data} > {u_ad}.')
            u_s.send(data.encode())
        except ConnectionError:
            log.info(f"Client {u_ad} suddenly closed, cannot send.")
            return False
    return True


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.bind(('192.168.1.64', 61023))
sock.listen(True)
connected = {GetIpFromTuple(sock.getsockname()): sock}
outputs = []


while True:
    readable, writeable, exceptional = select.select(connected.values(), outputs, connected.values())
    for user_sock in readable:
        if user_sock == sock:
            sk, adr = sock.accept()
            log.info(f'Connected by {adr}.')
            connected[GetIpFromTuple(adr)] = sk
        else:
            adr = user_sock.getpeername()
            if not handle(user_sock, adr):
                del connected[GetIpFromTuple(adr)]
                user_sock.close()

