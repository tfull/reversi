import _common

import sys
import threading

from application.system import Config, Process, GuiAgent
from application.player import Builder


def main(player_name):
    dummy_config = { "board_size": 8 }
    config = dict(Config.get_global("game", default={}), **dummy_config)

    you = Builder.build_gui_player(config, "You")
    opponent = Builder.build_player(config, player_name)

    gui_agent = GuiAgent(you, opponent)
    gui_agent.main_loop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("few arguments\n")
        sys.exit(1)

    main(sys.argv[1])
