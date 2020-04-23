import React from 'react';
import Lobby from './Lobby';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      scene: "lobby",
      players: [],
      debug: "connected"
    };

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
    this.setState({ debug: object.command });
    if (object.command === "/player/list") {
      this.setState({
        players: object.players
      });
    } else {
      this.setState({
        scene: "error",
        debug: object.command
      });
    }
  }

  render() {
    if (this.state.scene === "lobby") {
      return (
        <div id="App">
          <Lobby players={this.state.players} />
          <div id="debug">{this.state.debug}</div>
        </div>
      );
    } else {
      return (
        <div>
          <div id="error">エラーが発生しました</div>
          <div id="debug">{this.state.debug}</div>
        </div>
      );
    }
  }

  requestPlayerList() {
    this.send({
      command: "/player/list"
    });
  }
}

export default App;
