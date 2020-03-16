
import Home from './Home'
import Game from './Game'
import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

class App extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Router>
        <Switch>
          <Route exact path='/' component={Home} />
          <Route exact path='/game' component={Game} />
        </Switch>
      </Router>
    );
  }
}

export default App;