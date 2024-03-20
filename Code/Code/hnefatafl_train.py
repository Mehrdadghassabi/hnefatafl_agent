"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Jon Dumm
Date: 4/4/2019

"""

import sys
import pygame
from pygame.locals import *
import random
import numpy as np
import hnefatafl as tafl
import tools as tool
import value_net as vn
import torch
import time
import copy


def Simple_heuristic(game_state, defender):
    red_capture = 24 - np.count_nonzero(game_state == 1)
    white_capture = 13 - np.count_nonzero(game_state == -1)
    index = np.argwhere(game_state == -2)
    x = index[0][0]
    y = index[0][1]
    distance_to_burg = min(x + y, 20 - x - y, x + 10 - y, y + 10 - x)
    if defender:
        return (red_capture - white_capture) + 0.1 * distance_to_burg
    else:
        return -((red_capture - white_capture) + 0.1 * distance_to_burg)


def Hingston_Simple_Agent(move, defender):
    game_state = game_state_to_array()  # Preserves the current game state

    if move.a_turn:
        pieces = tafl.Attackers
    else:
        pieces = tafl.Defenders

    best_score = -99999999999999.0
    best_piece = None
    best_move = None
    best_game_state = None
    # len("N Pieces: ",len(pieces))
    for piece in pieces:
        move.select(piece)  # Move class defines all possible valid moves
        tafl.Current.add(piece)
        if len(move.vm) == 0:  # No valid moves for this piece, move on
            move.select(piece)
            tafl.Current.empty()
            continue
        else:
            for m in move.vm:
                # Swap game state for candidate move
                temp = game_state[piece.x_tile][piece.y_tile]
                game_state[piece.x_tile][piece.y_tile] = 0
                game_state[m[0]][m[1]] = temp
                score = Simple_heuristic(game_state, defender)
                # print(game_state)
                # print(Simple_heuristic(game_state))
                # model.predict(game_state.reshape(1, 11 * 11))[0][0]

                if score > best_score:
                    best_score = score
                    best_piece = piece
                    best_move = m

                # Reverse swap to restore game state
                temp = game_state[m[0]][m[1]]
                game_state[piece.x_tile][piece.y_tile] = temp
                game_state[m[0]][m[1]] = 0
        move.select(piece)  # Deselect
        tafl.Current.empty()

    move.select(best_piece)
    tafl.Current.add(best_piece)
    # print("Moving piece to: {}".format(pos))
    if move.is_valid_move(best_move, tafl.Current.sprites()[0], True):
        if tafl.Current.sprites()[0] in tafl.Kings:
            move.king_escaped(tafl.Kings)
        if move.a_turn:
            move.remove_pieces(tafl.Defenders, tafl.Attackers, tafl.Kings)
        else:
            move.remove_pieces(tafl.Attackers, tafl.Defenders, tafl.Kings)
        move.end_turn(tafl.Current.sprites()[0])
        tafl.Current.empty()
        # return best_score,game_state_to_array()
        # Just do this by hand for efficiency
        temp = game_state[best_piece.x_tile][best_piece.y_tile]
        game_state[best_piece.x_tile][best_piece.y_tile] = 0
        game_state[best_move[0]][best_move[1]] = temp

        # print(game_state,best_score)
        return game_state, best_score
    else:
        print("ERROR: Efficient move logic failed... Fix!")
        sys.exit(1)


def run_game_random(screen=None):
    """Start a new game with random (legal) moves.

    TODO: Add description

    """
    board = tafl.Board()
    move = tafl.Move()
    tool.initialize_pieces(board)
    num_moves = 0
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pass

        '''
        if move.a_turn:
            text = "Attacker's Turn: Move {}".format(num_moves)
            print(text)
        if not move.a_turn:
            text = "Defender's Turn: Move {}".format(num_moves)
            print(text)
        '''
        # print(move.to_array())
        do_random_move(move)
        num_moves += 1
        if num_moves >= 1000:
            print("Draw game after {} moves".format(num_moves))
            return False

        """Text to display on bottom of game."""
        text2 = None
        if move.escaped:
            text = "King escaped! Defenders win!"
            print(text)
            text2 = "Play again? y/n"
            return False
        if move.king_killed:
            text = "King killed! Attackers win!"
            print(text)
            text2 = "Play again? y/n"
            return False
        if move.restart:
            text = "Restart game? y/n"
            print(text)
            return False
        if screen is not None:
            tool.update_image(screen, board, "tafl")
            pygame.display.update()
        # time.sleep(1)


def do_random_move(move):
    if move.a_turn:
        pieces = tafl.Attackers
    else:
        pieces = tafl.Defenders
    while 1:
        # rn = int(random.random() * len(pieces.sprites()))
        # piece = pieces.sprites()[rn]
        piece = random.choice(pieces.sprites())
        move.select(piece)
        tafl.Current.add(piece)
        # print("Piece at: {} {}".format(piece.x_tile,piece.y_tile))
        # print("  Valid Moves: {}".format(move.vm))
        if len(move.vm) == 0:
            # print("No valid moves...")
            move.select(piece)
            tafl.Current.empty()
            continue
        else:
            pos = random.choice(tuple(move.vm))
            # print("Moving piece to: {}".format(pos))
            if move.is_valid_move(pos, tafl.Current.sprites()[0], True):
                if tafl.Current.sprites()[0] in tafl.Kings:
                    move.king_escaped(tafl.Kings)
                if move.a_turn:
                    move.remove_pieces(tafl.Defenders, tafl.Attackers, tafl.Kings)
                else:
                    move.remove_pieces(tafl.Attackers, tafl.Defenders, tafl.Kings)
                move.end_turn(tafl.Current.sprites()[0])
                tafl.Current.empty()
            break


def run_game_cacd_RL(screen, attacker_model):
    """Start and run one game of computer vs computer hnefatafl.

    TODO: Add description

    """
    board = tafl.Board()
    fake_board = copy.deepcopy(board)
    move = tafl.Move()
    tool.initialize_pieces(board)
    num_moves = 0
    while 1:
        if screen is not None:
            tool.update_image(screen, board, "")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pass

        num_moves += 1
        if num_moves >= 1000:
            return 0

        if move.a_turn:
            # print("Attacker's Turn: Move {}".format(num_moves))
            game_state_previous = game_state_to_array_board(fake_board)
            do_best_move(move, attacker_model, fake_board)
            tool.update_grid(fake_board)
            game_state_current = game_state_to_array_board(fake_board)
            update_value_function(game_state_previous, game_state_current, attacker_model)
            time.sleep(10)

        else:
            # print("Defender's Turn: Move {}".format(num_moves))
            game_state_previous = game_state_to_array_board(fake_board)
            do_random_move(move)
            tool.update_grid(fake_board)
            game_state_current = game_state_to_array_board(fake_board)
            time.sleep(10)

        """Text to display on bottom of game."""
        if move.escaped:
            return -1
        if move.king_killed:
            return 1


def do_best_move(move, model, board):
    """ Function to try all possible moves and select the best according to the model provided
    """

    game_state = game_state_to_array_board(board)  # Preserves the current game state

    # print(game_state)
    # print("==============================================================================")
    if move.a_turn:
        pieces = tafl.Attackers
    else:
        pieces = tafl.Defenders

    best_score = -99999999999999999999.0
    best_piece = None
    best_move = None
    # len("N Pieces: ",len(pieces))
    for piece in pieces:
        move.select(piece)  # Move class defines all possible valid moves
        tafl.Current.add(piece)
        if len(move.vm) == 0:  # No valid moves for this piece, move on
            move.select(piece)
            tafl.Current.empty()
            continue
        else:
            for m in move.vm:
                # Swap game state for candidate move
                temp = game_state[piece.x_tile][piece.y_tile]
                game_state[piece.x_tile][piece.y_tile] = 0
                game_state[m[0]][m[1]] = temp
                try:  # model.predict crashed once...
                    tens = torch.from_numpy(game_state).reshape([1, 1, 11, 11])
                    score = model(tens).detach().numpy()[0]
                except:
                    print("Erorr")
                    score = -1.0

                if score > best_score:
                    best_score = score
                    best_piece = piece
                    best_move = m

                # Reverse swap to restore game state
                temp = game_state[m[0]][m[1]]
                game_state[piece.x_tile][piece.y_tile] = temp
                game_state[m[0]][m[1]] = 0
        move.select(piece)  # Deselect
        tafl.Current.empty()

    move.select(best_piece)
    tafl.Current.add(best_piece)
    # best_piece_copy = copy.deepcopy(best_piece)
    if move.is_valid_move(best_move, tafl.Current.sprites()[0], True):
        if tafl.Current.sprites()[0] in tafl.Kings:
            move.king_escaped(tafl.Kings)
        if move.a_turn:
            move.remove_pieces(tafl.Defenders, tafl.Attackers, tafl.Kings)
        else:
            move.remove_pieces(tafl.Attackers, tafl.Defenders, tafl.Kings)
        move.end_turn(tafl.Current.sprites()[0])
        tafl.Current.empty()
    else:
        print("ERROR: Efficient move logic failed... Fix!")
        sys.exit(1)


def game_state_to_array():
    """2D Numpy array representation of game state for ML model.
    """
    if tafl.Attackers is None or tafl.Defenders is None or tafl.Kings is None:
        print("Game not properly initialized.  Exiting.")
        sys.exit(1)
    arr = np.zeros((11, 11), dtype=np.float32)

    for p in tafl.Attackers:
        arr[p.x_tile][p.y_tile] = 1.0
    for p in tafl.Defenders:
        arr[p.x_tile][p.y_tile] = -1.0
    for p in tafl.Kings:
        arr[p.x_tile][p.y_tile] = -2.0

    return arr


def game_state_to_array_board(board):
    """2D Numpy array representation of game state for ML model.
    """

    arr = np.zeros((11, 11), dtype=np.float32)

    for x in range(board.dim):
        for y in range(board.dim):
            if board.grid[x][y] == "a":
                arr[x][y] = 1.0
            if board.grid[x][y] == "d":
                arr[x][y] = -1.0
            if board.grid[x][y] == "c":
                arr[x][y] = -2.0

    return arr.transpose()

def update_value_function(game_state_previous,game_state_current,attacker_model):
    tens_previous = torch.from_numpy(game_state_previous).reshape([1, 1, 11, 11])
    V_previous = attacker_model(tens_previous).detach().numpy()[0]
    tens_current = torch.from_numpy(game_state_current).reshape([1, 1, 11, 11])
    V_current = attacker_model(tens_current).detach().numpy()[0]

    white_pieces_number_previous = np.count_nonzero(game_state_previous == -1)
    white_pieces_number_current = np.count_nonzero(game_state_current == -1)
    captured_white_pieces_number = white_pieces_number_previous - white_pieces_number_current

    avoid_the_king_from_escaping = (is_the_king_about_to_escape(game_state_previous) and
                                    not is_the_king_about_to_escape(game_state_current))
    create_a_way_for_king_to_escape = (not is_the_king_about_to_escape(game_state_previous) and
                                       is_the_king_about_to_escape(game_state_current))
    #if avoid_the_king_from_escaping:
        #print("king avoided")
    # print(V_previous)
    # print(V_current)
    # print("========================================================")


def is_the_king_about_to_escape(game_state):
    king_coordinates = np.argwhere(game_state == -2)
    king_x = king_coordinates[0][0]
    king_y = king_coordinates[0][1]
    king_is_about_to_escape = False

    if king_x == 0 or king_x == 10:
        king_is_about_to_escape = True
        for j in range(0, king_y):
            if game_state[king_x][j] != 0:
                king_is_about_to_escape = False
        if king_is_about_to_escape:
            return True
        king_is_about_to_escape = True
        for j in range(king_y + 1, 10):
            if game_state[king_x][j] != 0:
                king_is_about_to_escape = False
        if king_is_about_to_escape:
            return True

    if king_y == 0 or king_y == 10:
        king_is_about_to_escape = True
        for i in range(0, king_x):
            if game_state[i][king_y] != 0:
                king_is_about_to_escape = False
        if king_is_about_to_escape:
            return True
        king_is_about_to_escape = True
        for i in range(king_x + 1, 10):
            if game_state[i][king_y] != 0:
                king_is_about_to_escape = False
        if king_is_about_to_escape:
            return True

    return False


def main():
    """Main function- initializes screen and starts new games."""
    interactive = False
    if interactive:
        pygame.init()
        screen = pygame.display.set_mode(tafl.WINDOW_SIZE)
    else:
        screen = None
    tool.initialize_groups()

    num_train_games = 0
    while num_train_games < 10:
        num_train_games += 1
        attacker_model = vn.HingstonNetwork()
        result = run_game_cacd_RL(screen, attacker_model)
        print(result)
        tool.cleanup()


def main1():
    """Main function- initializes screen and starts new games."""
    interactive = True
    if interactive:
        pygame.init()
        screen = pygame.display.set_mode(tafl.WINDOW_SIZE)
    else:
        screen = None
    tool.initialize_groups()
    attacker_model = vn.HingstonNetwork()
    result = run_game_cacd_RL(screen, attacker_model)
    print(result)
    # print("Game finished in {} moves".format(len(a_corrected_scores) + len(d_corrected_scores)))
    tool.cleanup()


if __name__ == '__main__':
    main1()
