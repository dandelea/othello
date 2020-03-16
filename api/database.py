'''Database module script.
Manages the mongo database and the server queries.'''

import datetime
import pickle

import numpy
import pytz
from bson.binary import Binary
from pymongo import MongoClient

from models import Game, Piece

from config import MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOSTNAME, MONGO_PORT

CONNECTION_STRING = 'mongodb://{0}:{1}@{2}:{3}'.format(
    MONGO_USERNAME,
    MONGO_PASSWORD,
    MONGO_HOSTNAME,
    MONGO_PORT
)

#------------------------------------------#
#              SCHEDULED TASKS             #
#------------------------------------------#

def ai_plays(app_logger):
    """Search for games with AI turn. Execute a play."""
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    games = database.games
    for game in games.find({'gameover': False, 'turn': 'AI'}):
        game_id = game['_id']
        game['matrix'] = pickle.loads(game['matrix'])
        game = Game(
            game['white'], game['black'],
            game['matrix'], game['turn'])

        app_logger.info('AI juega al juego {0}'.format(str(game_id)))
        game.play_ai()

        copy_save = dict(game)
        copy_save['matrix'] = Binary(
            pickle.dumps(copy_save['matrix'], protocol=2))
        copy_save['possible_moves'] = numpy.array(
            copy_save['possible_moves']).tolist()
        games.update_one({'_id': game_id}, {'$set': copy_save})
    client.close()

#--------------------------------------#
#            MODIFICATIONS             #
#--------------------------------------#

def still_alive(ip_address, web_browser, app_logger):
    """The beacon /still_alive resets the last_seen date for the
    actual player and returns the actual state of the game and its
    opponent.
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    :param app_logger: Flask app logger
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    games = database.games

    player1 = players.find_one({'ip': ip_address, 'web_browser': web_browser})
    player2 = None
    game = None
    if player1:
        players.update_one(
            {'_id': player1['_id']},
            {'$set': {
                'date': datetime.datetime.now(pytz.utc)
                }
            }
        )
        if player1['game_id']:
            game = games.find_one({'_id': player1['game_id']})
            game['matrix'] = pickle.loads(game['matrix']).tolist()

            if player1['online_mode']:
                index_player2 = int(not game['players'].index(player1['_id']))
                player2_id = game['players'][index_player2]
                player2 = find_player_by_id(player2_id)
                player2['id'] = str(player2['_id'])
                del player2['_id']
                player2['game_id'] = str(player2['game_id'])
                player2['date'] = str(player2['date'])['$date']
            else:
                if game['turn'] == 'AI':
                    ai_plays(app_logger)
                player2 = {
                    'game_id': str(game['_id'])
                }

            game['id'] = str(game['_id'])
            del game['_id']
            game['players'] = [str(player) if player != 'AI' else 'AI' for player in game['players']]
            game['turn'] = str(game['turn']) if game['turn'] != 'AI' else 'AI'
            game['white'] = str(game['white']) if game['white'] != 'AI' else 'AI'
            game['black'] = str(game['black']) if game['black'] != 'AI' else 'AI'
        player1['id'] = str(player1['_id'])
        del player1['_id']
        player1['game_id'] = str(player1['game_id'])
        player1['date'] = str(player1['date'])
    client.close()
    return {'player1': player1,
            'player2': player2,
            'game': game,
            'sync': True}

def new_player(ip_address, web_browser, selection_mode,
               online_mode, app_logger):
    """Register a new player in the database. If already registered,
    updates its information.
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    :param selection_mode: Manual or automatic selection
    :param online_mode: Online activated or not
    :param app_logger: Flask app logger
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    player = players.find_one({'ip': ip_address, 'web_browser': web_browser})
    if player:
        players.update_one(
            {'_id': player['_id']},
            {'$set': {
                'game_id': None,
                'date': datetime.datetime.now(pytz.utc),
                'selection_mode': selection_mode,
                'online_mode': online_mode
                }
            }
        )
        app_logger.info("Updating player registration of " + str(player['_id']))
    else:
        player = {
            "ip" : ip_address,
            "web_browser" : web_browser,
            "date" : datetime.datetime.now(pytz.utc),
            "game_id" : None,
            "selection_mode" : selection_mode,
            "online_mode": online_mode
        }
        players.insert_one(player)
        app_logger.info("Registrating new player " + str(player['_id']))

    client.close()
    return player['_id']

def pair_players(id_player1, id_player2, app_logger):
    """Pair two players registered in the database,
    with a new game.
    :param id_player1: ID of player1
    :param id_player2: Id of player2 (opponent)
    :param app_logger: Flask app logger
    """
    game_id = None
    new_game = dict(Game(id_player1, id_player2))
    new_game['matrix'] = Binary(pickle.dumps(new_game['matrix'], protocol=2))
    new_game['possible_moves'] = numpy.array(
        new_game['possible_moves']).tolist()
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    games = database.games
    players = database.players

    result = players.find_one({'_id': id_player1})
    result2 = players.find_one({'_id': id_player2})
    if result and result2:
        if (
                result['game_id'] is None and
                result2['game_id'] is None and
                result['online_mode'] and
                result2['online_mode']
        ):
            games.insert_one(new_game)
            game_id = new_game['_id']
            players.update_one({'_id':id_player1}, {'$set':{'game_id':game_id}})
            players.update_one({'_id':id_player2}, {'$set':{'game_id':game_id}})
            game_id = str(game_id)
        else:
            if result['game_id'] != None:
                app_logger.error(
                    "Requested pairing player1 already in a game. game_id: {0} player1_id: {1}".format(
                        result['game_id'], str(result['_id'])))
            if result2['game_id'] != None:
                app_logger.error(
                    "Requested pairing player2 already in a game. game_id: {0} player2_id: {1}".format(
                        result2['game_id'], str(result2['_id'])))
            if not result['online_mode']:
                app_logger.error(
                    "Player 1 requested offline only play: player1_id: {0}".format(
                        str(result['_id'])))
            if not result2['online_mode']:
                app_logger.error(
                    "Player 1 requested offline only play: player1_id: {0}".format(
                        str(result2['_id'])))
    else:
        if result:
            app_logger.error(
                "Requested pairing player2 doesnt exist: {0}".format(
                    str(id_player2)))
        if result2:
            app_logger.error(
                "Requested pairing player1 doesnt exist: {0}".format(
                    str(id_player1)))
    client.close()

    return game_id

def single_player(player_id, app_logger):
    """Starts a new game with the AI player.
    :param player_id: ID of player
    :param app_logger: Flask app logger
    """

    game_id = None
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    games = database.games
    players = database.players

    new_game = dict(Game(player_id, "AI"))
    new_game['matrix'] = Binary(pickle.dumps(new_game['matrix'], protocol=2))
    new_game['possible_moves'] = numpy.array(
        new_game['possible_moves']).tolist()

    result = players.find_one({'_id': player_id})
    if result:
        if result['game_id'] is None and not result['online_mode']:
            games.insert_one(new_game)
            game_id = new_game['_id']
            players.update_one({'_id':player_id}, {'$set':{'game_id':game_id}})
            game_id = str(game_id)
        else:
            if result['online_mode']:
                app_logger.error(
                    "Single player requested online play: {0}".format(
                        str(player_id)
                    )
                )
            if result['game_id'] != None:
                app_logger.error(
                    "Single player already in a game. game_id: {0} player_id: {1}".format(
                        str(result['game_id']),
                        str(player_id)
                    )
                )
    else:
        app_logger.error(
            "Requested single player doesnt exist: {0}".format(
            str(player_id)))
    client.close()
    return game_id

def play(ip_address, web_browser, coor_x, coor_y, app_logger):
    """Update the information of the game of the player.
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    :param coor_x: X Coordinate of piece
    :param coor_y: Y Coordinate of piece
    :param app_logger: Flask app logger
    """
    player = find_player_by_ip(ip_address, web_browser)
    if player:
        client = MongoClient(CONNECTION_STRING)
        database = client.othello
        games = database.games
        game = games.find_one({'_id': player['game_id']})
        if game:
            game_id = game['_id']
            game['matrix'] = pickle.loads(game['matrix'])
            game = Game(
                game['white'], game['black'],
                game['matrix'], game['turn'])

            result = game.play(Piece(coor_x, coor_y, player['_id']))

            copy_save = dict(game)
            copy_save['matrix'] = Binary(
                pickle.dumps(copy_save['matrix'], protocol=2))
            copy_save['possible_moves'] = numpy.array(
                copy_save['possible_moves']).tolist()
            games.update_one({'_id': game_id}, {'$set': copy_save})
            game.matrix = game.matrix.tolist()
            result['matrix'] = game.matrix
            client.close()
            return result
        client.close()
        app_logger.error(
            "/play: Game not found. game_id: {0} player_id: {1}".format(
                player['game_id'], player['_id']))
        return {'success': False, 'code': 500}
    app_logger.error(
        "/play: Player not found. ip_address: {0} \nweb_browser: {1}".format(
            ip_address, web_browser))
    return {'success': False, 'code': 500}

def exit_app(ip_address, web_browser, app_logger):
    """The player manually exit the game.
    Delete the game and updates its information.
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    :param app_logger: Flask app logger
    """
    player = find_player_by_ip(ip_address, web_browser)
    if player:
        client = MongoClient(CONNECTION_STRING)
        database = client.othello
        games = database.games
        players = database.players
        games.delete_one({'_id': player['game_id']})
        app_logger.info("Player {0} exiting of game {1}".format(
            player['_id'], player['game_id']))
        players.update_one({'_id': player['_id']}, {'$set': {'game_id': None}})
        client.close()

    else:
        app_logger.error(
            "/exit Player not found ip_address: {0} web_browser: {1}".format(
                ip_address, web_browser))

#--------------------------------------#
#                QUERIES               #
#--------------------------------------#

def find_game_by_id(game_id, ip_address, web_browser):
    """Query a game by its game_id.
    Player ip and web are mandatory due to security.
    :param game_id: ID of game
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    games = database.games
    players = database.players

    result_game = games.find_one({'_id': game_id})
    result_player = players.find_one(
        {'ip': ip_address, 'web_browser': web_browser})

    if result_game and result_player:
        player_id = result_player['_id']
        if player_id in result_game['players']:
            result_game['matrix'] = pickle.loads(result_game['matrix'])
            result_game['possible_moves'] = numpy.array(
                result_game['possible_moves']).tolist()
            result_game['matrix'] = result_game['matrix'].tolist()
            result_game['id'] = str(result_game['_id'])
            del result_game['_id']
            result_game['players'] = [str(player) if player != 'AI' else 'AI' for player in result_game['players']]
            result_game['turn'] = str(result_game['turn']) if result_game['turn'] != 'AI' else 'AI'
            result_game['white'] = str(result_game['white']) if result_game['white'] != 'AI' else 'AI'
            result_game['black'] = str(result_game['black']) if result_game['black'] != 'AI' else 'AI'
            client.close()
            return result_game
        client.close()
        return None
    client.close()
    return None

def find_game_by_player_ip(ip_address, web_browser):
    """Find a game by its player ip and web browser.
    """
    game = None
    player = find_player_by_ip(ip_address, web_browser)
    if player:
        client = MongoClient(CONNECTION_STRING)
        database = client.othello
        games = database.games
        game = games.find_one({'players': player['_id']})
        client.close()
    return game

def find_player_by_id(player_id):
    """Find a player by its player_id.
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    result = players.find_one({'_id': player_id})
    client.close()
    return result

def find_player_by_ip(ip_address, web_browser):
    """Find a player by its ip and web browser.
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    result = players.find_one({'ip': ip_address, 'web_browser': web_browser})
    client.close()
    return result

def available_opponents(ip_address, web_browser):
    """Find available players with no current game_id,
    that are not equals to actual player.
    :param ip_address: IP Adress of actual player
    :param web_browser: User-Agent Header of player request
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    search_dict = {
        '$or': [{
            'ip': {
                '$ne': ip_address
            }
        }, {
            'web_browser': {
                '$ne': web_browser
            }
        }],
        'game_id': None,
        'online_mode': True
    }
    result = list(players.find(search_dict))
    client.close()
    return result
