from tictactoe.board import update_ttt_board, board_states, send_ttt_board, del_ttt_board
from tictactoe.rules import check_winner
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def move_ttt(client, callback_query, session, position: int, session_id: int, get_translation, save_points):
    user = callback_query.from_user

    if session["next_move"] == "X" and user.id != session["x"]["id"]:
        await callback_query.answer(get_translation(session["lang"], "x_turn"))
        return
    elif session["next_move"] == "O" and user.id != session["o"]["id"]:
        await callback_query.answer(get_translation(session["lang"], "o_turn"))
        return
    elif session["next_move"] == "D":
        await callback_query.answer(get_translation(session['lang'], 'complete'))
        return

    player_symbol = session["next_move"]
    logging.debug(f"User {user.id}: Select {position}")
    move_successful = await update_ttt_board(session_id, session, position, player_symbol, callback_query, get_translation)
    if not move_successful:
        await callback_query.answer(get_translation(session["lang"], "occupied"))
        return
    
    board = board_states[session_id]
    board_size = session.get("board_size", 3)
    game_mode = session.get("game_mode", 0)
    winner, combo = check_winner(board, board_size=board_size, game_mode=game_mode, session_id=session_id, x_points=session["x_points"], o_points=session["o_points"], save_points=save_points, combos=session.get("combos", []))
    logging.debug(f"Session {session_id}: Check winner: {winner}")
    
    if winner == "X":
        await send_ttt_board(session_id, client, session, get_translation, winner="X", winning_combo=combo)
        del_ttt_board(session_id)
        session["next_move"] = "D"

    elif winner == "X wins by points":
        await send_ttt_board(session_id, client, session, get_translation, winner="X_P", winning_combo=combo)
        del_ttt_board(session_id)
        session["next_move"] = "D"
        
    elif winner == "O":
        await send_ttt_board(session_id, client, session, get_translation, winner="O", winning_combo=combo)
        del_ttt_board(session_id)
        session["next_move"] = "D"

    elif winner == "O wins by points":
        await send_ttt_board(session_id, client, session, get_translation, winner="O_P", winning_combo=combo)
        del_ttt_board(session_id)
        session["next_move"] = "D"
        
    elif winner == "draw":
        await send_ttt_board(session_id, client, session, get_translation, winner="D")
        del_ttt_board(session_id)
        session["next_move"] = "D"
        
    else:
        session["next_move"] = "O" if player_symbol == "X" else "X"
        next_player = "🔴" if session["next_move"] == "O" else "❌"
        logging.debug(f"Session {session_id}: next move {session["next_move"]}")
        await send_ttt_board(session_id, client, session, get_translation, next_player)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
