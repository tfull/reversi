import React from 'react';
import Lobby from './Lobby';
import Board from './Board';
import Color from './Color';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      scene: "lobby",
      players: [],
      board: null,
      debug: "connected"
    };

    this.selectPlayer = this.selectPlayer.bind(this);
    this.startGame = this.startGame.bind(this);
  }

  componentDidMount() {
    this.socket = new WebSocket("ws://" + process.env.REACT_APP_SERVER_AUTHORITY);
    this.setNetworkHandler();
  }

  setNetworkHandler() {
    this.socket.onopen = () => {
      this.setState({
        debug: "connected"
      });
      this.requestPlayerList();
    };

    this.socket.onmessage = (event) => {
      this.setState({ debug: "read" })
      this.readMessage(JSON.parse(event.data));
    }

    this.socket.onclose = () => {
      this.setState({
        debug: "disconnected",
        scene: "error"
      });
    }
  }

  send(data) {
    this.socket.send(JSON.stringify(data));
  }

  readMessage(object) {
    const command = object.command;

    this.setState({ debug: command });

    if (command === "/player/list") {
      this.setState({
        players: object.players
      });
    } else if (command === "/room/create") {
      this.setState({
        board_size: object.board_size,
        scene: "color"
      });
    } else if (command === "/game/start") {
      this.initializeBoard(this.state.board_size);
      this.setState({
        scene: "board"
      });
    } else {
      this.setState({
        scene: "error",
        debug: command
      });
    }
  }

  render() {
    if (this.state.scene === "lobby") {
      return (
        <div id="App">
          <Lobby players={this.state.players} selectPlayer={this.selectPlayer} />
          <div id="debug">{this.state.debug}</div>
        </div>
      );
    } else if (this.state.scene === "color") {
      return (
        <Color startGame={this.startGame} />
      );
    } else if (this.state.scene === "board") {
      return (
        <Board board={this.state.board} />
      );
    } else {
      return (
        <div id="Error">
          <div id="error">エラーが発生しました</div>
          <div id="debug">{this.state.debug}</div>
        </div>
      );
    }
  }

  initializeBoard(size) {
    var board = Array(size).fill(0).map((_, i) => Array(size).fill(0).map((_, j) => 0));

    board[Math.floor(size / 2) - 1][Math.floor(size / 2) - 1] = 1;
    board[Math.floor(size / 2)][Math.floor(size / 2) - 1] = 2;
    board[Math.floor(size / 2) - 1][Math.floor(size / 2)] = 2;
    board[Math.floor(size / 2)][Math.floor(size / 2)] = 1;

    this.setState({
      board: board
    });
  }

  requestPlayerList() {
    this.send({
      command: "/player/list"
    });
  }

  selectPlayer(name) {
    this.send({
      command: "/room/create",
      name: name
    });
  }

  startGame(color) {
    this.send({
      command: "/game/start",
      color: color
    });
  }
}

export default App;
