import threading
import select
import socket


def GetIpFromTuple(tpl):
    return '{}:{}'.format(*tpl)


def GetIpFromString(st):
    st = st.split(':')
    return ':'.join(st[:-1]), st[-1]


def SendList(s, m):
    s.send(m)
    s.recv(1024)


def handle(u_s, u_ad):
    try:
        data: bytes = u_s.recv(1024)  # Should be ready
    except ConnectionError:
        print(f"Client suddenly closed while receiving")
        return False
    if not data:
        print("Disconnected by", u_ad)
        return False
    else:
        data: str = data.decode().replace('>', '')
        if 'ConnectAroundNAT' in data:
            expect = data.replace('ConnectAroundNAT', '').split('|')
            if expect[0] in connected:
                connected_data_list[expect[0]].append(f'ConnectAroundNATInbound{GetIpFromTuple(expect[1])}')
            else:
                data = 'ConnectAroundNATInboundError'
        elif 'ping!.' in data:
            for d in connected_data_list[GetIpFromTuple(u_ad)]:
                threading.Thread(target=SendList, args=[u_s, str(d).encode()]).start()
            else:
                data = 'pong!.'
            connected_data_list[GetIpFromTuple(u_ad)] = []
        elif 'mine.' in data:
            connected_data_list[GetIpFromTuple(u_ad)].append(GetIpFromTuple(u_ad))
        else:
            print(f"recv: {data} from: {u_ad}")
    if data:
        try:
            u_s.send(data.encode())  # Hope it won't block
        except ConnectionError:
            print(f"Client suddenly closed, cannot send")
            return False
    return True


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.bind(('0.0.0.0', 0))
sock.listen(True)
connected = {GetIpFromTuple(sock.getsockname()): sock}
connected_data_list = {GetIpFromTuple(sock.getsockname()): []}
outputs = []


while True:
    readable, writeable, exceptional = select.select(connected.values(), outputs, connected.values())
    for user_sock in readable:
        if user_sock == sock:
            sk, adr = sock.accept()
            print("Connected by", adr)
            connected[GetIpFromTuple(adr)] = sk
            connected_data_list[GetIpFromTuple(adr)] = []
        else:
            adr = user_sock.getpeername()
            if not handle(user_sock, adr):
                del connected[GetIpFromTuple(adr)]
                del connected_data_list[GetIpFromTuple(adr)]
                # if sock in outputs:
                #     outputs.remove(sock)
                user_sock.close()
