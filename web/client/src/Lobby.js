import React from 'react';

class Lobby extends React.Component {
  constructor(props) {
    super(props);
      this.state = {
    };
  }

  render() {
    return (
      <div>
        {
          this.props.players.map((record) =>
            <div>{record.name}</div>
          )
        }
      </div>
    );
  }
}

export default Lobby;
