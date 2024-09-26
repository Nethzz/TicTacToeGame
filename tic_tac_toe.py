import tkinter as tk
from tkinter import messagebox
import sqlite3

def print_board(board):
    """
    Print the current state of the Tic-Tac-Toe board.
    """
    for row in board:
        print(" | ".join(row))
        print("-" * 5)

def initialize_board():
    """
    Initialize the Tic-Tac-Toe board with empty spaces.
    """
    return [[' ' for _ in range(3)] for _ in range(3)]

def is_valid_move(board, row, col):
    """
    Check if the move is valid (the cell is empty).
    """
    return board[row][col] == ' '

def make_move(board, row, col, player):
    """
    Make a move on the board if it is valid.
    """
    if is_valid_move(board, row, col):
        board[row][col] = player
        return True
    return False

def check_winner(board):
    """
    Check if there is a winner on the board.
    """
    lines = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[2][0], board[1][1], board[0][2]],
    ]
    for line in lines:
        if line[0] == line[1] == line[2] and line[0] != ' ':
            return line[0]
    return None

def is_board_full(board):
    """
    Check if the board is full (no empty spaces left).
    """
    return all(cell != ' ' for row in board for cell in row)

def minimax(board, depth, is_maximizing, alpha, beta):
    """
    Minimax algorithm with alpha-beta pruning to find the best move.
    """
    winner = check_winner(board)
    if winner == 'X':
        return -10 + depth
    if winner == 'O':
        return 10 - depth
    if is_board_full(board):
        return 0

    if is_maximizing:
        max_eval = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    eval = minimax(board, depth + 1, False, alpha, beta)
                    board[i][j] = ' '
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    eval = minimax(board, depth + 1, True, alpha, beta)
                    board[i][j] = ' '
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval

def find_best_move(board):
    """
    Find the best move for the AI using the minimax algorithm.
    """
    best_move = None
    best_value = -float('inf')
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                move_value = minimax(board, 0, False, -float('inf'), float('inf'))
                board[i][j] = ' '
                if move_value > best_value:
                    best_move = (i, j)
                    best_value = move_value
    return best_move

def on_button_click(row, col):
    global board
    if board[row][col] == ' ':
        make_move(board, row, col, 'X')
        update_buttons()
        if check_winner(board):
            messagebox.showinfo("Tic-Tac-Toe", "Player X wins!")
            reset_game()
        elif is_board_full(board):
            messagebox.showinfo("Tic-Tac-Toe", "It's a draw!")
            reset_game()
        else:
            root.after(500, ai_move)  # Delay AI's move by 500 milliseconds

def ai_move():
    ai_move = find_best_move(board)
    make_move(board, ai_move[0], ai_move[1], 'O')
    update_buttons()
    if check_winner(board):
        messagebox.showinfo("Tic-Tac-Toe", "Player O wins!")
        reset_game()
    elif is_board_full(board):
        messagebox.showinfo("Tic-Tac-Toe", "It's a draw!")
        reset_game()

def update_buttons():
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text=board[i][j])

def reset_game():
    global board
    winner = check_winner(board)
    if winner:
        save_game(board, winner)
    board = initialize_board()
    update_buttons()

def save_game(board, winner):
    board_str = ''.join([''.join(row) for row in board])
    c.execute("INSERT INTO games (board, winner) VALUES (?, ?)", (board_str, winner))
    conn.commit()

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('tic_tac_toe.db')
c = conn.cursor()

# Create a table to store game states
c.execute('''CREATE TABLE IF NOT EXISTS games
             (id INTEGER PRIMARY KEY, board TEXT, winner TEXT)''')
conn.commit()

# Initialize the game
board = initialize_board()

# Create the main window
root = tk.Tk()
root.title("Tic-Tac-Toe")

# Create the buttons
buttons = [[None for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(root, text=' ', font='normal 20 bold', width=5, height=2,
                                  command=lambda row=i, col=j: on_button_click(row, col))
        buttons[i][j].grid(row=i, column=j)

# Make sure to close the database connection when the application exits
root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

# Start the GUI event loop
root.mainloop()
