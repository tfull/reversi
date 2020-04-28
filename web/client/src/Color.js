import React from 'react';

class Color extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  startGame(color) {
    this.props.startGame(color);
  }

  render() {
    return (
      <div style={{ backgroundColor: "darkgreen" }}>
        <div style={{ position: "relative" }}>
          <div
            style={{ position: "absolute", top: 0, left: 0, width: 200, height: 300 }}
            onClick={this.startGame.bind(this, "black")}
          >黒（先攻）</div>
          <div
            style={{ position: "absolute", top: 0, left: 220, width: 200, height: 300 }}
            onClick={this.startGame.bind(this, "white")}
          >白（後攻）</div>
          <div
            style={{ position: "absolute", top: 0, left: 440, width: 200, height: 300 }}
            onClick={this.startGame.bind(this, "random")}
          >おまかせ</div>
        </div>
      </div>
    );
  }
}

export default Color;
