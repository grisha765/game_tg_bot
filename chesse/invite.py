from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from chesse.board import send_chessboard, initialize_board
from config import logging_config
import asyncio

logging = logging_config.setup_logging(__name__)

async def chess_start(session_id, sessions, message):
    user = message.from_user
    sessions[session_id]["white"]["id"] = user.id
    sessions[session_id]["white"]["name"] = user.username if user.username else user.first_name
    logging.debug(f"Start game: {sessions[session_id]['white']['name']}")
    initialize_board(session_id)
    join_button = InlineKeyboardButton("Присоединиться к игре за черных", callback_data=f"join_black_{session_id}")
    reply_markup = InlineKeyboardMarkup([[join_button]])
    msg = await message.reply_text(f"Шахматная доска: {session_id}\nБелые: @{sessions[session_id]['white']['name']}\nОжидание игрока за черных.", reply_markup=reply_markup)
    return sessions[session_id]["white"]["id"], sessions[session_id]["white"]["name"], msg.id

async def join_black(session_id, sessions, client, callback_query):
    user = callback_query.from_user
    logging.debug(f"Join game: {user.username}")
    if user.id == sessions[session_id]["white"]["id"]:
        await callback_query.answer("Вы не можете присоединиться к игре за черных, если вы уже играете за белых.")
    elif not sessions[session_id]["black"]["id"]:
        sessions[session_id]["black"]["id"] = user.id
        sessions[session_id]["black"]["name"] = user.username if user.username else user.first_name
        await callback_query.message.edit_text(f"Шахматная доска: {session_id}\nЧерные: @{sessions[session_id]['black']['name']}\nБелые: @{sessions[session_id]['white']['name']}\nИгра начинается.")
        await send_chessboard(session_id, sessions[session_id], client, callback_query.message.chat.id)
    else:
        await callback_query.answer("Игра уже началась.")

async def remove_expired_session(session_id, sessions, selected_squares, available_session_ids, client):
    await asyncio.sleep(300)
    if not sessions[session_id]["black"]["id"]:
        chat_id = sessions[session_id]["chat_id"]
        message_id = sessions[session_id]["message_id"]
        await client.delete_messages(chat_id, message_id)
        del sessions[session_id]
        del selected_squares[session_id]
        available_session_ids.append(session_id)
        logging.debug(f"Session {session_id} expired and was removed.")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

