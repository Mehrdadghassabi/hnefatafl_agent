"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Jon Dumm
Date: 4/4/2019

Edited by Mehrdadghassabi
Date: 3/15/2024
"""
import pygame
import tools as tool
import hnefatafl as tafl
import sys
import random
from pygame.locals import *


def run_cacd_game(screen=None):
    """Start and run one game of computer vs computer hnefatafl.

    TODO: Add description

    """
    board = tafl.Board()
    move = tafl.Move()
    tool.initialize_pieces(board)
    a_game_states = []
    a_predicted_scores = []
    d_game_states = []
    d_predicted_scores = []
    num_moves = 0
    while 1:
        if screen is not None:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pass

        num_moves += 1
        if num_moves >= 1000:
            print("Draw game after {} moves".format(num_moves))
            a_predicted_scores.append(0.0)
            d_predicted_scores.append(0.0)
            return a_game_states, a_predicted_scores[1:], d_game_states, d_predicted_scores[
                                                                         1:]  # i.e. the corrected scores from RL

        if move.a_turn:
            game_state = tool.do_random_move(move)
            predicted_score = (random.random() - 0.5) * 2
            a_game_states.append(game_state)
            a_predicted_scores.append(predicted_score)
        else:
            game_state = tool.do_random_move(move)
            predicted_score = (random.random() - 0.5) * 2
            d_game_states.append(game_state)
            d_predicted_scores.append(predicted_score)

        """Text to display on bottom of game."""
        if move.escaped:
            print("King escaped! Defenders win!")
            a_predicted_scores.append(-1.0)
            d_predicted_scores.append(+1.0)
            return a_game_states, a_predicted_scores[1:], d_game_states, d_predicted_scores[
                                                                         1:]  # i.e. the corrected scores from RL
        if move.king_killed:
            print("King killed! Attackers win!")
            # print(a_predicted_scores[-1])
            a_predicted_scores.append(+1.0)
            d_predicted_scores.append(-1.0)
            return a_game_states, a_predicted_scores[1:], d_game_states, d_predicted_scores[
                                                                         1:]  # i.e. the corrected scores from RL
        if screen is not None:
            tool.update_image(screen, board, "")
            pygame.display.update()


def main():
    """Main function- initializes screen and starts new games."""
    interactive = True
    if interactive:
        pygame.init()
        screen = pygame.display.set_mode(tafl.WINDOW_SIZE)
    else:
        screen = None
    tool.initialize_groups()
    a_game_states, a_corrected_scores, d_game_states, d_corrected_scores = run_cacd_game(screen)
    print("Game finished in {} moves".format(len(a_corrected_scores) + len(d_corrected_scores)))
    tool.cleanup()


if __name__ == '__main__':
    main()
