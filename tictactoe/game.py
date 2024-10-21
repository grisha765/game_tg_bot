from tictactoe.board import update_ttt_board, board_states, send_ttt_board
from tictactoe.rules import check_winner
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def clear_ttt_session(session_id, sessions, selected_squares, available_session_ids):
    if session_id in sessions:
        del sessions[session_id]
    
    if session_id in selected_squares:
        del selected_squares[session_id]
    
    available_session_ids.append(session_id)
    logging.debug(f"Session {session_id} expired and was removed.")

async def move_ttt(client, callback_query, session, position: int, session_id: int, sessions, selected_squares, available_session_ids, get_translation, save_points):
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
    game_mode = session.get("game_mode", 0)
    winner = check_winner(board, board_size=board_size, game_mode=game_mode, session_id=session_id, x_points=session["x_points"], o_points=session["o_points"], save_points=save_points, combos=session.get("combos", []))
    logging.debug(f"Session {session_id}: Check winner: {winner}")
    
    if winner == "X":
        winner_name = session["x"]["name"]
        await client.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=session["message_id"],
            text=f"@{winner_name} ({get_translation(session["lang"], "x").lower()}) {get_translation(session["lang"], "win")}!"
        )
        await clear_ttt_session(session_id, sessions, selected_squares, available_session_ids)

    elif winner == "X wins by points":
        winner_name = session["x"]["name"]
        await client.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=session["message_id"],
            text=f"@{winner_name} ({get_translation(session["lang"], "x").lower()}) {get_translation(session["lang"], "win_points")}: {session["x_points"]}!"
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

    elif winner == "O wins by points":
        winner_name = session["o"]["name"]
        await client.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=session["message_id"],
            text=f"@{winner_name} ({get_translation(session["lang"], "o").lower()}) {get_translation(session["lang"], "win_points")}: {session["o_points"]}!"
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
