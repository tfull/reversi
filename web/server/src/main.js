const net = require('net');
const ws = require('ws');

const server = new ws.Server({ port: 8079 });

server.on("connection", socket => {
    console.log(socket);
    console.log("Web: open");

    var client = new net.Socket();

    client.setEncoding("utf8");

    client.connect("8000", "game", () => {
        console.log("Game: open");
    });

    client.on("data", message => {
        console.log("Game: " + message);
        socket.send(message);
    });

    socket.on("message", message => {
        console.log("Web: " + message);
        client.write(message + "\n");
        console.log("sent message");
    });

    socket.on("close", () => {
        console.log("Web: close");
        client.end();
    });
});
