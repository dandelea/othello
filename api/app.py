'''This script manages the flask server'''

import logging
from logging.handlers import RotatingFileHandler

from bson import ObjectId

from flask import Flask, request
from flask_cors import CORS

import database

from MongoJSONEncoder import MongoJSONEncoder

app = Flask(__name__) # pylint: disable=invalid-name
app.json_encoder = MongoJSONEncoder
app.config.from_object('config')
CORS(app)

# Logging Configuration
formatter = logging.Formatter( # pylint: disable=invalid-name
    '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
)
logHandler = RotatingFileHandler('info.log', maxBytes=10000, backupCount=1) # pylint: disable=invalid-name
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)

# Routes

@app.route('/api/test', methods=['GET'])
def test():
    """ Test OK """
    return ({'status': 'OK'}, 200)

@app.route('/api/register', methods=['POST'])
def register():
    """Register the player(ip,web) in the database."""
    body = request.get_json()
    database.new_player(
        request.remote_addr,
        request.headers['User-Agent'],
        body['mode'],
        body['online'],
        app.logger
    )
    return ('', 204)

@app.route('/api/stillalive', methods=['GET'])
def still_alive():
    """Beacon."""
    data = database.still_alive(
        request.remote_addr, request.headers['User-Agent'],
        app.logger)
    return data

@app.route('/api/game', methods=['POST'])
def get_game():
    """Returns JSON representation of the object with game_id."""
    body = request.get_json()
    game_id = ObjectId(body['game_id'])
    game = database.find_game_by_id(
        game_id, request.remote_addr,
        request.headers['User-Agent'])
    return {'game': game}

@app.route('/api/pair', methods=['GET'])
def pair():
    """Pairs two players to a new game, if possible. Serves game_id."""
    player1 = database.find_player_by_ip(
        request.remote_addr,
        request.headers['User-Agent'])
    player1_id = None
    if player1:
        player1_id = player1['_id']
    else:
        return ({'status': 'KO', 'message': 'User not found'}, 404)
    opponents = database.available_opponents(
        request.remote_addr, request.headers['User-Agent'])
    if opponents:
        id_player2 = opponents[0]['_id']
        game_id = database.pair_players(player1_id, id_player2, app.logger)
        data = {'game_id': game_id}
    else:
        data = {}
    return data

@app.route('/api/single', methods=['GET'])
def single():
    """Starts a new game for a single player."""
    player1 = database.find_player_by_ip(
        request.remote_addr,
        request.headers['User-Agent'])
    player1_id = None
    if player1:
        player1_id = player1['_id']
    else:
        return ({'status': 'KO', 'message': 'User not found'}, 404)
    game_id = database.single_player(player1_id, app.logger)
    if game_id:
        data = {'game_id': game_id}
        return data
    return ({'status': 'KO', 'message': 'Game not found'}, 404)

@app.route('/api/play', methods=['POST'])
def play():
    """Do a play from the player to its actual game."""
    body = request.get_json()
    ip_address, web_browser = request.remote_addr, request.headers['User-Agent']
    x, y = body['x'], body['y'] # pylint: disable=invalid-name
    result = database.play(ip_address, web_browser, x, y, app.logger)
    return result

@app.route('/api/exit', methods=['GET'])
def exit_app():
    """Exit the game. Removes the game from the player"""
    ip_address, web_browser = request.remote_addr, request.headers['User-Agent']
    database.exit_app(ip_address, web_browser, app.logger)
    return ('', 204)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=5000, debug=True)
