import numpy as np
import torch

import chess.pgn


import chess
from gym_chess.alphazero.move_encoding import utils
from pathlib import Path


from typing import Optional

def make_move(user_move):
    print("1- USER MOVE", user_move)
    move = chess.Move.from_uci(user_move)
    print("2- MOVE", move)
    # move  = board.fen()
    board.push(move)
    aiMove = model.predict(board)
    print("3- BOT OUTPUT : ", aiMove, "************")
    board.push(aiMove)
    print("4- ", board)
    return f'{aiMove}'


def _decodeKnight(action: int) -> Optional[chess.Move]:
    _NUM_TYPES: int = 8

    #: Starting point of knight moves in last dimension of 8 x 8 x 73 action array.
    _TYPE_OFFSET: int = 56

    #: Set of possible directions for a knight move, encoded as
    #: (delta rank, delta square).
    _DIRECTIONS = utils.IndexedTuple(
        (+2, +1),
        (+1, +2),
        (-1, +2),
        (-2, +1),
        (-2, -1),
        (-1, -2),
        (+1, -2),
        (+2, -1),
    )

    from_rank, from_file, move_type = np.unravel_index(action, (8, 8, 73))

    is_knight_move = _TYPE_OFFSET <= move_type and move_type < _TYPE_OFFSET + _NUM_TYPES

    if not is_knight_move:
        return None

    knight_move_type = move_type - _TYPE_OFFSET

    delta_rank, delta_file = _DIRECTIONS[knight_move_type]

    to_rank = from_rank + delta_rank
    to_file = from_file + delta_file

    move = utils.pack(from_rank, from_file, to_rank, to_file)
    return move


def _decodeQueen(action: int) -> Optional[chess.Move]:
    _NUM_TYPES: int = 56  # = 8 directions * 7 squares max. distance

    #: Set of possible directions for a queen move, encoded as
    #: (delta rank, delta square).
    _DIRECTIONS = utils.IndexedTuple(
        (+1, 0),
        (+1, +1),
        (0, +1),
        (-1, +1),
        (-1, 0),
        (-1, -1),
        (0, -1),
        (+1, -1),
    )
    from_rank, from_file, move_type = np.unravel_index(action, (8, 8, 73))

    is_queen_move = move_type < _NUM_TYPES

    if not is_queen_move:
        return None

    direction_idx, distance_idx = np.unravel_index(indices=move_type, shape=(8, 7))

    direction = _DIRECTIONS[direction_idx]
    distance = distance_idx + 1

    delta_rank = direction[0] * distance
    delta_file = direction[1] * distance

    to_rank = from_rank + delta_rank
    to_file = from_file + delta_file

    move = utils.pack(from_rank, from_file, to_rank, to_file)
    return move


def _decodeUnderPromotion(action):
    _NUM_TYPES: int = 9  # = 3 directions * 3 piece types (see below)

    #: Starting point of underpromotions in last dimension of 8 x 8 x 73 action
    #: array.
    _TYPE_OFFSET: int = 64

    #: Set of possibel directions for an underpromotion, encoded as file delta.
    _DIRECTIONS = utils.IndexedTuple(
        -1,
        0,
        +1,
    )

    #: Set of possibel piece types for an underpromotion (promoting to a queen
    #: is implicitly encoded by the corresponding queen move).
    _PROMOTIONS = utils.IndexedTuple(
        chess.KNIGHT,
        chess.BISHOP,
        chess.ROOK,
    )

    from_rank, from_file, move_type = np.unravel_index(action, (8, 8, 73))

    is_underpromotion = (
        _TYPE_OFFSET <= move_type and move_type < _TYPE_OFFSET + _NUM_TYPES
    )

    if not is_underpromotion:
        return None

    underpromotion_type = move_type - _TYPE_OFFSET

    direction_idx, promotion_idx = np.unravel_index(
        indices=underpromotion_type, shape=(3, 3)
    )

    direction = _DIRECTIONS[direction_idx]
    promotion = _PROMOTIONS[promotion_idx]

    to_rank = from_rank + 1
    to_file = from_file + direction

    move = utils.pack(from_rank, from_file, to_rank, to_file)
    move.promotion = promotion

    return move


# primary decoding function, the ones above are just helper functions
def decodeMove(action: int, board) -> chess.Move:
    move = _decodeQueen(action)
    is_queen_move = move is not None

    if not move:
        move = _decodeKnight(action)

    if not move:
        move = _decodeUnderPromotion(action)

    if not move:
        raise ValueError(f"{action} is not a valid action")

    # Actions encode moves from the perspective of the current player. If
    # this is the black player, the move must be reoriented.
    turn = board.turn

    if turn == False:  # black to move
        move = utils.rotate(move)

    # Moving a pawn to the opponent's home rank with a queen move
    # is automatically assumed to be queen underpromotion. However,
    # since queenmoves has no reference to the board and can thus not
    # determine whether the moved piece is a pawn, we have to add this
    # information manually here
    if is_queen_move:
        to_rank = chess.square_rank(move.to_square)
        is_promoting_move = (to_rank == 7 and turn == True) or (
            to_rank == 0 and turn == False
        )

        piece = board.piece_at(move.from_square)
        if piece is None:  # NOTE I added this, not entirely sure if it's correct
            return None
        is_pawn = piece.piece_type == chess.PAWN

        if is_pawn and is_promoting_move:
            move.promotion = chess.QUEEN

    return move


def encodeBoard(board: chess.Board) -> np.array:
    """Converts a board to numpy array representation."""

    array = np.zeros((8, 8, 14), dtype=int)

    for square, piece in board.piece_map().items():
        rank, file = chess.square_rank(square), chess.square_file(square)
        piece_type, color = piece.piece_type, piece.color

        # The first six planes encode the pieces of the active player,
        # the following six those of the active player's opponent. Since
        # this class always stores boards oriented towards the white player,
        # White is considered to be the active player here.
        offset = 0 if color == chess.WHITE else 6

        # Chess enumerates piece types beginning with one, which we have
        # to account for
        idx = piece_type - 1

        array[rank, file, idx + offset] = 1

    # Repetition counters
    array[:, :, 12] = board.is_repetition(2)
    array[:, :, 13] = board.is_repetition(3)

    return array

class Model(torch.nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.INPUT_SIZE = 896
        # self.INPUT_SIZE = 7*7*13 #NOTE changing input size for using cnns
        self.OUTPUT_SIZE = 4672  # = number of unique moves (action space)

        # can try to add CNN and pooling here (calculations taking into account spacial features)

        # input shape for sample is (8,8,14), flattened to 1d array of size 896
        # self.cnn1 = nn.Conv3d(4,4,(2,2,4), padding=(0,0,1))

        self.activation = torch.nn.Tanh()
        # self.activation = torch.nn.ReLU()

        self.linear1 = torch.nn.Linear(self.INPUT_SIZE, 1000)
        self.linear2 = torch.nn.Linear(1000, 1000)
        self.linear3 = torch.nn.Linear(1000, 1000)
        self.linear4 = torch.nn.Linear(1000, 200)
        self.linear5 = torch.nn.Linear(200, self.OUTPUT_SIZE)
        self.softmax = torch.nn.Softmax(
            1
        )  # use softmax as prob for each move, dim 1 as dim 0 is the batch dimension

    def forward(self, x):  # x.shape = (batch size, 896)
        x = x.to(torch.float32)
        # x = self.cnn1(x) #for using cnns
        x = x.reshape(x.shape[0], -1)
        x = self.linear1(x)
        x = self.activation(x)
        x = self.linear2(x)
        x = self.activation(x)
        x = self.linear3(x)
        x = self.activation(x)
        x = self.linear4(x)
        x = self.activation(x)
        x = self.linear5(x)
        # x = self.softmax(x) #do not use softmax since you are using cross entropy loss
        return x

    def predict(self, board: chess.Board):
        """takes in a chess board and returns a chess.move object. NOTE: this function should definitely be written better, but it works for now"""
        with torch.no_grad():
            encodedBoard = encodeBoard(board)
            encodedBoard = encodedBoard.reshape(1, -1)
            encodedBoard = torch.from_numpy(encodedBoard)
            res = self.forward(encodedBoard)
            probs = self.softmax(res)

            probs = probs.numpy()[
                0
            ]  # do not want tensor anymore, 0 since it is a 2d array with 1 row

            # verify that move is legal and can be decoded before returning
            while len(probs) > 0:  # try max 100 times, if not throw an error
                moveIdx = probs.argmax()
                try:  # TODO should not have try here, but was a bug with idx 499 if it is black to move
                    uciMove = decodeMove(moveIdx, board)
                    if uciMove is None:  # could not decode
                        probs = np.delete(probs, moveIdx)
                        continue
                    move = chess.Move.from_uci(str(uciMove))
                    if (
                        move in board.legal_moves
                    ):  # if legal, return, else: loop continues after deleting the move
                        return move
                except:
                    pass
                probs = np.delete(
                    probs, moveIdx
                )  # TODO probably better way to do this, but it is not too time critical as it is only for predictions
                # remove the move so its not chosen again next iteration

            # return random move if model failed to find move
            moves = board.legal_moves
            if len(moves) > 0:
                return np.random.choice(list(moves))
            return None  # if no legal moves found, return None
            # raise Exception("Your predict function could not find any legal/decodable moves")
board = chess.Board()
# saved_model = pickle.load(open("saved_mode\model.pkl", "rb"))
model = Model()
model.load_state_dict(torch.load("saved_mode\model_best"))
model.eval()






# moveStr = "h3f4"
# move = chess.Move.from_uci(moveStr)
# board.push(move)
# print(board)

# # make ai move:
# aiMove = model.predict(board)
# print("BOT OUTPUT : ", aiMove, "************")
# board.push(aiMove)
# print(board)

# print(board)
# pgn = "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1"

# first_game = chess.pgn.read_headers(pgn)

# print(first_game)