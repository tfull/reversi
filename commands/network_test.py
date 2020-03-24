import contextlib
import json
import socket
import sys
import random


def main(port, step = 99):
    host = "localhost"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with contextlib.closing(sock):
        sock.connect((host, port))

        print("[Step 1] connected")

        receive_data = { "buffer": b"" }

        if step <= 1:
            return

        send(sock, { "command": "/player/list" })
        data = receive(sock, receive_data, command = "/player/list")
        print("[Step 2] (/player/list) players:", data["players"])

        if step <= 2:
            return

        send(sock, {
            "command": "/room/create",
            "name": random.choice(data["players"])["name"],
            "board_size": 8
        })
        data = receive(sock, receive_data, command = "/room/create")
        print("[Step 3] (/room/create) opponent:", data["opponent"])

def receive(sock, data, *, command = ""):
    while data["buffer"].find(b"\n") < 0:
        data["buffer"] += sock.recv(1024)

    index = data["buffer"].index(b"\n")
    body = data["buffer"][:index]
    data["buffer"] = data["buffer"][index + 1:]

    result = json.loads(body)

    if result.get("command", "") != command:
        if result.get("command", "") == "/error":
            print("error message:", result.get("message", ""))

        raise Exception("Error: {} is required but got {}".format(command, result.get("command", "")))

    return result

def send(sock, data):
    sock.sendall(bytes(json.dumps(data), "UTF-8") + b"\n")

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(int(sys.argv[1]))
    elif len(sys.argv) == 3:
        main(int(sys.argv[1], sys.argv[2]))
    else:
        sys.stderr.write("wrong number of arguments\n  1 => port\n  2 => step\n")
        sys.exit(1)
