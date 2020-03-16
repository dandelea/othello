import React from 'react';
import './Game.css';

import { game, play, stillAlive, exitApp } from './clients/api';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHome, faSpinner } from '@fortawesome/free-solid-svg-icons'

import $ from 'jquery';
const classNames = require('classnames');
const images = {
  avatar_water: require('./img/avatar_water.png'),
  avatar_grass: require('./img/avatar_grass.png'),
  avatar: require('./img/avatar.png'),
  
  instructions1: require('./img/instructions1.png'),
  animation: require('./img/animation.gif'),
  king: require('./img/king.png'),

  water: require('./img/water.png'),
  grass: require('./img/grass.png'),
}

class Game extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      game_id: null,
      show_instructions: true,

      selecting_index: 0,

      game: null,
      player1: null,
      player2: null,
      sync: false,
    }

    if (this.props.location.state && this.props.location.state.game_id) {
      this.state.game_id = this.props.location.state.game_id;
    } else {
      this.props.history.push('/');
    }

    this.interval = this.interval.bind(this);
    this.onclick = this.onclick.bind(this);
    this.player_color = this.player_color.bind(this);
    this.is_option = this.is_option.bind(this);
    this.click_play = this.click_play.bind(this);
    this.selection = this.selection.bind(this);
    this.findCoordinates = this.findCoordinates.bind(this);
    this.equals = this.equals.bind(this);
    this.my_turn = this.my_turn.bind(this);
    this.blank_left = this.blank_left.bind(this);
    this.play = this.play.bind(this);
    this.gameover = this.gameover.bind(this);
    this.return_home = this.return_home.bind(this);
    this.temporary_selecting = this.temporary_selecting.bind(this);
    this.speechText = this.speechText.bind(this);
    this.gameover_text = this.gameover_text.bind(this);
    this.score = this.score.bind(this);
    this.intervalAlive = this.intervalAlive.bind(this);

    document.onclick = this.onclick;
    window.setInterval(this.interval, 1000);
    window.setInterval(this.intervalAlive, 4000);
  }

  render() {
    let repeatTile = (matrix, player_color, N) => {
      let result = [];
      for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
          let tile = matrix[i][j];
          result.push(
            <div className="square" onClick={() => {this.click_play(i, j)}}>
              <div className={classNames({
                blank: tile === 0,
                white: tile === 1,
                black: tile === 2,
                options_white: this.is_option([i, j]) && player_color === 'white',
                options_black: this.is_option([i, j]) && player_color === 'black',
                selection_white: this.selection([i, j]) && player_color === 'white',
                selection_black: this.selection([i, j]) && player_color === 'black',
              })}></div>
            </div>
          )
        }
      }
      return result;
    }
    let range = n => Array.from(Array(n).keys())
    return (
      <div className="wrapper">
	      <img alt="avatar" src={this.player_color() === 'white' ? images.avatar_water : this.player_color() === 'black' ? images.avatar_grass : images.avatar} className="avatar"/>
	      <div className="speech-bubble"></div>
	      <div className="gameBoard">

		      {this.state.show_instructions && 
            <div id="instructions">
              <div>
                <img alt="Instrucciones" src={images.instructions1} />
                <p>Alinea fichas para ocupar el campo</p>
              </div>
              <div>
                <p>Salta fichas del oponente para convertirlas</p>
                <img alt="Animación 01" src={images.animation} />
              </div>
              <div>
                <img alt="Ganador" src={images.king} />
                <p>Gana quien tenga más fichas</p>
              </div>
		        </div>
          }

		      {this.gameover() &&
            <div className="gameover">
              <h3>Fin de la partida</h3>
              <div className="final-score" style={{'margin-bottom': '5%'}}>
                {this.gameover_text()}
              </div>
              <div style={{'margin-bottom': '10%'}}>
                <a href="#" className="button" onClick={() => {this.return_home()}}>
                  <FontAwesomeIcon icon={faHome} />
                </a>
              </div>
              <div>por <a href="http://www.dandelea.com">Daniel de los Reyes Leal</a></div>
            </div>
          }

          {!this.state.show_instructions 
            && (
              !this.state.sync || (!this.my_turn() && this.state.game && !this.state.game.gameover)
            ) &&
            <div id="waiting-screen">
              <span className="final-score">
                <p>Esperando al otro jugador...</p>
                <FontAwesomeIcon icon={faSpinner} />
              </span>
            </div>
          }

          { this.state.game && this.state.game.matrix && this.state.game.matrix.length &&
            repeatTile(this.state.game.matrix, this.player_color(), 8)
          }
	      </div>
	      <div className="sidebar">
          {range(12).map(() => {
            return (
              <div className="stone gametile"></div>
            )
          })}
		      <div className="scoreBoard">
            <h2>Quedan</h2>
            <span className="score">{this.blank_left()}</span>
            <div className="loot">
              <ul className="lootracker">
                <li><span>{this.score('white')}</span> x <img alt="Agua" src={images.water} /></li>
                <li><span>{this.score('black')}</span> x <img alt="Hierba" src={images.grass} /></li>
              </ul>
			      </div>
	        </div>
	      </div>

        <audio preload="auto" id={this.player_color() === 'white' ? 'pop': ''}>
          <source src="./sound/pop1.mp3"></source>
        </audio>
        <audio preload="auto" id={this.player_color() === 'black' ? 'pop': ''}>
          <source src="./sound/pop2.mp3"></source>
        </audio>
        <audio preload="auto" id="win" >
            <source src="./sound/win.mp3"></source>
            No audio :(
        </audio>
      </div>
    );
  }

  componentDidMount() {
    game(this.state.game_id).then((response) => {
      this.setState({
        game: response.game,
      })
    }).catch((error) => {
      console.error(error);
    });
  }

  interval() {
    if (this.my_turn()) {
      if (this.state.selecting_index + 1 >= this.state.game.possible_moves.length) {
        this.setState({
          selecting_index: 0,
        });
      } else {
        this.setState({
          selecting_index: this.state.selecting_index + 1,
        });
      }
    }
  }

  onclick() {
    if (this.state.show_instructions) {
      this.setState({
        show_instructions: false,
      });
    } else {
      this.click();
    }
  }

  click() {
    if (this.state.sync) {
      if (this.my_turn() && !this.gameover() && this.state.player1.selection_mode === 1) {
        let temporary_selecting = this.state.temporary_selecting();
        this.play(temporary_selecting[0], temporary_selecting[1]);
      } else {
        if (this.gameover() && this.state.player1.selection_mode === 1) {
          this.return_home();
        }
      }
    }
  }

  player_color() {
    let result = null;
    if (this.state.sync && this.state.game) {
      let found = this.state.game.players.indexOf(this.state.player1.id);
      result = found === 0 ? 'white' : 'black';
    }
    return result;
  }

  is_option(coordinates) {
    return this.state.sync && this.my_turn() && this.findCoordinates(coordinates) > -1;
  }

  click_play(x, y) {
    if (this.state.sync &&
        this.my_turn() && !this.gameover() && this.state.player1.selection_mode === 0 && this.is_option([x, y])) {
          this.play(x, y);
    }
  }

  selection(coordinates) {
    let result = false;
    if (this.state.sync &&
      this.my_turn() && this.state.player1.selection_mode === 1) {
        result = this.findCoordinates(coordinates) > -1 && this.equals(this.temporary_selecting(), coordinates);
    }
    return result;
  }

  findCoordinates(coordinates){
    var r = -1;
    for (var i = 0; i < this.state.game.possible_moves.length; i++) {
        if (this.equals(this.state.game.possible_moves[i], coordinates)) {
            r = i;
        }
    }
    return r;
  }

  equals(coordinates1, coordinates2) {
    return coordinates1[0] === coordinates2[0] && coordinates1[1] === coordinates2[1];
  }

  my_turn() {
    return this.state.sync && this.state.game && this.state.player1 && this.state.game.turn === this.state.player1.id
  }

  blank_left() {
    var r = null;
    if (this.state.sync && this.state.game) {
      var suma = Object.values(this.state.game.scoreboard).reduce((a, b) => a + b, 0)
      if (suma) {
        r = 64 - suma;
      }
    }
    return r;
  }

  play(x, y) {
    play(x, y).then((response) => {
      let game = this.state.game;
      game.matrix = response.matrix;
      game.possible_moves = [];
      game.gameover = response.gameover;
      this.setState({
        game: game,
      })
      this.speechText(300);
      $("#pop")[0].play();
    }).catch((error) => {
      console.error(error);
    })
  }

  gameover() {
    var result = false;
    if (this.state.sync && this.state.game) {
      result = this.state.game.gameover;
      if (result) {
        stillAlive().then((response) => {
          this.setState({
            game: response,
          })
          $("#win")[0].play();
        }).catch((error) => {
          console.error(error);
        });
      }
    }
    return result;
  }

  return_home() {
    if (this.state.game.gameover) {
      exitApp().then(() => {
        this.props.history.push('/');
      }).catch((error) => {
        console.error(error);
      })
    }
  }

  temporary_selecting() {
    if (this.state.my_turn()) {
      return this.state.game.possible_moves[this.state.selecting_index];
    } else {
      return null;
    }
  }

  speechText(delay) {
      var speech_texts = ["Sigue asi", "WOW!", "Bien", "Bien hecho", "Buena jugada"];
      var text = speech_texts[Math.round(Math.random()*(speech_texts.length-1))];
      $(".speech-bubble").stop(true, false).animate({opacity: "1"},200);
      $(".speech-bubble").text(text);
      $(".speech-bubble").delay(delay).animate({opacity:"0"},40);
  }

  gameover_text() {
    var r = null;
    if (this.gameover()) {
        var player1_id = this.state.player1.id;
        var player2 = this.state.player2;
        var scoreboard = this.state.game.scoreboard;
        if (player2) {
            var player2_id = player2.id;
            if (scoreboard[player1_id] === scoreboard[player2_id]) {
                r = "empate";
            } else {
                if (scoreboard[player1_id] > scoreboard[player2_id]) {
                    r = "ganaste";
                } else {
                    r = "perdiste";
                }
            }
        } else {
            r = "oponente abandonó";
        }
    }
    return r;
  }

  score(color) {
    var r = null;
    if (this.state.sync && this.state.game) {
      if (color === 'white') {
        r = this.state.game.scoreboard[this.state.game.white];
      }
      if (color === 'black') {
          if (this.state.game.black === "AI") {
              r = this.state.game.scoreboard.AI;
          } else {
              r = this.state.game.scoreboard[this.state.game.black];
          }
      }
    }
    return r;
  }

  intervalAlive() {
    stillAlive().then((response) => {
      this.setState({
        game: response.game,
        player1: response.player1,
        player2: response.player2,
        sync: response.sync,
      })
    }).catch(error => {
      console.error(error)
    })
  }

}

export default Game