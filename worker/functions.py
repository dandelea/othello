
from pymongo import MongoClient
DISCONNECTION_TIME = 30
from bson.binary import Binary
from models import Game

import datetime, numpy, pickle, pytz
try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus

from config import MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOSTNAME, MONGO_PORT

CONNECTION_STRING = 'mongodb://{0}:{1}@{2}:{3}'.format(
    MONGO_USERNAME,
    MONGO_PASSWORD,
    MONGO_HOSTNAME,
    MONGO_PORT
)

def init_database():
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    print(database.command('ping'))
    client.drop_database('othello')
    client.close()

def purge_disconnected():
    """Removes all the players in the database that didnt send
    the beacon /still_alive in X seconds (DISCONNECTION_TIME).
    Then set its game to gameover, meaning the other player wins.
    """
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    games = database.games
    for player in players.find():
        now = datetime.datetime.now(pytz.utc)
        diff = now - player['date']
        if diff.seconds > DISCONNECTION_TIME:
            if player['game_id']:
                game = games.find_one({'_id': player['game_id']})
                if game:
                    game['scoreboard'][str(player['_id'])] = 0
                    game['gameover'] = True
                    games.update_one(
                        {'_id': game['_id']},
                        {'$set' : {
                            'gameover': game['gameover'],
                            'scoreboard': game['scoreboard']
                        }})
                    print(
                        "Modificando el juego {0} {1} a gameover manualmente".format(
                            str(game['_id']), str(game['players'])))
                    players.delete_one({'_id': player['_id']})
                    print(
                        "Purgando el jugador {0} por inactividad".format(str(player['_id'])))
    client.close()

def purge_gameover():
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    players = database.players
    games = database.games
    for game in games.find({'gameover': True}):
        players.update(
            {'game_id': game['_id']},
            {'$set' : {
                'game_id': None
            }})
        games.delete_one({'_id': game['_id']})
        print(
            "Purgando el juego finalizado {0} {1}".format(str(game['_id']), str(game['players'])))
    client.close()

def ai_plays():
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

        print('AI juega al juego {0}'.format(str(game_id)))
        game.play_ai()

        copy_save = dict(game)
        copy_save['matrix'] = Binary(
            pickle.dumps(copy_save['matrix'], protocol=2))
        copy_save['possible_moves'] = numpy.array(
            copy_save['possible_moves']).tolist()
        other = [player for player in game['players'] if player != 'AI'][0]
        copy_save['turn'] = other
        games.update_one({'_id': game_id}, {'$set': copy_save})
    client.close()

def ping():
    client = MongoClient(CONNECTION_STRING)
    database = client.othello
    database.ping.insert_one({
        "ping": database.command('ping'),
        "date": datetime.datetime.now(pytz.utc)
    })
    client.close()
