# src/game.py

from src.board import Board

class Connect6Game:
    def __init__(self, size=19):
        self.board = Board(size)
        self.current_player = 'X'
        self.first_move = True  # First-ever move: only one stone allowed

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_available_moves(self):
        return [
            (i, j)
            for i in range(self.board.size)
            for j in range(self.board.size)
            if self.board.grid[i][j] == '.'
        ]

    def check_winner(self, x, y):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            i, j = x + dx, y + dy
            while 0 <= i < self.board.size and 0 <= j < self.board.size and \
                  self.board.grid[i][j] == self.current_player:
                count += 1
                i += dx; j += dy
            i, j = x - dx, y - dy
            while 0 <= i < self.board.size and 0 <= j < self.board.size and \
                  self.board.grid[i][j] == self.current_player:
                count += 1
                i -= dx; j -= dy
            if count >= 6:
                return True
        return False

    def _validate_moves_atomic(self, moves):
        """
        Validate moves *without changing the board*.
        Ensures:
          - Correct number of moves for the current turn (1 for first move, else 2).
          - All coordinates are inside board bounds.
          - All target cells are empty.
          - No duplicate coordinates inside the same turn.
        Returns:
          (True, "") if valid; (False, "reason") if invalid.
        """
        required_moves = 1 if self.first_move else 2
        if len(moves) != required_moves:
            return False, f"You must provide exactly {required_moves} move(s)."

        seen = set()
        for (x, y) in moves:
            # Check coordinate types and bounds
            if not (isinstance(x, int) and isinstance(y, int)):
                return False, "Coordinates must be integers."
            if not (0 <= x < self.board.size and 0 <= y < self.board.size):
                return False, f"Move ({x}, {y}) is out of bounds."
            # Check cell is empty
            if self.board.grid[x][y] != '.':
                return False, f"Cell ({x}, {y}) is already occupied."
            # Check for duplicates within the same turn
            if (x, y) in seen:
                return False, f"Duplicate move ({x}, {y}) in the same turn."
            seen.add((x, y))

        return True, ""

    def play_turn(self, moves):
        """
        Play a turn atomically:
         1. Validate all moves first (no changes made if any invalid).
         2. If all valid, place them in the same order provided.
         3. After each placement, check for a win.
         4. If the board fills up, declare a draw.

        Args:
          moves: list of (x,y) tuples. For first turn, length must be 1; otherwise 2.
        Returns:
          True if the game ended (win or draw), False if game continues.
        """
        # 1. Validate without placing
        valid, reason = self._validate_moves_atomic(moves)
        if not valid:
            print("Invalid move(s):", reason)
            return False  # Do not change the board or switch players

        # 2. Place moves (safe to do now)
        for (x, y) in moves:
            # place_move should succeed because we already validated
            self.board.place_move(x, y, self.current_player)

            # 3. Check for winner after each placed stone
            if self.check_winner(x, y):
                self.board.display()
                print(f"Player {self.current_player} wins!")
                return True

        # 4. Check for draw (board full)
        if self.board.is_full():
            self.board.display()
            print("It's a draw!")
            return True

        # After the very first move, switch off the single-move mode
        if self.first_move:
            self.first_move = False

        # Switch player for next turn
        self.switch_player()
        return False
