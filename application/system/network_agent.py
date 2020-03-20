import contextlib
import json
import queue
import socket
import threading

from .config import Config
from ..player import Builder


class Scene:
    LOBBY = 0
    COLOR = 1
    BOARD = 2
    RESULT = 3


class NetworkAgent:

    def __init__(self):
        self.read_queue = queue.Queue()
        self.write_queue = queue.Queue()

        self.you = Builder.build_network_player({ "board_size": 8 }, "You")
        self.you.set_queue(self.write_queue, self.read_queue)

        self.scene = Scene.LOBBY

    def handle(self, connection):
        self.scene = Scene.LOBBY

        self.read_thread = threading.Thread(target = self.read_loop, args = (connection,))
        self.receive_thread = threading.Thread(target = self.receive_loop, args = (connection,))

        self.read_thread.start()
        self.receive_thread.start()

        self.read_thread.join()
        self.receive_thread.join()

    def read_loop(self, connection):
        while True:
            item = self.read_queue.get()

            if item.get("system") == "end":
                return

    def receive_loop(self, connection):
        size = 4096
        buffer = b""

        while True:
            message = connection.recv(size)

            if not message:
                break

            buffer += message

            while True:
                index = buffer.find(b"\n")

                if index < 0:
                    break

                data = buffer[:index + 1]
                buffer = buffer[index + 1:]

                response = self.devide(json.loads(str(data, "UTF-8")))

                if response is not None:
                    connection.send(bytes(json.dumps(response), "UTF-8") + b"\n")

        self.quit()

    def devide(self, data):
        if data.get("command") == "/player/list":
            return self.get_player_list()
        elif data.get("command") == "/player/nominate":
            return self.nominate_player(data.get("name", ""))
        elif data.get("command") == "/game/start":
            pass
        else:
            return { "command": "/error", "message": "no such command \"{}\"".format(data.get("command", "")) }

    def quit(self):
        self.read_queue.put({ "system": "end" })

    def get_player_list(self):
        result = []

        players = Config.get("players")

        for name, value in players.items():
            if value.get("hide") == True:
                continue

            board_size = value.get("board_size")
            screen_name = value.get("screen_name", name)
            result.append({
                "name": name,
                "board_size": board_size,
                "screen_name": screen_name
            })

        return { "command": "/player/list", "players": result }

    def nominate_player(self, name):
        if self.scene != Scene.LOBBY:
            return {
                "command": "/error",
                "message": "incorrect scene: now scene is {}".format(self.scene.name),
                "error_command": "/player/nominate"
            }

        player = Config.get_player(name)

        if player is None:
            return {
                "command": "/error",
                "message": "no such player \"{}\"".format(name),
                "error_command": "/player/nominate"
            }

        screen_name = player.get("screen_name", name)

        self.opponent = Builder.build_player(name)

        self.scene = Scene.COLOR

        return {
            "command": "/room/create",
            "opponent": {
                "name": name,
                "screen_name": screen_name
            }
        }

    def serve(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with contextlib.closing(sock):
            sock.bind((host, port))
            sock.listen(1)

            while True:
                connection, address = sock.accept()
                self.handle(connection)
