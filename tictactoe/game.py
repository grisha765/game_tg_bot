from tictactoe.board import update_ttt_board, board_states, send_ttt_board
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def clear_ttt_session(session_id, sessions, selected_squares, available_session_ids):
    if session_id in sessions:
        del sessions[session_id]
    
    if session_id in selected_squares:
        del selected_squares[session_id]
    
    available_session_ids.append(session_id)
    logging.debug(f"Session {session_id} expired and was removed.")

def check_winner(board, board_size=3):
    if board_size == 3:
        win_length = 3
    elif board_size in [5, 7]:
        win_length = 4
    else:
        win_length = board_size
    
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

    if all(cell != " " for cell in board):
        return "draw"

    return None

async def move_ttt(client, callback_query, session, position: int, session_id: int, sessions, selected_squares, available_session_ids, get_translation):
    user = callback_query.from_user

    if session["next_move"] == "X" and user.id != session["x"]["id"]:
        await callback_query.answer(get_translation(session["lang"], "x_turn"))
        return
    elif session["next_move"] == "O" and user.id != session["o"]["id"]:
        await callback_query.answer(get_translation(session["lang"], "o_turn"))
        return
    player_symbol = session["next_move"]
    logging.debug(f"User {user.id}: Select {position}")
    move_successful = await update_ttt_board(session_id, position, player_symbol)
    if not move_successful:
        await callback_query.answer(get_translation(session["lang"], "occupied"))
        return
    
    board = board_states[session_id]
    board_size = session.get("board_size", 3)
    winner = check_winner(board, board_size=board_size)
    logging.debug(f"Session {session_id}: Check winner: {winner}")
    
    if winner == "X":
        winner_name = session["x"]["name"]
        await client.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=session["message_id"],
            text=f"@{winner_name} ({get_translation(session["lang"], "x").lower()}) {get_translation(session["lang"], "win")}!"
        )
        await clear_ttt_session(session_id, sessions, selected_squares, available_session_ids)
        
    elif winner == "O":
        winner_name = session["o"]["name"]
        await client.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=session["message_id"],
            text=f"@{winner_name} ({get_translation(session["lang"], "o").lower()}) {get_translation(session["lang"], "win")}!"
        )
        await clear_ttt_session(session_id, sessions, selected_squares, available_session_ids)
        
    elif winner == "draw":
        await client.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=session["message_id"],
            text=f"{get_translation(session["lang"], "complete")}: {get_translation(session["lang"], "draw")}!"
        )
        await clear_ttt_session(session_id, sessions, selected_squares, available_session_ids)
        
    else:
        session["next_move"] = "O" if player_symbol == "X" else "X"
        next_player = "🔴" if session["next_move"] == "O" else "❌"
        await send_ttt_board(session_id, client, session["message_id"], session["chat_id"], next_player, session, get_translation)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
