from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

board_states = {}

def initialize_ttt_board(session_id, board_size=3):
    board_states[session_id] = [" " for _ in range(board_size * board_size)]

async def send_ttt_board(session_id, client, message_id, chat_id, current_player, session, get_translation):
    board = board_states[session_id]
    board_size = session.get("board_size", 3)
    
    buttons = []
    for i in range(board_size * board_size):
        symbol = "❌" if board[i] == "X" else "🔴" if board[i] == "O" else " "
        buttons.append(InlineKeyboardButton(symbol, callback_data=f"{session_id}_{i}"))
    
    keyboard = InlineKeyboardMarkup([buttons[i:i+board_size] for i in range(0, len(buttons), board_size)])
    
    x_player = f"@{session['x']['name']}" + (" <==" if current_player == "❌" else "")
    o_player = f"@{session['o']['name']}" + (" <==" if current_player == "🔴" else "")
    
    await client.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"{get_translation(session['lang'], 'x')}: {x_player}\n{get_translation(session['lang'], 'o')}: {o_player}\n\n",
        reply_markup=keyboard
    )

async def update_ttt_board(session_id, position, symbol):
    board = board_states[session_id]
    if board[position] == " ":
        board[position] = symbol
        return True
    return False

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
