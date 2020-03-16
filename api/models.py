'''Script that manages the game logic'''

import copy as cp
import numpy as np

N = 8
DIRECTIONS = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1],
    [-1, -1],
    [1, 1],
    [-1, 1],
    [1, -1]
]

def initial_matrix():
    """Initial configuration of the game table"""
    matrix = np.zeros((N, N))
    matrix[3, 3] = 1
    matrix[4, 4] = 1
    matrix[3, 4] = 2
    matrix[4, 3] = 2
    return matrix

class Game:
    """Python class for the game state"""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, player1, player2, matrix=initial_matrix(), turn=None):
        self.white = player1
        self.black = player2
        self.players = [player1, player2]
        self.matrix = matrix
        self.gameover = False
        if turn is None:
            self.turn = self.white
        else:
            self.turn = turn
        self.scoreboard = self.calc_scoreboard()
        self.possible_moves = self.calc_possible_moves(self.turn)

    def get_piece(self, x, y):
        """Returns a Piece object in for column x and row y of self.matrix.
        :param x: column number [0 to N-1]
        :param y: row number [0 to N-1]
        """
        v = self.matrix[x, y]
        if v:
            # Player1 is in players[0]
            # Player2 is in players[1]
            return Piece(x, y, self.players[int(v)-1])
        return None

    def set_piece(self, x, y, player):
        """Modify self.matrix in (x,y) for player.
        :param x: column number [0 to N-1]
        :param y: row number [0 to N-1]
        :param player: Player name or identifier
        """
        self.matrix[x, y] = self.player_code(player)

    def player_code(self, player):
        """Returns a player code (1 or 2) for a player's name or identifier.
        :param player: Player name or identifier
        """
        return self.players.index(player)+1

    def other_player(self, player):
        """Returns the other player name or identifier.
        :param player: Player name or identifier
        """
        return self.players[int(not self.players.index(player))]

    @staticmethod
    def valid_coordinates(piece):
        """Returns bool if piece coordinates are correct.
        """
        return piece.x >= 0 and piece.x < N and piece.y >= 0 and piece.y < N

    def pieces_of(self, player):
        """Returns a list of tuples coordinates, from a player.
        :param player: Player name or identifier
        """
        indices = np.where(self.matrix == self.player_code(player))
        coordinates = list(zip(*indices))
        return coordinates

    def calc_scoreboard(self):
        """Returns a dict.
        Key: Player name or identifier.
        Value: Number of pieces.
        """
        result = {}
        for player in self.players:
            result[str(player)] = len(self.pieces_of(player))
        return result

    def calc_possible_moves(self, player):
        """Returns list of tuples coordinates,
        possible moves that the player can play.
        :param player: Player name or identifier
        """
        moves = []
        for coor in self.pieces_of(player):
            piece = Piece(coor[0], coor[1], player)
            for vector in DIRECTIONS:
                copy = cp.copy(piece)
                while (
                        self.valid_coordinates(copy) and
                        self.get_piece(copy.x, copy.y) != None
                ): # While there are pieces
                    # Proceed in that direction
                    copy.x = copy.x + vector[0]
                    copy.y = copy.y + vector[1]
                    if (
                            self.valid_coordinates(copy) and
                            self.get_piece(copy.x, copy.y) is None and# There is a blank
                            self.get_piece(copy.x - vector[0], copy.y - vector[1]).player != player and# Previous was an enemy piece
                            (copy.x, copy.y) not in moves
                    ): # and not registered move yet
                        moves.append((copy.x, copy.y))
        return sorted(moves)

    def post_play(self, last_piece):
        """Post play: Transformation of pieces.
        :pararm last_piece: Last piece object (x,y,player) played
        """
        pending_transf = []
        for vector in DIRECTIONS:
            del pending_transf[:]
            copy = cp.copy(last_piece)

            while(
                    self.valid_coordinates(copy) and
                    self.get_piece(copy.x, copy.y) != None
            ):

                #Proceed in that direction
                copy.x = copy.x + vector[0]
                copy.y = copy.y + vector[1]

                if (
                        self.valid_coordinates(copy) and
                        self.get_piece(copy.x, copy.y) != None
                ): # There is a piece
                    if self.get_piece(copy.x, copy.y).player != last_piece.player:
                        #Its an enemy piece
                        pending_transf.append(self.get_piece(copy.x, copy.y))
                    else:
                        for piece in pending_transf:
                            self.set_piece(piece.x, piece.y, last_piece.player)
        self.turn = self.other_player(last_piece.player)
        self.possible_moves = self.calc_possible_moves(self.turn)
        self.scoreboard = self.calc_scoreboard()
        self.gameover = not self.possible_moves

    def play(self, piece):
        """Set a piece of a player, post play and check game over.
        :param piece: Piece object (x,y,player)
        """
        p_moves = self.calc_possible_moves(piece.player)
        if piece.get_tuple() in p_moves:

            self.set_piece(piece.x, piece.y, piece.player)
            self.post_play(piece)
            if self.gameover: #gameover
                return {
                    'success': True,
                    'code': 200,
                    'gameover': True,
                    'scoreboard': self.scoreboard
                }
            return {
                'success': True,
                'code': 200,
                'gameover': False,
                'scoreboard': self.scoreboard
            }
        return {
            'success': False,
            'code': 400
        }

    def play_ai(self):
        """Plays a move for the AI player, post play and check game over.
        """
        p_moves = self.calc_possible_moves("AI")
        scores = []
        for p_move in p_moves:
            p_move = Piece(p_move[0], p_move[1], "AI")
            copy = cp.deepcopy(self)
            copy.set_piece(p_move.x, p_move.y, p_move.player)
            copy.post_play(p_move)
            scores.append(copy.scoreboard["AI"])

        selected_move = p_moves[scores.index(max(scores))]
        piece = Piece(selected_move[0], selected_move[1], "AI")
        return self.play(piece)


    def __repr__(self):
        """Return a string representation of this object that can
        be evaluated as a Python expression."""
        print_this = repr(self.matrix.astype(int))
        return print_this
    __str__ = __repr__

    def __iter__(self):
        return iter([
            ('white', self.white),
            ('black', self.black),
            ('players', self.players),
            ('matrix', self.matrix),
            ('gameover', self.gameover),
            ('turn', self.turn),
            ('possible_moves', self.possible_moves),
            ('scoreboard', self.scoreboard)
            ])

class Piece:
    """Python class for a game piece."""
    # pylint: disable=too-few-public-methods
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player

    def get_tuple(self):
        """Retuns piece representation as a
        tuple of coordinates.
        """
        return (self.x, self.y)

    def __repr__(self):
        """Return a string representation of this object that can
        be evaluated as a Python expression."""
        print_this = "[{0} = {1}]".format(
            repr(self.get_tuple()), repr(self.player))
        return print_this
    __str__ = __repr__
