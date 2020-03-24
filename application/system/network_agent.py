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

        self.game_thread = None

        self.read_thread = threading.Thread(target = self.read_loop, args = (connection,))
        self.receive_thread = threading.Thread(target = self.receive_loop, args = (connection,))

        self.read_thread.start()
        self.receive_thread.start()

        self.read_thread.join()
        self.receive_thread.join()

    def read_loop(self, connection):
        while True:
            item = self.read_queue.get()

            if item.get("game", "") == "move":
                self.send(connection, {
                    "command": "/game/move",
                    "piece": item["piece"],
                    "target": item["target"]
                })
            elif item.get("game", "") == "movable":
                self.send(connection, {
                    "command": "/game/notice/your_turn",
                    "movable": item["movable"]
                })
            elif item.get("game", "") == "complete":
                self.send(connection, {
                    "command": "/game/complete"
                })
            elif item.get("game", "") == "error":
                self.send(connection, {
                    "command": "/error",
                    "message": item["message"]
                })
            elif item.get("system", "") == "end":
                return

    def send(self, connection, data):
        connection.send(bytes(json.dumps(data), "UTF-8") + b"\n")

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
                    self.send(connection, response)

        self.quit()

    def devide(self, data):
        command = data.get("command", "")

        if command == "/player/list":
            return self.get_player_list()
        elif command == "/room/create":
            return self.create_room(data)
        elif command == "/game/start":
            return self.start_game(data.get("color", "random"))
        elif command == "/game/move":
            return self.action_move(data)
        else:
            return {
                "command": "/error",
                "message": "no such command \"{}\"".format(command)
            }

    def quit(self):
        self.read_queue.put({ "system": "end" })

        if self.scene == Scene.BOARD:
            self.read_queue.put("surrender")

        if self.game_thread is not None:
            self.game_thread.join()

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

        return {
            "command": "/player/list",
            "players": result
        }

    def create_room(self, data):
        if self.scene != Scene.LOBBY:
            return {
                "command": "/error",
                "message": "incorrect scene: now scene is {}".format(self.scene.name),
                "error_command": "/room/create"
            }

        name = data.get("name", "")

        player = Config.get_player(name)

        if player is None:
            return {
                "command": "/error",
                "message": "no such player \"{}\"".format(name),
                "error_command": "/room/create"
            }

        screen_name = player.get("screen_name", name)

        d_size = data.get("board_size")
        p_size = player.get("board_size")

        if d_size is not None and p_size is not None:
            if d_size != p_size:
                return {
                    "command": "/error",
                    "message": "board_size: got {d} but {p} was required".format(d = d_size, p = p_size),
                    "error_command": "/room/create"
                }
            else:
                board_size = d_size
        elif d_size is None and p_size is None:
            board_size = Config.get_global("game", "board_size", default = 8)
        else:
            board_size = d_size or p_size

        self.opponent = Builder.build_player({ "board_size": board_size }, name)

        self.scene = Scene.COLOR

        return {
            "command": "/room/create",
            "opponent": {
                "name": name,
                "screen_name": screen_name,
                "board_size": board_size
            }
        }

    def start_game(self, color):
        if self.scene != Scene.COLOR:
            return {
                "command": "/error",
                "message": "incorrect scene: now scene is {}".format(self.scene.name),
                "error_command": "/game/start"
            }

        if color == "black":
            self.you.initialize(Piece.BLACK)
            self.opponent.initialize(Piece.WHITE)
            black = self.you
            white = self.opponent
        elif color == "white":
            self.you.initialize(Piece.WHITE)
            self.opponent.initialize(Piece.BLACK)
            black = self.opponent
            white = self.you
        elif color == "" or color == "random":
            index = random.randint(0, 1)
            players = [self.you, self.opponent]
            players[index].initialize(Piece.BLACK)
            players[1 - index].initialize(Piece.WHITE)
            black = players[index]
            white = players[1 - index]
        else:
            return {
                "command": "/error",
                "message": "incorrect color {}: \"\", \"black\", \"white\" or \"random\"".format(color)
            }

        self.game = Game(black, white)

        if self.game_thread is not None:
            self.game_thread.join()

        self.game_thread = threading.Thread(target = self.game.play)
        self.game_thread.start()

        self.scene = Scene.BOARD

    def action_move(self, data):
        if self.scene != Scene.BOARD:
            return {
                "command": "/error",
                "message": "incorrect scene: game is not started"
            }

        self.write_queue.put({
            data.get("value", "")
        })

    def serve(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with contextlib.closing(sock):
            sock.bind((host, port))
            sock.listen(1)

            while True:
                connection, address = sock.accept()
                self.handle(connection)
