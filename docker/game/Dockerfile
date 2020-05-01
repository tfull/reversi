FROM python:3.7

RUN useradd -m game

COPY ./requirements.txt /home/game/
COPY ./application /home/game/application
COPY ./commands /home/game/commands

RUN chown -R game:game /home/game
RUN pip install -r /home/game/requirements.txt
