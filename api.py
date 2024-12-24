import requests

class MinesweeperAPI:
    """
    A Python client for the Minesweeper REST service.
    Usage:
        api = MinesweeperAPI("http://localhost:8000")
        api.init_board(rows=9, cols=9, mines=10)
        api.reveal_cell(3, 4)
        board_state = api.get_status()
    """
    def __init__(self, base_url: str):
        """
        :param base_url: The base URL of the Minesweeper server (e.g. 'http://localhost:8000')
        """
        self.base_url = base_url.rstrip("/")

    def init_board(self, rows: int = 9, cols: int = 9, mines: int = 10):
        """
        Initialize a new Minesweeper board.

        :param rows: Number of rows
        :param cols: Number of columns
        :param mines: Number of mines
        :return: dict with server response, e.g. { "status": "OK", "message": "Board initialized." }
        """
        url = f"{self.base_url}/init"
        params = {
            "rows": rows,
            "cols": cols,
            "mines": mines
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def reveal_cell(self, row: int, col: int):
        """
        Reveal a single cell on the board.

        :param row: Row index (0-based)
        :param col: Column index (0-based)
        :return: The entire updated board state as dict
        """
        url = f"{self.base_url}/reveal"
        params = {
            "row": row,
            "col": col
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def flag_cell(self, row: int, col: int):
        """
        Flag (or unflag) a single cell on the board.

        :param row: Row index (0-based)
        :param col: Column index (0-based)
        :return: The entire updated board state as dict
        """
        url = f"{self.base_url}/flag"
        params = {
            "row": row,
            "col": col
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_status(self):
        """
        Retrieve the current board status.

        :return: A dict containing keys like "rows", "cols", "game_over", "board", etc.
        """
        url = f"{self.base_url}/status"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()