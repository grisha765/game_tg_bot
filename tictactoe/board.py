from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

board_states = {}

def initialize_ttt_board(session_id, board_size=3):
    board_states[session_id] = [" " for _ in range(board_size * board_size)]

def del_ttt_board(session_id):
    if session_id in board_states:
        del board_states[session_id]

async def send_ttt_board(session_id, client, session, get_translation, current_player=None, winner=None, winning_combo=None):
    board = board_states[session_id]
    board_size = session["board_size"]
    
    buttons = []
    for i in range(board_size * board_size):
        symbol = "❌" if board[i] == "X" else "🔴" if board[i] == "O" else " "
        if winner and winning_combo and i in winning_combo:
            symbol = "🟢" if winner == "O" else "❎"
        buttons.append(InlineKeyboardButton(symbol, callback_data=f"{session_id}_{i}"))
    
    keyboard = InlineKeyboardMarkup([buttons[i:i+board_size] for i in range(0, len(buttons), board_size)])
    
    if current_player is not None:
        x_player = f"@{session['x']['name']}" + (" <==" if current_player == "❌" else "")
        o_player = f"@{session['o']['name']}" + (" <==" if current_player == "🔴" else "")
    else:
        if winner == "D":
            x_player = f"@{session['x']['name']} <== {get_translation(session['lang'], 'draw')}"
            o_player = f"@{session['o']['name']} <== {get_translation(session['lang'], 'draw')}"
        elif winner is not None and "P" in winner:
            x_player = f"@{session['x']['name']}" + (f" <== {get_translation(session['lang'], 'win')}" if winner == "X_P" else "")
            o_player = f"@{session['o']['name']}" + (f" <== {get_translation(session['lang'], 'win')}" if winner == "O_P" else "")
        else:
            x_player = f"@{session['x']['name']}" + (f" <== {get_translation(session['lang'], 'win')}" if winner == "X" else "")
            o_player = f"@{session['o']['name']}" + (f" <== {get_translation(session['lang'], 'win')}" if winner == "O" else "")


    x_points = session["x_points"] if session["game_mode"] == 2 else ""
    o_points = session["o_points"] if session["game_mode"] == 2 else ""

    x_display = f"{get_translation(session['lang'], 'x')} - {x_points}: {x_player}" if session["game_mode"] == 2 else f"{get_translation(session['lang'], 'x')}: {x_player}"
    o_display = f"{get_translation(session['lang'], 'o')} - {o_points}: {o_player}" if session["game_mode"] == 2 else f"{get_translation(session['lang'], 'o')}: {o_player}"
    if session["chat_id"] == None:
        await client.edit_inline_text(
            inline_message_id=session["message_id"],
            text=f"{x_display}\n{o_display}\n\n",
            reply_markup=keyboard
        )
    else:
        await client.edit_message_text(
            chat_id=session["chat_id"],
            message_id=session["message_id"],
            text=f"{x_display}\n{o_display}\n\n",
            reply_markup=keyboard
        )

async def update_ttt_board(session_id, session, position, symbol, callback_query, get_translation):
    board = board_states.get(session_id)
    if board == None:
        await callback_query.answer(get_translation(session['lang'], 'complete'))
    else:
        if board[position] == " ":
            board[position] = symbol
            return True
        return False

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
