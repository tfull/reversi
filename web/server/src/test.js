const WebSocket = require('ws');
 
const ws = new WebSocket('ws://localhost:8079');
 
ws.on('open', function open() {
  ws.send("{\"command\":\"/player/list\"}");
});
 
ws.on('message', function incoming(data) {
  console.log(data);
});
