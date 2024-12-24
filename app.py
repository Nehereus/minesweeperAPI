from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
# --------- Data Structures ---------

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.total_mines = mines

        self.game_over = False
        self.game_won = False

        # Track how many safe cells are revealed so far
        self.revealed_count = 0

        # Create board
        self.cells = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self._place_mines()
        self._calculate_adjacency()

    def _place_mines(self):
        placed = 0
        while placed < self.total_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if not self.cells[r][c].is_mine:
                self.cells[r][c].is_mine = True
                placed += 1

    def _calculate_adjacency(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].is_mine:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        rr = r + dr
                        cc = c + dc
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            if self.cells[rr][cc].is_mine:
                                count += 1
                self.cells[r][c].adjacent_mines = count

    def _check_win(self):
        """ Check if revealed_count covers all non-mine cells. """
        # Number of total safe cells
        total_safe_cells = self.rows * self.cols - self.total_mines
        if self.revealed_count == total_safe_cells:
            self.game_over = True
            self.game_won = True

    def reveal(self, r, c):
        """ Reveal the cell (r, c). If it's safe and has 0 adjacent mines, recursively reveal neighbors. """
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return
        if self.game_over:
            return

        cell = self.cells[r][c]
        # If already revealed or flagged, do nothing
        if cell.is_revealed or cell.is_flagged:
            return

        # Reveal this cell
        cell.is_revealed = True
        # If it was not a mine, increment revealed_count
        if not cell.is_mine:
            self.revealed_count += 1
        else:
            # Hitting a mine => lose
            self.game_over = True
            self.game_won = False
            return

        # Flood reveal if no adjacent mines
        if cell.adjacent_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal(r + dr, c + dc)

        # After revealing, check if we won
        self._check_win()

    def flag(self, r, c):
        if self.game_over:
            return
        if 0 <= r < self.rows and 0 <= c < self.cols:
            cell = self.cells[r][c]
            # Toggle flag only if cell is not revealed
            if not cell.is_revealed:
                cell.is_flagged = not cell.is_flagged
            else:
                return

# --------- Global Game State ---------

board = None  # We'll store a single global board for demo

# --------- Helper Functions ---------

def board_to_json(b):
    """Convert the board to JSON including a status: 'win', 'lose', or 'in_progress'."""
    if b.game_over:
        status = "win" if b.game_won else "lose"
    else:
        status = "in_progress"

    # Build JSON structure (similar to above)
    rows_data = []
    for r in range(b.rows):
        row_list = []
        for c in range(b.cols):
            cell = b.cells[r][c]
            if not cell.is_revealed:
                row_list.append({
                    "covered": True,
                    "flagged": cell.is_flagged
                })
            else:
                if cell.is_mine:
                    row_list.append({"mine": True})
                else:
                    row_list.append({"adjacent": cell.adjacent_mines})
        rows_data.append(row_list)

    return {
        "rows": b.rows,
        "cols": b.cols,
        "game_over": b.game_over,
        "game_won": b.game_won,
        "status": status,
        "board": rows_data
    }

    return {
        "rows": b.rows,
        "cols": b.cols,
        "game_over": b.game_over,
        "game_won": b.game_won,
        "status": status,
        "board": rows_data
    }

# --------- Flask Routes ---------
@app.route("/init", methods=["GET"])
def init_board():
    global board
    rows = int(request.args.get("rows", 9))
    cols = int(request.args.get("cols", 9))
    mines = int(request.args.get("mines", 10))

    board = Board(rows, cols, mines)
    return jsonify({"status": "OK", "message": "Board initialized."})

@app.route("/reveal", methods=["GET"])
def reveal_cell():
    global board
    if board is None:
        return jsonify({"error": "Board not initialized"}), 400

    r = int(request.args.get("row", -1))
    c = int(request.args.get("col", -1))
    if r < 0 or r >= board.rows or c < 0 or c >= board.cols:
        return jsonify({"error": "Out of range"}), 400

    board.reveal(r, c)
    # After changing state, broadcast to all
    # socketio.emit("board_update", board_to_json(board), broadcast=True)
    socketio.emit("board_update", board_to_json(board))
    return jsonify(board_to_json(board))

@app.route("/flag", methods=["GET"])
def flag_cell():
    global board
    if board is None:
        return jsonify({"error": "Board not initialized"}), 400

    r = int(request.args.get("row", -1))
    c = int(request.args.get("col", -1))
    if r < 0 or r >= board.rows or c < 0 or c >= board.cols:
        return jsonify({"error": "Out of range"}), 400

    board.flag(r, c)
    # After changing state, broadcast to all
    socketio.emit("board_update", board_to_json(board))
    return jsonify(board_to_json(board))

@app.route("/status", methods=["GET"])
def status_board():
    global board
    if board is None:
        return jsonify({"error": "Board not initialized"}), 400
    return jsonify(board_to_json(board))

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
