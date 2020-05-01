import React from 'react';

class Lobby extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  selectPlayer(name) {
    this.props.selectPlayer(name);
  }

  render() {
    return (
      <div>
        {
          this.props.players.map((record) =>
            <div key={record.name} onClick={this.selectPlayer.bind(this, record.name)}>{record.screen_name}</div>
          )
        }
      </div>
    );
  }
}

export default Lobby;
