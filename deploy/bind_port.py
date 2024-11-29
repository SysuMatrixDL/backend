import socket
import random

def get_free_ports(start=6000, end=8000, count=3):
    free_ports = set()
    while len(free_ports) < count:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                free_ports.add(port)
            except OSError:
                # 端口已被占用，继续寻找
                continue
    return list(free_ports)

if __name__ == "__main__":
    free_ports = get_free_ports(start=6000, end=8000, count=3)
    for port in free_ports:
        print(port, end=' ')
    print()