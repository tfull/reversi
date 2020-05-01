import React from 'react';

class Board extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  move(x, y) {
    if (this.props.scene !== "board") {
      return;
    }

    if (this.props.movable.filter((v) => v[0] === x && v[1] === y).length === 1) {
      this.props.move(x, y);
    }
  }

  playAgain() {
    if (this.props.scene !== "result") {
      return;
    }

    this.props.playAgain();
  }

  render() {
    const cell_size = 60;
    const stone_size = parseInt(cell_size * 0.9);

    /*
    if (this.props.board === null) {
      this.props.goToLobby();
      return <div>Redirect</div>;
    }
    */

    return (
      <div style={{ margin: 80 }}>
        <table style={
          {
            borderCollapse: "collapse",
            backgroundColor: "#008800",
            border: "solid 2px black"
          }
        }>
          {
            this.props.board.map((row, i) =>
              <tr key={String(i)}>
                {
                  row.map((v, j) =>
                    {
                      return <td
                        key={String(j)}
                        style={{ width: cell_size, height: cell_size, border: "solid 1px black" }}
                        onClick={this.move.bind(this, j, i)}
                      >
                        {
                          (v === 1 || v === 2) &&
                          <div style={
                            {
                              backgroundColor: (v === 1 ? "black" : "white"),
                              width: stone_size,
                              height: stone_size,
                              margin: "auto",
                              borderRadius: "50%"
                            }
                          }></div>
                        }
                      </td>;
                    }
                  )
                }
              </tr>
            )
          }
        </table>
        {
          this.props.scene === "result" &&
          <div>
            <div onClick={this.playAgain.bind(this)}>もう一度</div>
          </div>
        }
      </div>
    );
  }
}

export default Board;
