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
      color: null,
      movable: [],
      debug: "connected"
    };

    this.requestSelectPlayer = this.requestSelectPlayer.bind(this);
    this.requestStartGame = this.requestStartGame.bind(this);
    this.requestMove = this.requestMove.bind(this);
    this.playAgain = this.playAgain.bind(this);
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
      console.log(event.data);
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
        scene: "board",
        color: object.color
      });
    } else if (command === "/game/move") {
      this.move(object.piece, object.target);
    } else if (command === "/game/notice/your_turn") {
      this.setState({
        movable: object.movable
      });
    } else if (command === "/game/complete") {
      this.setState({
        scene: "result"
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
          <Lobby players={this.state.players} selectPlayer={this.requestSelectPlayer} />
          <div id="debug">{this.state.debug}</div>
        </div>
      );
    } else if (this.state.scene === "color") {
      return (
        <Color startGame={this.requestStartGame} />
      );
    } else if (this.state.scene === "board") {
      return (
        <Board board={this.state.board} scene={"board"} movable={this.state.movable} move={this.requestMove} />
      );
    } else if (this.state.scene === "result") {
      return (
        <Board board={this.state.board} scene={"result"} playAgain={this.playAgain} />
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
    let board = Array(size).fill(0).map((_, i) => Array(size).fill(0).map((_, j) => 0));
    let half = Math.floor(size / 2)

    board[half - 1][half - 1] = 1;
    board[half][half - 1] = 2;
    board[half - 1][half] = 2;
    board[half][half] = 1;

    this.setState({
      board: board
    });
  }

  move(piece, target) {
    let v = 0;

    if (piece === "black") {
      v = 1;
    } else if (piece === "white") {
      v = 2;
    }

    var new_board = this.state.board.slice();

    for (let i = 0; i < target.length; i++) {
      let x = target[i][0];
      let y = target[i][1];
      new_board[y][x] = v;
    }

    this.setState({
      board: new_board
    });
  }

  playAgain() {
    this.setState({
      scene: "color"
    });
  }

  requestPlayerList() {
    this.send({
      command: "/player/list"
    });
  }

  requestSelectPlayer(name) {
    this.send({
      command: "/room/create",
      name: name
    });
  }

  requestStartGame(color) {
    this.send({
      command: "/game/start",
      color: color
    });
  }

  requestMove(x, y) {
    this.send({
      command: "/game/move",
      value: [x, y]
    });
  }
}

export default App;
