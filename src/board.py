# src/board.py
import constants as c
class Board:
    def __init__(self, size=c.BOARD_SIZE):
        """
        Initialize the board with a given size (default 19x19).
        Each cell is represented by '.' when it's empty.
        """
        self.size = size
        self.grid = [[c.EMPTY for _ in range(size)] for _ in range(size)]

    def display(self):
        """
        Print the board to the console.
        Each row of the grid is displayed as space-separated symbols.
        """

        print("    ", end="")  # Add padding before column numbers
        for col in range(self.size):
            # Each column number is right-aligned with width 2 (1-indexed for display)
            print(f"{col + 1:2}", end=" ")
        print()  # New line after column numbers

        # Print a separating line for clarity
        print("   " + "---" * self.size)

        # Print each row with its row number at the start
        for row_index, row in enumerate(self.grid):
            print(f"{row_index + 1:2} |", end=" ")  # Row number (1-indexed) and separator
            for cell in row:
                print(cell, end="  ")
            print()  # New line at the end of each row
        print()  # Extra spacing after the board



    def is_valid_move(self, x, y):
        """
        Check if a move at (x, y) is valid.
        A move is valid if:
          - The coordinates are inside the board boundaries.
          - The cell is currently empty ('.').
        """
        return (
            0 <= x < self.size and
            0 <= y < self.size and
            self.grid[x][y] == '.'
        )

    def place_move(self, x, y, player):
        """
        Place a player's symbol ('X' or 'O') at position (x, y)
        if the move is valid. Returns True if the move was made,
        otherwise False.
        """
        if not self.is_valid_move(x, y):
            return False
        self.grid[x][y] = player
        return True
        
    def undo_move(self, x, y):
        if self.grid[x][y] != c.EMPTY:
            self.grid[x][y] = c.EMPTY
            return True
        return False

    def is_full(self):
        """
        Check if the board is completely filled.
        This is used to detect a draw condition.
        """
        return all(cell != '.' for row in self.grid for cell in row)

    def copy(self):
        """
        Create and return a deep copy of the board.
        This will be useful later for AI algorithms like Minimax
        that simulate possible moves.
        """
        import copy
        new_board = Board(self.size)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board
