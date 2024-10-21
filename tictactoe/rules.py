def check_winner(board, board_size=3, game_mode=0):
    if board_size == 3:
        win_length = 3
    elif board_size in [5, 7]:
        win_length = 4
    else:
        win_length = board_size

    if game_mode == 0:
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

        for combo in winning_combinations:
            if all(board[pos] == board[combo[0]] and board[pos] != " " for pos in combo):
                return board[combo[0]]

    elif game_mode == 1:
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

    if all(cell != " " for cell in board):
        return "draw"

    return None
