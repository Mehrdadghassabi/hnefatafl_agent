"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Sean Lowen
Date: 7/13/2015

Edited by Mehrdadghassabi
Date: 3/15/2024
"""

import pygame
import hnefatafl as tafl
import random


def initialize_groups():
    """Create global groups for different pieces.

    Notes:
        The groups are defined as follows:
            Pieces: all pieces
            Attackers: all attacking pieces
            Defenders: all defending pieces, including king
            Kings: the king piece
            Current: the current selected piece
    """
    global Pieces
    global Attackers
    global Defenders
    global Kings
    global Current

    Pieces = pygame.sprite.Group()
    tafl.Pieces = Pieces
    Attackers = pygame.sprite.Group()
    tafl.Attackers = Attackers
    Defenders = pygame.sprite.Group()
    tafl.Defenders = Defenders
    Kings = pygame.sprite.Group()
    tafl.Kings = Kings
    Current = pygame.sprite.Group()
    tafl.Current = Current

    tafl.Piece.groups = Pieces
    tafl.Defender.groups = Pieces, Defenders
    tafl.Attacker.groups = Pieces, Attackers
    tafl.King.groups = Pieces, Defenders, Kings


def initialize_pieces(board):
    """Create all of the game pieces and put them in groups.

    Note:
        The board layout from Board class is used for initial placement of
        pieces.

    Args:
        board (Board): the game board object
    """
    for x in range(board.dim):
        for y in range(board.dim):
            p = board.grid[x][y]
            if p == "a":
                tafl.Attacker(x, y)
            elif p == "d":
                tafl.Defender(x, y)
            elif p == "c":
                tafl.King(x, y)


def update_image(screen, board, text):
    """Update the image that the users see.

    Note:
        Right now, it redraws the whole board every time it goes through this
        function. In the future, it should only update the necessary tiles.

    Args:
        :param screen: the game window that the user interacts with
        :param board: the board that the pieces are on
        :param text: the text that is shown below the board
    """
    screen.fill(tafl.MARGIN_COLOR)
    for y in range(board.dim):
        for x in range(board.dim):
            xywh = [x * (tafl.GSIZE + tafl.MARGIN) + tafl.MARGIN,
                    y * (tafl.GSIZE + tafl.MARGIN) + tafl.MARGIN,
                    tafl.GSIZE,
                    tafl.GSIZE]
            pygame.draw.rect(screen, board.colors[board.grid[x][y]], xywh)

    for piece in Pieces:
        piece.draw(screen)

    """Write which player's turn it is on the bottom of the window."""
    font = pygame.font.Font(None, 36)
    msg = font.render(text, 1, (0, 0, 0))
    msgpos = msg.get_rect()
    msgpos.centerx = screen.get_rect().centerx
    msgpos.centery = ((tafl.HEIGHT - tafl.WIDTH) / 2) + tafl.WIDTH
    screen.blit(msg, msgpos)

    pygame.display.flip()


def update_grid(board):
    """Create all of the game pieces and put them in groups.

    Note:
        The board layout from Board class is used for initial placement of
        pieces.

    Args:
        board (Board): the game board object
    """
    for x in range(board.dim):
        for y in range(board.dim):
            l = list(board.grid[x])
            if (x == 0 and y == 0) or (x == 10 and y == 0) or (x == 10 and y == 0) or (x == 10 and y == 0):
                l[y] = "x"
            else:
                l[y] = "."
            board.grid[x] = ''.join(l)

    for p in tafl.Attackers:
        l = list(board.grid[p.x_tile])
        l[p.y_tile] = "a"
        board.grid[p.x_tile] = ''.join(l)
    for p in tafl.Defenders:
        l = list(board.grid[p.x_tile])
        l[p.y_tile] = "d"
        board.grid[p.x_tile] = ''.join(l)
    for p in tafl.Kings:
        l = list(board.grid[p.x_tile])
        l[p.y_tile] = "c"
        board.grid[p.x_tile] = ''.join(l)


def do_random_move(move):
    if move.a_turn:
        pieces = tafl.Attackers
    else:
        pieces = tafl.Defenders
    while 1:
        piece = random.choice(pieces.sprites())
        move.select(piece)
        tafl.Current.add(piece)
        if len(move.vm) == 0:
            # print("No valid moves...")
            move.select(piece)
            tafl.Current.empty()
            continue
        else:
            pos = random.choice(tuple(move.vm))
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


def cleanup():
    """Empty out all groups of sprites.

    Note:
        Although this works for now, I don't think that it properly deletes
        all of the sprites. Must fix this.
    """
    tafl.Current.empty()
    tafl.Kings.empty()
    tafl.Defenders.empty()
    tafl.Attackers.empty()
    tafl.Pieces.empty()
