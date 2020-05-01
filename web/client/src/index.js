import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';

class Test extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  render() {
    return (
      <div>This is Test Component</div>
    );
  }
}

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
