import React from 'react';

class Board extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  move(x, y) {
    if (this.props.movable.filter((v) => v[0] === x && v[1] === y).length === 1) {
      this.props.move(x, y);
    }
  }

  render() {
    return (
      <div style={{ position: "relative" }}>
        {
          this.props.board.map((row, i) =>
            row.map((v, j) =>
              {
                var color = "green";
                if (v === 1) {
                  color = "black";
                } else if (v === 2) {
                  color = "white";
                }

                return <div
                  key={String(i) + ":" + String(j)}
                  style={{ position: "absolute", top: i * 60, left: j * 60, width: 60, height: 60, backgroundColor: color }}
                  onClick={this.move.bind(this, j, i)}
                ></div>;
              }
            )
          )
        }
      </div>
    );
  }
}

export default Board;
