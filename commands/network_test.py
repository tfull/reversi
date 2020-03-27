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
        data = receive(sock, receive_data)
        validate(data, "/player/list")
        print("[Step 2] (/player/list) players:", data["players"])

        if step <= 2:
            return

        send(sock, {
            "command": "/room/create",
            "name": random.choice(data["players"])["name"],
            "board_size": 8
        })
        data = receive(sock, receive_data)
        validate(data, "/room/create")
        print("[Step 3] (/room/create) opponent:", data["opponent"])

        if step <= 3:
            return

        for i_game in range(3):
            send(sock, {
                "command": "/game/start",
                "color": "random"
            })
            data = receive(sock, receive_data)
            validate(data, "/game/start")
            print("[Step {i}-1] (/game/start) color: {color}".format(i = 4 + min(i_game, 1), color = data["color"]))

            while True:
                data = receive(sock, receive_data)
                command = data.get("command", "")

                if command == "/game/move":
                    print(data["target"])
                    pass
                elif command == "/game/notice/your_turn":
                    movable = data["movable"]

                    if len(movable) > 0:
                        move = random.choice(movable)
                    else:
                        move = "pass"

                    print("[Step {i}-2] (/game/move) {move}".format(i = 4 + min(i_game, 1), move = move))
                    send(sock, {
                        "command": "/game/move",
                        "value": move
                    })
                elif command == "/game/complete":
                    print("[Step {i}-3] complete".format(i = 4 + min(i_game, 1)))
                    break
                else:
                    raise Exception("/game loop")

            if step <= 4:
                return

    print("Complete!")


def validate(data, command):
    if data.get("command", "") != command:
        if data.get("command", "") == "/error":
            print("error message:", data.get("message", ""))

        raise Exception("Error: {} is required but got {}".format(command, data.get("command", "")))


def receive(sock, data):
    while data["buffer"].find(b"\n") < 0:
        bs = sock.recv(1024)

        if len(bs) == 0:
            return None

        data["buffer"] += bs

    index = data["buffer"].index(b"\n")
    body = data["buffer"][:index]
    data["buffer"] = data["buffer"][index + 1:]

    return json.loads(body)


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
