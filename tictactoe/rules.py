from config import logging_config
logging = logging_config.setup_logging(__name__)

def check_winner(board, board_size, game_mode, session_id, x_points, o_points, save_points, combos):
    if board_size == 3:
        win_length = 3
    elif board_size in [5, 7]:
        win_length = 4
    else:
        win_length = board_size

    def check_combinations(combinations):
        for combo in combinations:
            if all(board[pos] == board[combo[0]] and board[pos] != " " for pos in combo):
                return board[combo[0]]
        return None

    if game_mode == 0 or game_mode == 2:
        winning_combinations = []

        for i in range(board_size):
            for j in range(board_size - win_length + 1):
                winning_combinations.append([i * board_size + k for k in range(j, j + win_length)])

        for i in range(board_size):
            for j in range(board_size - win_length + 1):
                winning_combinations.append([k * board_size + i for k in range(j, j + win_length)])

        for i in range(board_size - win_length + 1):
            for j in range(board_size - win_length + 1):
                winning_combinations.append([((i + k) * board_size + (j + k)) for k in range(win_length)])

        for i in range(board_size - win_length + 1):
            for j in range(win_length - 1, board_size):
                winning_combinations.append([((i + k) * board_size + (j - k)) for k in range(win_length)])

        if game_mode == 0 or game_mode == 2:
            winner = check_combinations(winning_combinations)
            if winner:
                return winner

    if game_mode == 1:
        def is_valid(x, y):
            return 0 <= x < board_size and 0 <= y < board_size

        def check_recursive(x, y, symbol, visited):
            if len(visited) == win_length:
                return True
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if is_valid(nx, ny) and (nx, ny) not in visited and board[nx * board_size + ny] == symbol:
                    if check_recursive(nx, ny, symbol, visited | {(nx, ny)}):
                        return True
            return False

        for i in range(board_size):
            for j in range(board_size):
                if board[i * board_size + j] != " ":
                    symbol = board[i * board_size + j]
                    if check_recursive(i, j, symbol, {(i, j)}):
                        return symbol

    if game_mode == 0 or game_mode == 1:
        if all(cell != " " for cell in board):
            return "draw"

    if game_mode == 2:
        point_combinations = []
        scored_combinations = combos

        for i in range(board_size):
            for j in range(board_size - 3 + 1):
                point_combinations.append([i * board_size + k for k in range(j, j + 3)])

        for i in range(board_size):
            for j in range(board_size - 3 + 1):
                point_combinations.append([k * board_size + i for k in range(j, j + 3)])

        for i in range(board_size - 3 + 1):
            for j in range(board_size - 3 + 1):
                point_combinations.append([((i + k) * board_size + (j + k)) for k in range(3)])

        for i in range(board_size - 3 + 1):
            for j in range(3 - 1, board_size):
                point_combinations.append([((i + k) * board_size + (j - k)) for k in range(3)])

        for combo in point_combinations:
            if combo in scored_combinations:
                continue

            if all(board[pos] == 'X' for pos in combo):
                x_points += 1
                save_points(session_id, x_points=x_points, combos=[combo]) 
                logging.debug(f"Session {session_id}: Add x_point: {x_points}")
            elif all(board[pos] == 'O' for pos in combo):
                o_points += 1
                save_points(session_id, o_points=o_points, combos=[combo])
                logging.debug(f"Session {session_id}: Add o_points: {o_points}")

        if all(cell != " " for cell in board):
            if x_points > o_points:
                return "X wins by points"
            elif o_points > x_points:
                return "O wins by points"
            else:
                return "draw"

    return None

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
