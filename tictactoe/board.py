from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

board_states = {}

def initialize_ttt_board(session_id):
    board_states[session_id] = [" " for _ in range(9)]

async def send_ttt_board(session_id, client, message_id, chat_id, current_player, session):
    board = board_states[session_id]
    buttons = []
    for i in range(9):
        symbol = "❌" if board[i] == "X" else "🔴" if board[i] == "O" else " "
        buttons.append(InlineKeyboardButton(symbol, callback_data=f"{session_id}_{i}"))
    keyboard = InlineKeyboardMarkup([buttons[i:i+3] for i in range(0, 9, 3)])
    x_player = f"@{session['x']['name']}" + (" <==" if current_player == "❌" else "")
    o_player = f"@{session['o']['name']}" + (" <==" if current_player == "🔴" else "")
    await client.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Крестики: {x_player}\nНолики: {o_player}\n\n",
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
