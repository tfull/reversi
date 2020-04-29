const net = require('net');
const ws = require('ws');

const server = new ws.Server({ port: 8079 });

server.on("connection", socket => {
    console.log("Web: open");
    var buffer = "";

    var client = new net.Socket();

    client.setEncoding("utf8");

    client.connect("8000", "game", () => {
        console.log("Game: open");
    });

    client.on("data", message => {
        console.log("Game: " + message);
        buffer += message;

        while (message.indexOf("\n") >= 0) {
            var index = message.indexOf("\n");
            socket.send(message.slice(0, index));
            message = message.slice(index + 1);
        }
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
