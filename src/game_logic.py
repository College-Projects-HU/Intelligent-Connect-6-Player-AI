# src/game_logic.py

from src.board import Board

class Connect6Game:
    def __init__(self, size=19, human_player='X', ai_player='O', ai_algorithm='minimax', heuristic='heuristic_1'):
        """
        Initialize the Connect 6 game.
        
        Args:
            size: Board size (default 19x19)
            human_player: The player symbol for the human ('X' or 'O', default 'X')
            ai_player: The player symbol for the AI ('X' or 'O', default 'O')
            ai_algorithm: Which algorithm to use ('minimax' or 'alpha_beta', default 'minimax')
            heuristic: Which heuristic to use ('heuristic_1' or 'heuristic_2', default 'heuristic_1')
        """
        self.board = Board(size)
        self.current_player = 'X'
        self.first_move = True  # First-ever move: only one stone allowed
        self.human_player = human_player
        self.ai_player = ai_player
        self.ai_algorithm = ai_algorithm  # 'minimax' or 'alpha_beta'
        self.heuristic = heuristic  # 'heuristic_1' or 'heuristic_2'
        self.last_row = None
        self.last_col = None
        # Maintain a set of available moves for O(1) access instead of O(n^2) scanning
        self.available_moves = {(i, j) for i in range(size) for j in range(size)}


    def set_ai_config(self, algorithm, heuristic):
        """
        Set the AI algorithm and heuristic to use.
        
        Args:
            algorithm: 'minimax' or 'alpha_beta'
            heuristic: 'heuristic_1' or 'heuristic_2'
        """
        self.ai_algorithm = algorithm
        self.heuristic = heuristic

    def is_ai_turn(self):
        """Check if it's currently the AI's turn."""
        return self.current_player == self.ai_player

    def is_human_turn(self):
        """Check if it's currently the human player's turn."""
        return self.current_player == self.human_player

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_available_moves(self):
        """
        Get all available empty positions on the board.
        Optimized to O(1) by maintaining a set of available moves.
        Returns a list of (x, y) tuples.
        """
        return list(self.available_moves)
    
    def _remove_move(self, x, y):
        """Remove a move from the available moves set when it's placed."""
        self.available_moves.discard((x, y))
    
    def _add_move(self, x, y):
        """Add a move back to the available moves set when it's undone."""
        if 0 <= x < self.board.size and 0 <= y < self.board.size:
            self.available_moves.add((x, y))

    def is_draw(self):
        """
        Check if the game is in a draw state.
        
        A draw occurs when:
        1. The board is completely filled, OR
        2. The board size is even AND there's only 1 empty cell remaining 
           AND it's not the first move (current player needs 2 moves but only 1 available).
        
        Returns:
            True if the game is a draw, False otherwise.
        """
        # Check if board is full
        if self.board.is_full():
            return True
        
        # Check for the special case: even board size, 1 empty cell, not first move
        empty_count = self.board.get_empty_cells_count()
        board_size_even = (self.board.size % 2 == 0)
        requires_two_moves = not self.first_move
        
        if board_size_even and empty_count == 1 and requires_two_moves:
            return True
        
        return False

    def get_ai_move(self, depth=2):
        """
        Get the AI's move using the specified algorithm.
        
        This method will call either minimax or alpha_beta algorithm to determine
        the best move for the AI player.
        
        Args:
            depth: The depth to search in the game tree (default 3)
                  Higher depth = stronger AI but slower computation
        
        Returns:
            List of moves [(x1, y1), (x2, y2)] for the AI to play.
            For first move, returns [(x, y)] (single move).
            Returns empty list if no valid moves available.
        
        TODO: This method needs to be implemented to call the actual algorithms.
        Currently returns a placeholder that picks the first available moves.
        """
        available_moves = self.get_available_moves()
        if not available_moves:
            return []
        
        required_moves = 1 if self.first_move else 2
        
        # Call the appropriate AI algorithm
        # TODO: The algorithms (minimax and alpha_beta) need to be fully implemented
        # Currently they return placeholder values, so the AI will use a fallback strategy
        try:
            if self.ai_algorithm == 'minimax':
                from src.minimax import minimax
                # minimax returns (score, moves). Unpack properly.
                result = minimax(self, depth, True)
                # Debug: show raw minimax return so we can verify the moves used
                try:
                    print(f"[get_ai_move] minimax raw result: {result}")
                except Exception:
                    pass
                if isinstance(result, tuple) and len(result) == 2:
                    _, best_moves = result
                else:
                    best_moves = result

                # If algorithm returns valid moves, use them
                if best_moves and len(best_moves) == required_moves:
                    # Validate that all moves are still available
                    if all(move in available_moves for move in best_moves):
                        # Display chosen moves (1-based coords for user clarity)
                        try:
                            disp = [(m[0] + 1, m[1] + 1) for m in best_moves]
                            print(f"AI chooses: {disp}")
                        except Exception:
                            print(f"AI chooses: {best_moves}")
                        return best_moves
            elif self.ai_algorithm == 'alpha_beta':
                from src.alpha_beta import AlphaBetaPruning
                best_moves = AlphaBetaPruning(self, self.heuristic,depth).find_best_move(self)
                # If algorithm returns valid moves, use them
                if best_moves and len(best_moves) == required_moves:
                    # Validate that all moves are still available
                    if all(move in available_moves for move in best_moves):
                        try:
                            disp = [(m[0] + 1, m[1] + 1) for m in best_moves]
                            print(f"AI chooses: {disp}")
                        except Exception:
                            print(f"AI chooses: {best_moves}")
                        return best_moves
        except Exception as e:
            # If algorithm implementation has errors, fall back to simple strategy
            print(f"AI algorithm error (using fallback): {e}")
        
        # Fallback: If algorithms are not implemented or return invalid moves,
        # use a simple strategy (pick first available moves)
        # TODO: Remove this fallback once algorithms are fully implemented
        chosen = available_moves[:required_moves]
        try:
            disp = [(m[0] + 1, m[1] + 1) for m in chosen]
            print(f"AI chooses (fallback): {disp}")
        except Exception:
            print(f"AI chooses (fallback): {chosen}")
        return chosen

    def evaluate_position(self):
        """
        Evaluate the current board position from the AI's perspective.
        
        This is a heuristic function that should return:
        - Positive values: Good for AI (maximizing player)
        - Negative values: Good for human (minimizing player)
        - Zero: Neutral position
        
        Returns:
            A numerical score representing the position's value.
        """
        from src.heuristics import heuristic_1, heuristic_2
        
        if self.heuristic == 'heuristic_1':
            return heuristic_1(self)
        elif self.heuristic == 'heuristic_2':
            return heuristic_2(self)
        else:
            # Default to heuristic_1 if invalid
            return heuristic_1(self)

    def make_move_copy(self, moves, player):
        """
        Create a copy of the game state and apply moves to it.
        This is used by AI algorithms to simulate moves without modifying the actual game.
        
        Args:
            moves: List of (x, y) tuples to apply
            player: The player making the moves ('X' or 'O')
        
        Returns:
            A new Connect6Game instance with the moves applied.
        """
        # Create a copy of the board
        new_game = Connect6Game(
            size=self.board.size,
            human_player=self.human_player,
            ai_player=self.ai_player,
            ai_algorithm=self.ai_algorithm,
            heuristic=self.heuristic
        )
        new_game.board = self.board.copy()
        new_game.current_player = player
        new_game.first_move = self.first_move
        # Copy the available moves set
        new_game.available_moves = self.available_moves.copy()
        
        # Apply the moves
        last = None
        for x, y in moves:
            new_game.board.place_move(x, y, player)
            new_game._remove_move(x, y)
            last = (x, y)

        # Update first_move flag if needed
        if new_game.first_move:
            new_game.first_move = False
        else:
            # Switch player after applying moves (simulating a turn)
            new_game.switch_player()

        # Record last move position(s)
        if last:
            new_game.last_row, new_game.last_col = last

        # If the simulated moves were made by the human, record them as the
        # last human moves so search heuristics can focus around them.
        if player == self.human_player:
            new_game.last_human_moves = set(moves)

        return new_game

    def check_winner(self, x, y):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        # Determine which player's stone is at (x, y). This makes the check
        # independent of `self.current_player` and safe to call on simulated
        # game states where `current_player` might have been switched.
        if not (0 <= x < self.board.size and 0 <= y < self.board.size):
            return False
        player = self.board.grid[x][y]
        if player == '.':
            return False

        for dx, dy in directions:
            count = 1
            i, j = x + dx, y + dy
            while 0 <= i < self.board.size and 0 <= j < self.board.size and \
                  self.board.grid[i][j] == player:
                count += 1
                i += dx; j += dy
            i, j = x - dx, y - dy
            while 0 <= i < self.board.size and 0 <= j < self.board.size and \
                  self.board.grid[i][j] == player:
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
            display_x, display_y = x + 1, y + 1
            # Check coordinate types and bounds
            if not (isinstance(x, int) and isinstance(y, int)):
                return False, "Coordinates must be integers."
            if not (0 <= x < self.board.size and 0 <= y < self.board.size):
                return False, (
                    f"Move ({display_x}, {display_y}) is out of bounds. "
                    f"Valid indices are 1 to {self.board.size}."
                )
            # Check cell is empty
            if self.board.grid[x][y] != '.':
                return False, f"Cell ({display_x}, {display_y}) is already occupied."
            # Check for duplicates within the same turn
            if (x, y) in seen:
                return False, f"Duplicate move ({display_x}, {display_y}) in the same turn."
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
        last = None
        for (x, y) in moves:
            # place_move should succeed because we already validated
            self.board.place_move(x, y, self.current_player)
            # Update available moves set
            self._remove_move(x, y)
            last = (x, y)

            # 3. Check for winner after each placed stone
            if self.check_winner(x, y):
                self.board.display()
                print(f"Player {self.current_player} wins!")
                return True

        # 4. Check for draw (board full or special even board case)
        if self.is_draw():
            self.board.display()
            print("It's a draw!")
            return True

        # After the very first move, switch off the single-move mode
        if self.first_move:
            self.first_move = False

        # Record last move coordinates and last human moves (if human played)
        if last:
            self.last_row, self.last_col = last
            if self.current_player == self.human_player:
                self.last_human_moves = set(moves)

        # Switch player for next turn
        self.switch_player()
        return False
