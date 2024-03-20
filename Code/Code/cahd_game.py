"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Sean Lowen,Jon Dumm

Edited by Mehrdadghassabi
Date: 3/15/2024
"""

import pygame
from pygame.locals import *
import sys
import tools as tool
import hnefatafl as tafl
import random


def run_cahd_game(screen):
    """Start and run a new game of hnefatafl.

    The game, groups, board, move info, screen, and pieces are initialized
    first. Then, the game starts. It runs in a while loop, which will exit
    if the user closes out of the game. Another event that it listens
    for is a MOUSEBUTTONDOWN event; the game takes action when the user clicks
    on the board. If a piece has not been selected yet and the user clicks on
    one of his pieces, then the piece will be selected and change colors. The
    user can click on this piece again to deselect it, or they can click
    on a square that is a valid move for that piece. If it is a valid move,
    the piece will move there and it is the next person's turn. The game
    also listens for KEYDOWN event. If the game has ended or the player wants
    to restart the game, it will listen for 'y' or 'n'. If the player wants
    to restart the game, they can press 'r', which will require confirmation
    before actually restarting.

    Args:
        screen (pygame.Surface): The game window

    Returns:
        True if players want a new game, False o.w.
    """
    board = tafl.Board()
    move = tafl.Move()
    tool.initialize_pieces(board)
    while 1:
        if move.a_turn and not move.game_over:
            tool.do_random_move(move)
        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if move.game_over and event.key == pygame.K_n:
                        return False
                    if move.game_over and event.key == pygame.K_y:
                        return True
                    if move.restart and event.key == pygame.K_n:
                        move.restart = False
                    if move.restart and event.key == pygame.K_y:
                        return True
                    if event.key == pygame.K_r:
                        move.restart = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if move.game_over:
                        pass
                    elif move.restart:
                        pass
                    elif not move.selected:
                        for piece in tafl.Defenders:
                            if piece.rect.collidepoint(pos):
                                move.select(piece)
                                tafl.Current.add(piece)
                    else:
                        if tafl.Current.sprites()[0].rect.collidepoint(pos):
                            move.select(tafl.Current.sprites()[0])
                            tafl.Current.empty()
                        elif move.is_valid_move(pos, tafl.Current.sprites()[0]):
                            if tafl.Current.sprites()[0] in tafl.Kings:
                                move.king_escaped(tafl.Kings)
                            move.remove_pieces(tafl.Attackers, tafl.Defenders, tafl.Kings)
                            move.end_turn(tafl.Current.sprites()[0])
                            tafl.Current.empty()

        """Text to display on bottom of game."""
        text = "Turn"
        if move.a_turn:
            text = "Attacker's Turn"
        if not move.a_turn:
            text = "Defender's Turn"
        if move.escaped:
            text = "King escaped! Defenders win!"
        if move.king_killed:
            text = "King killed! Attackers win!"
        if move.restart:
            text = "Restart game? y/n"
        tool.update_image(screen, board, text)


def main():
    """Main function- initializes screen and starts new games."""
    pygame.init()
    screen = pygame.display.set_mode(tafl.WINDOW_SIZE)
    tool.initialize_groups()
    run_cahd_game(screen)
    tool.cleanup()


if __name__ == '__main__':
    main()
