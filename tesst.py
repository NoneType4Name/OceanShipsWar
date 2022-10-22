import netifaces, socket
for inter in netifaces.interfaces():
    print(netifaces.ifaddresses(inter).setdefault(netifaces.AF_INET, [{'addr': socket.gethostbyname(socket.getfqdn())}]))
