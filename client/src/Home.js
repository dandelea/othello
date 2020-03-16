import React from 'react';
import './Home.css';
import logo from './img/fondo.png'
import { stillAlive, register, single, pair } from './clients/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'
const classNames = require('classnames');

class Home extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      player_selected_mode: false,
      player_selected_online: false,
      selection_mode: 0,
      online_mode: 0,
    }

    this.click = this.click.bind(this);
    this.interval = this.interval.bind(this);

    window.setInterval(this.interval, 1000);
    document.onclick = this.click    
  }

  componentDidMount() {
    stillAlive().then((response) => {
      if (response.game && this.props.location.pathname === '/') {
        this.props.history.push('/game', {
          game_id: response.game.id
        });
      }
    }).catch((error) => {
      console.error(error);
    })
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Othello</h1>
          <div className="wrapper">
            <div id="modal-online" className="modal">
              <div className="modal-content">
                <FontAwesomeIcon icon={faSpinner} />
                <p>Buscando jugadores...</p>
              </div>
            </div>
            <div id="modal-offline" className="modal">
              <div className="modal-content">
                <FontAwesomeIcon icon={faSpinner} />
                <p>Preparando partida...</p>
              </div>
            </div>
            {!this.state.player_selected_mode && 
              <div>
                <a href="#" className={classNames({
                  selected: this.state.selection_mode === 0,
                  button: true,
                })}>
                  Selección manual
                </a>
                <a href="#" className={classNames({
                  selected: this.state.selection_mode === 1,
                  button: true,
                })}>
                  Selección por barrido
                </a>
              </div>
            }
            {this.state.player_selected_mode && !this.stateplayer_selected_online &&
              <div>
                <a href="#" onClick={() => {this.setState({online_mode: 0})}} className={classNames({
                  selected: this.state.online_mode === 0 && this.state.selection_mode === 1,
                  button: true,
                  'online-button': true,
                })}>
                  Jugar contra la máquina
                </a>
                <a href="#" onClick={() => {this.setState({online_mode: 1})}} className={classNames({
                  selected: this.state.online_mode === 1 && this.state.selection_mode === 1,
                  button: true,
                  'online-button': true,
                })}>
                  Jugar online
                </a>
              </div>
            }
            <ul>
              {this.state.player_selected_online && this.state.selection_mode === 0 &&
                <li>Selección manual</li>
              }
              {this.state.player_selected_online && this.state.selection_mode === 1 &&
                <li>Selección por barrido</li>
              }
              {this.state.player_selected_online && this.state.online_mode === 0 &&
                <li>Seleccionado modo de un jugador</li>
              }
              {this.state.player_selected_online && this.state.online_mode === 1 &&
                <li>Seleccionado modo online</li>
              }
            </ul>
            {this.state.player_selected_online && 
              <React.Fragment>
                <p>Puede cambiar los ajustes recargando la página</p>
                <h2>Pulsa para comenzar</h2>
              </React.Fragment>
            }
          </div>
  
          <div className="cute">
            <img src={logo} className="App-logo" alt="logo" />
          </div>
        </header>
      </div>
    );
  }

  click() {
    if (this.props.location.pathname === '/') {
      if (this.state.player_selected_mode) {
        if (this.state.player_selected_online) {
          document.getElementById("modal-offline").style.display = "block";
          register(this.state.selection_mode, this.state.online_mode).then((response) => {
            if (this.state.online_mode) {
              document.getElementById("modal-offline").style.display = "none";
              document.getElementById("modal-online").style.display = "block";
              pair().then((response) => {
                if (response.game_id) {
                  this.props.history.push('/game', {
                    game_id: response.game.id,
                  })
                }
              }).catch((error) => {
                console.error(error);
              })
            } else {
              single().then((response) => {
                if (response.game_id) {
                  this.props.history.push('/game', {
                    game_id: response.game_id,
                  })
                }
              }).catch((error) => {
                console.error(error);
              })
            }
          }).catch((error) => {
            console.error(error);
          });
        } else {
          this.setState({
            player_selected_online: true,
          })
        }
      } else {
        this.setState({
          player_selected_mode: true,
        })
      }
    }
  }

  interval() {
    if (!this.state.player_selected_mode) {
      this.setState({
        selection_mode: 1 - this.state.selection_mode,
      });
    } else {
      if (this.state.selection_mode === 1 && !this.state.player_selected_online) {
        this.setState({
          online_mode: 1 - this.state.online_mode,
        });
      }
    }
  }
}

export default Home;