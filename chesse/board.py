import chess
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import logging_config
logging = logging_config.setup_logging(__name__)

boards = {}

PIECE_SYMBOLS = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 
    'white': '⬜️', 'black': '⬛️'
}

def initialize_board(session_id):
    boards[session_id] = chess.Board()

def generate_chessboard(session_id, chat_id):
    logging.debug(f"Chat ({chat_id}): Generate board for session {session_id}.")
    board_keyboard = []
    board = boards[session_id]
    for row in range(8):
        board_row = []
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                symbol = PIECE_SYMBOLS[piece.symbol()]
            else:
                if (row + col) % 2 == 0:
                    symbol = PIECE_SYMBOLS['white']
                else:
                    symbol = PIECE_SYMBOLS['black']
            callback_data = f"{session_id}_{chess.square_name(chess.square(col, 7 - row))}"
            button = InlineKeyboardButton(text=symbol, callback_data=callback_data)
            board_row.append(button)
        board_keyboard.append(board_row)
    return board_keyboard

async def send_chessboard(session_id, session, client, chat_id, message_id=None):
    chessboard = generate_chessboard(session_id, chat_id)
    white_display = f"@{session['white']['name']} <==" if boards[session_id].turn == chess.WHITE else f"@{session['white']['name']}"
    black_display = f"@{session['black']['name']} <==" if boards[session_id].turn == chess.BLACK else f"@{session['black']['name']}"
    text = f"Шахматная доска: {session_id}\nЧерные: {black_display}\nБелые: {white_display}"
    reply_markup = InlineKeyboardMarkup(chessboard)
    if message_id:
        try:
            return await client.edit_message_text(chat_id, message_id, text=text, reply_markup=reply_markup)
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                return None
            else:
                raise e
    else:
        return await client.send_message(chat_id, text, reply_markup=reply_markup)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
