import _common

import argparse
import sys
import os

from application.system.network_agent import NetworkAgent


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="server host")
    parser.add_argument("--port", help="server port", type=int)
    args = parser.parse_args()

    host = args.host or os.environ["SERVER_HOST"]
    port = args.port or int(os.environ["SERVER_PORT"])

    NetworkAgent().serve(host, port)
