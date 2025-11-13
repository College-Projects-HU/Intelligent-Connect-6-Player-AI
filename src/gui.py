# src/gui.py

import tkinter as tk
from tkinter import messagebox, simpledialog
from src.game_logic import Connect6Game


class Connect6GUI:
    @staticmethod
    def get_board_size_dialog():
        """
        Show a dialog to get board size from user (6-19).
        
        Returns:
            int: Valid board size between 6 and 19, or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        while True:
            size_str = simpledialog.askstring(
                "Board Size",
                "Enter board size (6-19):",
                parent=root
            )
            
            if size_str is None:
                root.destroy()
                return None  # User cancelled
            
            try:
                size = int(size_str)
                if size < 6:
                    messagebox.showerror(
                        "Invalid Size",
                        "Board size must be at least 6. Please try again.",
                        parent=root
                    )
                    continue
                if size > 19:
                    messagebox.showerror(
                        "Invalid Size",
                        "Board size must be at most 19. Please try again.",
                        parent=root
                    )
                    continue
                root.destroy()
                return size
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a valid number between 6 and 19.",
                    parent=root
                )
    def __init__(self, size=19, human_player='X', ai_player='O', ai_algorithm='minimax'):
        """
        Initialize the Connect 6 GUI.
        
        Args:
            size: Board size (default 19x19)
            human_player: The player symbol for the human ('X' or 'O', default 'X')
            ai_player: The player symbol for the AI ('X' or 'O', default 'O')
            ai_algorithm: Which algorithm to use ('minimax' or 'alpha_beta', default 'minimax')
        """
        self.game = Connect6Game(size=size, human_player=human_player, ai_player=ai_player, ai_algorithm=ai_algorithm, heuristic='heuristic_1')
        self.size = size
        self.cell_size = 25  # Size of each cell in pixels
        self.margin = self.cell_size  # Space around the board for labels/border
        self.selected_moves = []  # Moves selected in current turn
        self.game_over = False
        self.human_player = human_player
        self.ai_player = ai_player
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Connect 6")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text=f"Your turn (Player {self.human_player}) - Place 1 stone",
            font=("Arial", 12, "bold"),
            pady=10
        )
        self.status_label.pack()
        
        # Canvas for the board
        board_pixel_size = self.size * self.cell_size
        canvas_size = board_pixel_size + self.margin * 2
        self.canvas = tk.Canvas(
            main_frame,
            width=canvas_size,
            height=canvas_size,
            bg="#DEB887",  # Tan/burlywood color for Go board
            highlightthickness=2,
            highlightbackground="black"
        )
        self.canvas.pack(padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_cell_click)
        
        # Draw the grid
        self.draw_grid()
        
        # Control buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Reset button
        reset_button = tk.Button(
            button_frame,
            text="New Game",
            command=self.reset_game,
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Clear selection button
        clear_button = tk.Button(
            button_frame,
            text="Clear Selection",
            command=self.clear_selection,
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Instructions label
        instructions = tk.Label(
            main_frame,
            text="Click on empty cells to place stones. First move: 1 stone, then 2 stones per turn. AI will play automatically after your turn.",
            font=("Arial", 9),
            fg="gray",
            wraplength=400
        )
        instructions.pack(pady=5)
    
    def draw_grid(self):
        """Draw the grid lines on the canvas."""
        self.canvas.delete("all")
        
        board_start = self.margin
        board_end = self.margin + self.size * self.cell_size
        line_start = board_start + self.cell_size // 2
        line_end = board_end - self.cell_size // 2

        # Draw board border
        self.canvas.create_rectangle(
            board_start,
            board_start,
            board_end,
            board_end,
            outline="black",
            width=3
        )

        # Draw grid lines
        for i in range(self.size):
            # Vertical lines
            x = line_start + i * self.cell_size
            self.canvas.create_line(
                x, line_start,
                x, line_end,
                fill="black",
                width=1
            )
            # Horizontal lines
            y = line_start + i * self.cell_size
            self.canvas.create_line(
                line_start, y,
                line_end, y,
                fill="black",
                width=1
            )

        self.draw_labels()
        
        # Draw stones
        for i in range(self.size):
            for j in range(self.size):
                if self.game.board.grid[i][j] != '.':
                    self.draw_stone(i, j, self.game.board.grid[i][j])
        
        # Highlight selected moves
        for x, y in self.selected_moves:
            self.highlight_cell(x, y)
    
    def draw_stone(self, x, y, player):
        """Draw a stone at position (x, y) for the given player."""
        center_x = self.margin + y * self.cell_size + self.cell_size // 2
        center_y = self.margin + x * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 2
        
        if player == 'X':
            color = "black"
        else:  # player == 'O'
            color = "white"
        
        # Draw stone with a slight shadow effect
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=color, outline="black", width=1
        )
    
    def highlight_cell(self, x, y):
        """Highlight a cell to show it's selected."""
        center_x = self.margin + y * self.cell_size + self.cell_size // 2
        center_y = self.margin + x * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 1
        
        # Draw a circle to indicate selection
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="red", width=2, fill="", dash=(3, 3)
        )
    
    def on_cell_click(self, event):
        """Handle mouse click on the canvas."""
        if self.game_over:
            return
        
        # Only allow clicks during human player's turn
        if not self.game.is_human_turn():
            messagebox.showinfo("Not Your Turn", "Please wait for the AI to make its move.")
            return
        
        # Convert pixel coordinates to grid coordinates
        board_start = self.margin
        board_end = self.margin + self.size * self.cell_size

        if not (board_start <= event.x < board_end and board_start <= event.y < board_end):
            return

        col = int((event.x - board_start) // self.cell_size)
        row = int((event.y - board_start) // self.cell_size)
        
        # Check if click is within bounds
        if not (0 <= row < self.size and 0 <= col < self.size):
            return
        
        # Check if cell is already occupied
        if self.game.board.grid[row][col] != '.':
            messagebox.showwarning("Invalid Move", "This cell is already occupied!")
            return
        
        # Check if this move is already selected
        if (row, col) in self.selected_moves:
            messagebox.showwarning("Invalid Move", "This cell is already selected for this turn!")
            return
        
        required_moves = 1 if self.game.first_move else 2
        
        # Add to selection
        self.selected_moves.append((row, col))
        
        # Update display
        self.draw_grid()
        
        # If we have the required number of moves, play the turn
        if len(self.selected_moves) == required_moves:
            if self.confirm_selection():
                self.play_turn()
            else:
                self.selected_moves = []
                self.update_status()
                self.draw_grid()
    
    def play_turn(self):
        """Play the selected moves for the human player, then trigger AI move if game continues."""
        # Play human player's turn
        if self.game.play_turn(self.selected_moves):
            # Game ended (win or draw)
            self.game_over = True
            self.draw_grid()
            self.update_status()
            
            # Show win/draw message
            if self.game.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")
            else:
                # Winner is the current player (game logic doesn't switch on win)
                winner = self.game.current_player
                if winner == self.human_player:
                    messagebox.showinfo("Game Over", "Congratulations! You win!")
                else:
                    messagebox.showinfo("Game Over", f"AI (Player {self.ai_player}) wins!")
        else:
            # Game continues - clear selection and update display
            self.selected_moves = []
            self.update_status()
            self.draw_grid()
            
            # If it's now AI's turn, ask user to choose algorithm first
            if self.game.is_ai_turn() and not self.game_over:
                # Show dialog to choose AI algorithm
                self.choose_ai_algorithm()
    
    def choose_ai_algorithm(self):
        """Show a dialog to let the user choose the AI algorithm for this turn."""
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose AI Algorithm")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Instructions
        label = tk.Label(
            dialog,
            text="Choose AI Algorithm for this turn:",
            font=("Arial", 11, "bold"),
            pady=10
        )
        label.pack()
        
        # Variable to store the choice
        choice_var = tk.IntVar(value=1)
        
        # Radio buttons for each option
        options = [
            ("1 - Minimax with 1st heuristic", 1),
            ("2 - Minimax with 2nd heuristic", 2),
            ("3 - Alpha-Beta with 1st heuristic", 3),
            ("4 - Alpha-Beta with 2nd heuristic", 4)
        ]
        
        for text, value in options:
            rb = tk.Radiobutton(
                dialog,
                text=text,
                variable=choice_var,
                value=value,
                font=("Arial", 10),
                padx=20,
                pady=5
            )
            rb.pack(anchor=tk.W)
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def confirm_choice():
            choice = choice_var.get()
            if choice == 1:
                algorithm, heuristic = 'minimax', 'heuristic_1'
            elif choice == 2:
                algorithm, heuristic = 'minimax', 'heuristic_2'
            elif choice == 3:
                algorithm, heuristic = 'alpha_beta', 'heuristic_1'
            elif choice == 4:
                algorithm, heuristic = 'alpha_beta', 'heuristic_2'
            else:
                algorithm, heuristic = 'minimax', 'heuristic_1'
            
            self.game.set_ai_config(algorithm, heuristic)
            dialog.destroy()
            # Schedule AI move after dialog closes
            self.root.after(100, self.play_ai_turn)
        
        confirm_button = tk.Button(
            button_frame,
            text="Confirm",
            command=confirm_choice,
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        confirm_button.pack(side=tk.LEFT, padx=5)
    
    def play_ai_turn(self):
        """
        Get and play the AI's move.
        
        This method:
        1. Calls game.get_ai_move() to get the AI's move from the algorithm
        2. Plays the move using game.play_turn()
        3. Updates the display
        4. Checks if game is over
        """
        if self.game_over or not self.game.is_ai_turn():
            return
        
        # Update status to show AI is thinking
        algorithm_name = self.game.ai_algorithm.replace('_', '-').title()
        heuristic_name = self.game.heuristic.replace('_', ' ').title()
        self.status_label.config(
            text=f"AI (Player {self.ai_player}) is thinking using {algorithm_name} with {heuristic_name}..."
        )
        self.root.update()  # Force GUI update
        
        # Get AI move from the algorithm
        ai_moves = self.game.get_ai_move(depth=3)  # depth can be adjusted for AI strength
        
        if not ai_moves:
            # No valid moves available (shouldn't happen in normal play)
            messagebox.showwarning("AI Error", "AI could not find a valid move!")
            return
        
        # Play the AI's move
        if self.game.play_turn(ai_moves):
            # Game ended (win or draw)
            self.game_over = True
            self.draw_grid()
            self.update_status()
            
            # Show win/draw message
            if self.game.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")
            else:
                winner = self.game.current_player
                if winner == self.human_player:
                    messagebox.showinfo("Game Over", "Congratulations! You win!")
                else:
                    messagebox.showinfo("Game Over", f"AI (Player {self.ai_player}) wins!")
        else:
            # Game continues - update display
            self.update_status()
            self.draw_grid()
            # Now it's human player's turn again

    def update_status(self):
        """Update the status label."""
        if self.game_over:
            if self.game.is_draw():
                self.status_label.config(text="Game Over - It's a draw!")
            else:
                winner = self.game.current_player
                if winner == self.human_player:
                    self.status_label.config(text="Game Over - You win!")
                else:
                    self.status_label.config(text=f"Game Over - AI (Player {self.ai_player}) wins!")
        else:
            required_moves = 1 if self.game.first_move else 2
            if self.game.is_human_turn():
                moves_text = f"Place {required_moves} stone(s)"
                if self.selected_moves:
                    moves_text += f" ({len(self.selected_moves)}/{required_moves} selected)"
                self.status_label.config(
                    text=f"Your turn (Player {self.human_player}) - {moves_text}"
                )
            else:
                self.status_label.config(
                    text=f"AI (Player {self.ai_player}) is thinking..."
                )
    
    def clear_selection(self):
        """Clear the current selection."""
        if not self.game_over:
            self.selected_moves = []
            self.draw_grid()
            self.update_status()
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.game = Connect6Game(
            size=self.size,
            human_player=self.human_player,
            ai_player=self.ai_player,
            ai_algorithm=self.game.ai_algorithm,
            heuristic=self.game.heuristic
        )
        self.selected_moves = []
        self.game_over = False
        self.draw_grid()
        self.update_status()

    def draw_labels(self):
        """Draw row and column labels around the board."""
        label_font = ("Arial", 10, "bold")
        half_cell = self.cell_size / 2
        board_start = self.margin
        board_end = self.margin + self.size * self.cell_size

        for index in range(self.size):
            label_value = str(index + 1)
            x_position = board_start + index * self.cell_size + half_cell
            y_position = board_start + index * self.cell_size + half_cell

            # Column labels (top and bottom)
            self.canvas.create_text(
                x_position,
                board_start - half_cell,
                text=label_value,
                font=label_font
            )
            self.canvas.create_text(
                x_position,
                board_end + half_cell,
                text=label_value,
                font=label_font
            )

            # Row labels (left and right)
            self.canvas.create_text(
                board_start - half_cell,
                y_position,
                text=label_value,
                font=label_font
            )
            self.canvas.create_text(
                board_end + half_cell,
                y_position,
                text=label_value,
                font=label_font
            )

    def confirm_selection(self):
        """Ask the player to confirm the selected moves before playing."""
        moves_text = ", ".join(
            f"({row + 1}, {col + 1})" for row, col in self.selected_moves
        )
        return messagebox.askyesno(
            "Confirm Moves",
            f"Play moves {moves_text}?"
        )
    
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()

