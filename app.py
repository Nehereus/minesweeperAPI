import random
from flask import Flask, request, jsonify

app = Flask(__name__)

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

    def reveal(self, r, c):
        # Out-of-range or game over checks
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return
        if self.game_over:
            return
        cell = self.cells[r][c]
        if cell.is_revealed or cell.is_flagged:
            return

        cell.is_revealed = True
        # If it was a mine, game over
        if cell.is_mine:
            self.game_over = True
            return

        # Flood reveal if no adjacent mines
        if cell.adjacent_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal(r + dr, c + dc)

    def flag(self, r, c):
        if self.game_over:
            return
        if 0 <= r < self.rows and 0 <= c < self.cols:
            cell = self.cells[r][c]
            # Toggle flag only if cell is not revealed
            if not cell.is_revealed:
                cell.is_flagged = not cell.is_flagged

# --------- Global Game State ---------

board = None  # We'll store a single global board for demo

# --------- Helper Functions ---------

def board_to_json(b: Board):
    # Build a JSON-friendly structure
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
        "board": rows_data
    }

# --------- Routes ---------

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
    """
    Reveal a given cell and return the updated board status
    so that you can see exactly which cells are now revealed.
    """
    global board
    if board is None:
        return jsonify({"error": "Board not initialized"}), 400

    try:
        r = int(request.args["row"])
        c = int(request.args["col"])
    except (KeyError, ValueError):
        return jsonify({"error": "Missing or invalid parameters"}), 400

    if r < 0 or r >= board.rows or c < 0 or c >= board.cols:
        return jsonify({"error": "Out of range"}), 400

    board.reveal(r, c)
    # Return the entire updated board
    return jsonify(board_to_json(board))

@app.route("/flag", methods=["GET"])
def flag_cell():
    global board
    if board is None:
        return jsonify({"error": "Board not initialized"}), 400

    try:
        r = int(request.args["row"])
        c = int(request.args["col"])
    except (KeyError, ValueError):
        return jsonify({"error": "Missing or invalid parameters"}), 400

    if r < 0 or r >= board.rows or c < 0 or c >= board.cols:
        return jsonify({"error": "Out of range"}), 400

    board.flag(r, c)
    # Return the entire updated board
    return jsonify(board_to_json(board))

@app.route("/status", methods=["GET"])
def status_board():
    global board
    if board is None:
        return jsonify({"error": "Board not initialized"}), 400
    return jsonify(board_to_json(board))

# --------- Main Entry Point ---------

if __name__ == "__main__":
    # Run Flask dev server on http://localhost:5000
    app.run(port=8000, debug=True)
