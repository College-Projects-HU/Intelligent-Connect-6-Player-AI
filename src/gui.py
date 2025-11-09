# src/gui.py

import tkinter as tk
from tkinter import messagebox
from src.game_logic import Connect6Game


class Connect6GUI:
    def __init__(self, size=19):
        self.game = Connect6Game(size=size)
        self.size = size
        self.cell_size = 25  # Size of each cell in pixels
        self.selected_moves = []  # Moves selected in current turn
        self.game_over = False
        
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
            text=f"Player {self.game.current_player}'s turn - Place 1 stone",
            font=("Arial", 12, "bold"),
            pady=10
        )
        self.status_label.pack()
        
        # Canvas for the board
        canvas_size = self.size * self.cell_size
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
            text="Click on empty cells to place stones. First move: 1 stone, then 2 stones per turn.",
            font=("Arial", 9),
            fg="gray",
            wraplength=400
        )
        instructions.pack(pady=5)
    
    def draw_grid(self):
        """Draw the grid lines on the canvas."""
        self.canvas.delete("all")
        
        # Draw grid lines
        for i in range(self.size):
            # Vertical lines
            x = i * self.cell_size + self.cell_size // 2
            self.canvas.create_line(
                x, self.cell_size // 2,
                x, (self.size - 1) * self.cell_size + self.cell_size // 2,
                fill="black", width=1
            )
            # Horizontal lines
            y = i * self.cell_size + self.cell_size // 2
            self.canvas.create_line(
                self.cell_size // 2, y,
                (self.size - 1) * self.cell_size + self.cell_size // 2, y,
                fill="black", width=1
            )
        
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
        center_x = y * self.cell_size + self.cell_size // 2
        center_y = x * self.cell_size + self.cell_size // 2
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
        center_x = y * self.cell_size + self.cell_size // 2
        center_y = x * self.cell_size + self.cell_size // 2
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
        
        # Convert pixel coordinates to grid coordinates
        col = (event.x - self.cell_size // 2) // self.cell_size
        row = (event.y - self.cell_size // 2) // self.cell_size
        
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
            self.play_turn()
    
    def play_turn(self):
        """Play the selected moves."""
        if self.game.play_turn(self.selected_moves):
            # Game ended (win or draw)
            self.game_over = True
            self.draw_grid()
            self.update_status()
            
            # Show win/draw message
            if self.game.board.is_full():
                messagebox.showinfo("Game Over", "It's a draw!")
            else:
                # Winner is the current player (game logic doesn't switch on win)
                winner = self.game.current_player
                messagebox.showinfo("Game Over", f"Player {winner} wins!")
        else:
            # Game continues
            self.selected_moves = []
            self.update_status()
            self.draw_grid()
    
    def update_status(self):
        """Update the status label."""
        if self.game_over:
            if self.game.board.is_full():
                self.status_label.config(text="Game Over - It's a draw!")
            else:
                winner = 'O' if self.game.current_player == 'X' else 'X'
                self.status_label.config(text=f"Game Over - Player {winner} wins!")
        else:
            required_moves = 1 if self.game.first_move else 2
            moves_text = f"Place {required_moves} stone(s)"
            if self.selected_moves:
                moves_text += f" ({len(self.selected_moves)}/{required_moves} selected)"
            self.status_label.config(
                text=f"Player {self.game.current_player}'s turn - {moves_text}"
            )
    
    def clear_selection(self):
        """Clear the current selection."""
        if not self.game_over:
            self.selected_moves = []
            self.draw_grid()
            self.update_status()
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.game = Connect6Game(size=self.size)
        self.selected_moves = []
        self.game_over = False
        self.draw_grid()
        self.update_status()
    
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()

