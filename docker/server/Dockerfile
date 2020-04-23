FROM node:12.16.1

RUN useradd -m server

COPY ./web/server/package.json /home/server/package.json

RUN chown -R server:server /home/server
