import requests
import sys

BASE_URL = "http://localhost:8000"  # Adjust if your server is on a different port/host

def print_pass(msg):
    print(f"[PASS] {msg}")

def print_fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)  # Exit immediately on test failure

def test_init():
    print("Testing /init ...")
    params = {"rows": 9, "cols": 9, "mines": 10}
    r = requests.get(f"{BASE_URL}/init", params=params)
    if r.status_code != 200:
        print_fail(f"/init returned status code {r.status_code}, expected 200")
    data = r.json()
    if data.get("status") != "OK":
        print_fail(f"/init failed, response: {data}")
    print_pass("/init responded with status=OK")

def test_status_before_reveal():
    print("Testing /status before any reveal...")
    r = requests.get(f"{BASE_URL}/status")
    if r.status_code != 200:
        print_fail(f"/status returned status code {r.status_code}, expected 200")

    data = r.json()
    if "rows" not in data or "cols" not in data or "board" not in data:
        print_fail(f"Malformed /status response: {data}")
    if not isinstance(data["board"], list) or len(data["board"]) == 0:
        print_fail("Board data not in expected format")
    # Spot-check a cell
    first_cell = data["board"][0][0]
    if not first_cell.get("covered", False):
        print_fail("Expected the first cell to be covered before any reveal")
    print_pass("/status responded with a valid, covered board")

def test_reveal():
    print("Testing /reveal...")
    # Reveal (row=3, col=4)
    r = requests.get(f"{BASE_URL}/reveal", params={"row": 3, "col": 4})
    if r.status_code != 200:
        print_fail(f"/reveal returned status code {r.status_code}, expected 200")

    data = r.json()
    # The updated board state should be returned
    if "board" not in data:
        print_fail("Expected an updated board in /reveal response but not found")

    # Check if game_over is a boolean
    if "game_over" not in data or not isinstance(data["game_over"], bool):
        print_fail("Invalid or missing 'game_over' in /reveal response")
    
    # If that cell was not a mine, it should be revealed
    cell_after_reveal = data["board"][3][4]
    if cell_after_reveal.get("covered") is True:
        print_fail("Cell (3,4) should no longer be covered after reveal")
    # We won't know if it's a mine or a number, but it shouldn't be covered if we successfully revealed
    print_pass("/reveal for cell (3,4) updated the board correctly")

def test_flag():
    print("Testing /flag...")
    # Flag (row=2, col=2)
    r = requests.get(f"{BASE_URL}/flag", params={"row": 8, "col": 9})
    if r.status_code != 200:
        print_fail(f"/flag returned status code {r.status_code}, expected 200")

    data = r.json()
    if "board" not in data:
        print_fail("Expected an updated board in /flag response but not found")
    cell_after_flag = data["board"][2][2]
    # If the cell was not revealed, it should now be flagged: {"covered": true, "flagged": true}
    covered = cell_after_flag.get("covered", False)
    flagged = cell_after_flag.get("flagged", False)
    if not covered or not flagged:
        print_fail("Cell (2,2) should be covered and flagged after /flag call")
    print_pass("/flag toggled the flag status correctly")

def test_reveal_out_of_range():
    print("Testing /reveal with out-of-range cell ...")
    r = requests.get(f"{BASE_URL}/reveal", params={"row": 999, "col": 999})
    # We expect a 400 or similar error code
    if r.status_code == 200:
        print_fail("Expected an error status when revealing out-of-range, got 200")
    data = r.json()
    if "error" not in data:
        print_fail("Expected an error message in out-of-range reveal response, none found")
    print_pass("Out-of-range reveal returned a correct error response")

def main():
    print("\n--- Minesweeper API Integration Tests ---\n")
    try:
        # 1. Initialize the board
        test_init()

        # 2. Check board status (all covered)
        test_status_before_reveal()

        # 3. Reveal a cell
        test_reveal()

        # 4. Flag a different cell
        test_flag()

        # 5. Attempt to reveal an out-of-range cell
        test_reveal_out_of_range()

        print("\nAll tests PASSED successfully!\n")
    except SystemExit as e:
        # If a test failed, we already printed a [FAIL] message and exited
        pass

if __name__ == "__main__":
    main()
