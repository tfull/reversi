FROM node:12.16.1

RUN useradd -m client

COPY ./web/client/public /home/client/public
COPY ./web/client/src /home/client/src
COPY ./web/client/package.json /home/client/package.json

RUN chown -R client:client /home/client


USER client
WORKDIR /home/client

RUN npm install
