import contextlib
import json
import socket
import sys


def main(port):
    host = "localhost"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with contextlib.closing(sock):
        sock.connect((host, port))
        data = json.dumps({ "command": "/player/list" })
        sock.sendall(bytes(data, "UTF-8") + b"\n")
        buf = b""
        while buf.find(b"\n") < 0:
            a = sock.recv(1024)
            buf += a

        print(json.loads(buf[:buf.find(b"\n")]))

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write("arguments: 1 => port\n")
        sys.exit(1)

    main(int(sys.argv[1]))
