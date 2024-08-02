import chess
from chesse.board import boards, send_chessboard
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def move_chess(client, callback_query, session, selected_square):
    user_id = callback_query.from_user.id
    session_id, position = callback_query.data.split('_')
    session_id = int(session_id)
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id

    board = boards[session_id]

    if (board.turn == chess.WHITE and user_id == session["white"]["id"]) or (board.turn == chess.BLACK and user_id == session["black"]["id"]):
        if selected_square:
            move = chess.Move.from_uci(selected_square + position)
            if move in board.legal_moves:
                board.push(move)
                selected_square = None
                await send_chessboard(session_id, session, client, chat_id, message_id=message_id)
                if board.is_checkmate():
                    await client.edit_message_text(chat_id, message_id, text="Мат!")
                    logging.debug(f"Chat {chat_id}: mate!")
                elif board.is_stalemate():
                    logging.debug(f"Chat {chat_id}: stalemate!")
            else:
                await callback_query.answer(f"Неправильный ход {selected_square + position}. Попробуйте еще раз.")
                selected_square = None
        else:
            selected_square = position
            await callback_query.answer()
            logging.debug(f"User {user_id}: Select {position}")
    else:
        await callback_query.answer("Сейчас не ваш ход")

    return selected_square

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
