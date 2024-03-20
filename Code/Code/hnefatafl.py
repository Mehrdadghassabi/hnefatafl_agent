"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Sean Lowen
Date: 7/13/2015
"""

import pygame

WINDOW_SIZE = WIDTH, HEIGHT = 640, 700
MARGIN_COLOR = 128, 102, 69
GSIZE = WIDTH // 12
MARGIN = GSIZE // 12
SPECIALSQS = set([(5, 5), (0, 0), (0, 10), (10, 10), (10, 0)])
global Pieces
global Attackers
global Defenders
global Kings
global Current



class Move(object):
    """The Move class contains all information about the current move state."""

    def __init__(self):
        """Initialized the Move object.

        a_turn: Bool which is true when its the Attacker's turn, false o.w.
        selected: Bool which is true if a piece has been selected to move.
        king_killed: Bool which is true if the king has been killed.
        escaped: Bool which is true if the king escaped
        game_over: Bool which is true if either player has won or its a draw
        restart: Bool which pauses game and asks if players want to restart
        """
        self.a_turn = True
        self.selected = False
        self.king_killed = False
        self.escaped = False
        self.game_over = False
        self.restart = False

    def select(self, piece):
        """Allow players to select one of their pieces to move.

        When a player clicks on a piece, this function first checks if they
        have chosen a piece to move already. If they have not, the function
        determines if the piece is theirs or not, and if it is, its location
        is stored in the Move object, its color is changed so the player can
        see what they selected, and the valid moves for that piece are
        calculated.

        Args:
            piece (Piece): the playing piece that the player selected.
        """
        if not self.selected:
            self.selected = True
            piece.color = (247, 5, 215)
            self.row = piece.x_tile
            self.col = piece.y_tile
            self.vm = self.valid_moves(piece.special_sqs)
        else:
            self.selected = False
            piece.color = piece.base_color

    def valid_moves(self, special_sqs):
        """Determine the valid moves for the selected piece.

        Currently there are four very similar functions to determine all valid
        moves to the left, the right, above, and below. These functions need to
        be refactored.

        Args:
            special_sqs (bool): True if piece can move on special squares

        Returns:
            vm (set(int,int)): Set of valid moves.
        """
        vm = set()
        vm.update(self.left_bound())
        vm.update(self.right_bound())
        vm.update(self.up_bound())
        vm.update(self.down_bound())
        if not special_sqs:
            vm.difference_update(SPECIALSQS)
        return vm

    def is_valid_move(self, pos, piece, tile_coords=False):
        """Determine if the selected move is valid or not.

        The function finds the tile on the board where the player wants to move
        their piece and returns True if the tile is in the set of valid moves
        for the selected piece.

        Args:
            pos (int, int): x and y coordinates in pixels
            piece (Piece): the selected piece

        Returns:
            bool: True if valid move, false o.w.
        """
        if tile_coords:
            row = pos[0]
            col = pos[1]
        else:
            row = pos[0] // (WIDTH // 11)
            col = pos[1] // (WIDTH // 11)

        if (row, col) in self.vm:
            piece.pos_cent(row, col)
            self.row = row
            self.col = col
            return True
        else:
            return False

    def king_escaped(self, Kings):
        """Check if king has moved onto a corner square."""
        king = (Kings.sprites()[0].x_tile, Kings.sprites()[0].y_tile)
        if king in SPECIALSQS.difference([(5, 5)]):
            self.escaped = True
            self.game_over = True

    def remove_pieces(self, g1, g2, Kings):
        """Determine if any pieces need to be removed from the board.

        check_pts is a list of four tuples. Each tuple is a tuple of tile
        coordinates, the first of which is directly next to the square
        where the piece moved, and the second of which is two squares away
        in the same direction. First, the function checks to see if there is
        an opponent's piece adjacent to where the player just moved his
        piece. If there is one, then it checks if the other side of the
        opponenet's piece is either occupied by the player's piece or if it
        is an unoccupied hostile territory (SPECIALSQS). If either of those
        is true, then the piece is captured, and removed from the board.

        Args:
            g1 (Group(sprites)): the opponent's pieces
            g2 (Group(sprites)): the current player's pieces
            Kings (Group(sprites)): the group containing the king
        """
        check_pts = set([((self.row, self.col + 1), (self.row, self.col + 2)),
                         ((self.row + 1, self.col), (self.row + 2, self.col)),
                         ((self.row, self.col - 1), (self.row, self.col - 2)),
                         ((self.row - 1, self.col), (self.row - 2, self.col))])
        captured = []
        king = (Kings.sprites()[0].x_tile, Kings.sprites()[0].y_tile)
        for square in check_pts:
            if square[0] == king:
                if Kings.sprites()[0] in g1:
                    if self.kill_king(king[0], king[1], g2):
                        self.king_killed = True
                        self.game_over = True
                        captured.append(Kings.sprites()[0])
            else:
                for p1 in g1:
                    if (p1.x_tile, p1.y_tile) == square[0]:
                        for p2 in g2:
                            if (p2.x_tile, p2.y_tile) == (square[1]):
                                captured.append(p1)
                            elif square[1] in SPECIALSQS:
                                if square[1] != king:
                                    captured.append(p1)
        for a in captured:
            a.kill()

    def kill_king(self, x, y, attackers):
        """Determine if the king has been killed.

        The king is killed if it is surrounded on all four sides by attacking
        pieces or hostile territories.

        Args:
            x (int): x tile coordinate of the king
            y (int): y tile coordinate of the king

        Returns:
            True if king has been killed, False o.w.
        """
        kill_pts = set([(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)])
        kill_pts.difference_update(SPECIALSQS)
        attack_pts = set()
        for pt in kill_pts:
            for a in attackers:
                try:
                    attack_pts.add((a.x_tile, a.y_tile))
                except KeyError:
                    pass
        kill_pts.difference_update(attack_pts)
        if not kill_pts:
            return True

    def left_bound(self):
        """Find the all valid moves to the left of the selected piece.

        Iterates through all spaces to the left until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves to the left.
        """
        vm = set()
        temp_row = self.row - 1
        while True:
            if temp_row < 0:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(temp_row, self.col)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((temp_row, self.col))
            temp_row -= 1

    def right_bound(self):
        """Find the all valid moves to the right of the selected piece.

        Iterates through all spaces to the right until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves to the right.
        """
        vm = set()
        temp_row = self.row + 1
        clear = True
        while clear:
            if temp_row > 10:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(temp_row, self.col)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((temp_row, self.col))
            temp_row += 1

    def up_bound(self):
        """Find the all valid moves above the selected piece.

        Iterates through all spaces above until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves above.
        """
        vm = set()
        temp_col = self.col - 1
        clear = True
        while clear:
            if temp_col < 0:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(self.row, temp_col)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((self.row, temp_col))
            temp_col -= 1

    def down_bound(self):
        """Find the all valid moves below the selected piece.

        Iterates through all spaces below until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves below.
        """
        vm = set()
        temp_col = self.col + 1
        clear = True
        while clear:
            if temp_col > 10:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(self.row, temp_col)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((self.row, temp_col))
            temp_col += 1

    def ppos(self, x):
        """Find the top or left pixel position of a given tile.

        Args:
            x (int): the row or column number

        Returns:
            (int): the top or left pixel location of the tile.
        """
        return x * (GSIZE + (GSIZE // 12)) + (GSIZE // 12)

    def ppos_cent(self, x, y):
        """Find the center pixel position of a given tile.

        Args:
            x (int): the row number
            y (int): the column number

        Returns:
            (int, int): tuple of the center pixel location of tile
        """
        return (self.ppos(x) + (GSIZE // 2), self.ppos(y) + (GSIZE // 2))

    def end_turn(self, piece):
        """Perform some cleanup to end the turn.

        Once the turn has been completed, the a_turn bool is flipped so the
        other player can go, the selected piece is deselected, and its color
        returns to normal.
        """
        self.a_turn = not self.a_turn
        self.selected = False
        piece.color = piece.base_color


class Board(object):
    """The Board class contains information about the physical board.

    Whereas the move class contains information about the state of the pieces,
    the Board class contains information for the look of the board.
    """

    def __init__(self):
        """Create a playing board and color code it.

        Attributes:
            grid (list(str)): A list of strings which classify each tile. Each
                              char in the string maps to a type of tile:
                                  x -> corner tile
                                  a -> initial attack tile
                                  d -> initial defend tile
                                  c -> center tile
            colors (dict): Maps the tiles to the appropriate color.
            dim (int): Dimension of the board (i.e. num of rows or cols.)
            piece (int): Size of playing piece.
        """
        self.grid = ["x..aaaaa..x",
                     ".....a.....",
                     "...........",
                     "a....d....a",
                     "a...ddd...a",
                     "aa.ddcdd.aa",
                     "a...ddd...a",
                     "a....d....a",
                     "...........",
                     ".....a.....",
                     "x..aaaaa..x"]

        self.colors = {'x': (92, 83, 70),
                       'a': (48, 43, 14),
                       'd': (57, 62, 65),
                       'c': (0, 0, 0),
                       '.': (203, 163, 40)}

        self.dim = len(self.grid)


class Piece(pygame.sprite.Sprite):
    """Class for all playing pieces.

    Pieces are pygame sprite objects. It makes grouping, determining
    collisions, and removing pieces very simple.
    """

    def __init__(self, x, y):
        """Create a piece at a given location.

        special_sqs, a bool which dermines if a piece is allowed to move
        onto the corners or center square, defaults to False.

        Args:
            x (int): the row that the piece will be placed
            y (int): the column that the piece will be placed.
        """
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.special_sqs = False
        self.pos_cent(x, y)

    def pos(self, x):
        """Find the top or left pixel position of a given tile.

        Args:
            x (int): the row or column number

        Returns:
            (int): the top or left pixel location of the tile.
        """
        return x * (GSIZE + (GSIZE // 12)) + (GSIZE // 12)

    def pos_cent(self, x, y):
        """Find the center pixel position of a given tile.

        Stores coordinates of the tile (x_tile and y_tile) as well as the
        center pixel locations of the tiles.

        Args:
            x (int): the row number
            y (int): the column number

        Returns:
            (int, int): tuple of the center pixel location of tile
        """
        self.x_tile = x
        self.y_tile = y
        self.x_px = self.pos(x) + (GSIZE // 2)
        self.y_px = self.pos(y) + (GSIZE // 2)
        self.rect = pygame.Rect([self.x_px - GSIZE // 2,
                                 self.y_px - GSIZE // 2,
                                 GSIZE,
                                 GSIZE])

    def draw(self, screen):
        """Draw the piece on the board in the correct location."""
        pygame.draw.circle(screen, self.color, [self.x_px, self.y_px],
                           GSIZE // 2)


class Attacker(Piece):
    """Class for all attacking pieces; inherits from Piece."""

    def __init__(self, x, y):
        """Inherit from Piece and give attacking piece a color."""
        Piece.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.base_color = (150, 0, 24)
        self.color = self.base_color


class Defender(Piece):
    """Class for all defending pieces; inherits from Piece."""

    def __init__(self, x, y):
        """Inherit from Piece and give attacking piece a color."""
        Piece.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.base_color = (255, 255, 240)
        self.color = self.base_color


class King(Defender):
    """Class for king; inherits from Defender."""

    def __init__(self, x, y):
        """Inherit from Piece and give attacking piece a color.

        The king can move on special squares, so special_sqs is True.
        """
        Defender.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.base_color = (255, 255, 0)
        self.color = self.base_color
        self.special_sqs = True