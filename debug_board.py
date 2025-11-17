from src.game_logic import Connect6Game

# Reproduce the board from the failing run
g = Connect6Game()
# Place O's (AI) on row 6, cols 7-11 (1-indexed in display)
o_coords = [(5,6),(5,7),(5,8),(5,9),(5,10)]
# Place X's (human) on row 8, cols 6-11
x_coords = [(7,5),(7,6),(7,7),(7,8),(7,9),(7,10)]

for x,y in o_coords:
    g.board.grid[x][y] = g.ai_player
    g.board.empty_cells -= 1
for x,y in x_coords:
    g.board.grid[x][y] = g.human_player
    g.board.empty_cells -= 1

# Rebuild available moves set
g.available_moves = {(i,j) for i in range(g.board.size) for j in range(g.board.size) if g.board.grid[i][j] == '.'}

g.first_move = False
# Set it to AI's turn (so it should try to block)
g.current_player = g.ai_player

print('Current board:')
g.board.display()
print('AI move suggestion (depth=2):')
print(g.get_ai_move(depth=2))
