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

def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Строки
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Столбцы
        [0, 4, 8], [2, 4, 6]              # Диагонали
    ]
    
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] != " ":
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
    winner = check_winner(board)
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
