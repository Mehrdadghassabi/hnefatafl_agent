"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Sean Lowen
Date: 7/13/2015
"""

import pygame
from pygame.locals import *
import sys
import hnefatafl
from hnefatafl import *


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
    hnefatafl.Pieces = Pieces
    Attackers = pygame.sprite.Group()
    hnefatafl.Attackers = Attackers
    Defenders = pygame.sprite.Group()
    hnefatafl.Defenders = Defenders
    Kings = pygame.sprite.Group()
    hnefatafl.Kings = Kings
    Current = pygame.sprite.Group()
    hnefatafl.Current = Current

    Piece.groups = Pieces
    Defender.groups = Pieces, Defenders
    Attacker.groups = Pieces, Attackers
    King.groups = Pieces, Defenders, Kings


def initialize_pieces(board):
    """Create all of the game pieces and put them in groups.

    Note:
        The board layout from Board class is used for initial placement of
        pieces.

    Args:
        board (Board): the game board object
    """
    for y in range(board.dim):
        for x in range(board.dim):
            p = board.grid[y][x]
            if p == "a":
                Attacker(x, y)
            elif p == "d":
                Defender(x, y)
            elif p == "c":
                King(x, y)


def update_image(screen, board, move, text, text2):
    """Update the image that the users see.

    Note:
        Right now, it redraws the whole board every time it goes through this
        function. In the future, it should only update the necessary tiles.

    Args:
        screen (pygame.Surface): game window that the user interacts with
        board (Board): the board that the pieces are on
        move (Move): the move state data
    """
    screen.fill(MARGIN_COLOR)
    for y in range(board.dim):
        for x in range(board.dim):
            xywh = [x * (GSIZE + MARGIN) + MARGIN,
                    y * (GSIZE + MARGIN) + MARGIN,
                    GSIZE,
                    GSIZE]
            pygame.draw.rect(screen, board.colors[board.grid[x][y]], xywh)

    for piece in Pieces:
        piece.draw(screen)

    """Write which player's turn it is on the bottom of the window."""
    font = pygame.font.Font(None, 36)
    msg = font.render(text, 1, (0, 0, 0))
    msgpos = msg.get_rect()
    if text2:
        msg2 = font.render(text2, 1, (0, 0, 0))
        msgpos2 = msg2.get_rect()
        msgpos.centerx = screen.get_rect().centerx
        msgpos.centery = ((HEIGHT - WIDTH) / 7) + WIDTH
        msgpos2.centerx = screen.get_rect().centerx
        msgpos2.centery = (5 * (HEIGHT - WIDTH) / 7) + WIDTH
        screen.blit(msg, msgpos)
        screen.blit(msg2, msgpos2)
    else:
        msgpos.centerx = screen.get_rect().centerx
        msgpos.centery = ((HEIGHT - WIDTH) / 2) + WIDTH
        screen.blit(msg, msgpos)

    pygame.display.flip()


def run_game(screen):
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
    board = Board()
    move = Move()
    initialize_pieces(board)
    while 1:
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
                    if move.a_turn:
                        for piece in Attackers:
                            if piece.rect.collidepoint(pos):
                                move.select(piece)
                                Current.add(piece)
                    else:
                        for piece in Defenders:
                            if piece.rect.collidepoint(pos):
                                move.select(piece)
                                Current.add(piece)
                else:
                    if Current.sprites()[0].rect.collidepoint(pos):
                        move.select(Current.sprites()[0])
                        Current.empty()
                    elif move.is_valid_move(pos, Current.sprites()[0]):
                        if Current.sprites()[0] in Kings:
                            move.king_escaped(Kings)
                        if move.a_turn:
                            move.remove_pieces(Defenders, Attackers, Kings)
                        else:
                            move.remove_pieces(Attackers, Defenders, Kings)
                        move.end_turn(Current.sprites()[0])
                        Current.empty()

        """Text to display on bottom of game."""
        text2 = None
        text = "Turn"
        if move.a_turn:
            text = "Attacker's Turn"
        if not move.a_turn:
            text = "Defender's Turn"
        if move.escaped:
            text = "King escaped! Defenders win!"
            text2 = "Play again? y/n"
        if move.king_killed:
            text = "King killed! Attackers win!"
            text2 = "Play again? y/n"
        if move.restart:
            text = "Restart game? y/n"
        update_image(screen, board, move, text, text2)


def cleanup():
    """Empty out all groups of sprites.

    Note:
        Although this works for now, I don't think that it properly deletes
        all of the sprites. Must fix this.
    """
    Current.empty()
    Kings.empty()
    Defenders.empty()
    Attackers.empty()
    Pieces.empty()


def main():
    """Main function- initializes screen and starts new games."""
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    initialize_groups()
    run_game(screen)
    cleanup()


if __name__ == '__main__':
    main()
