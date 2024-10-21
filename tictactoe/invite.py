from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tictactoe.board import send_ttt_board, initialize_ttt_board
from config import logging_config
import asyncio

logging = logging_config.setup_logging(__name__)

async def ttt_start(session_id, sessions, message, get_translation):
    user = message.from_user
    sessions[session_id]["x"]["id"] = user.id
    sessions[session_id]["x"]["name"] = user.username if user.username else user.first_name
    logging.debug(f"Session {session_id}: Start game: {sessions[session_id]['x']['name']}")
    initialize_ttt_board(session_id)
    sessions[session_id]["next_move"] = "X"
    join_button = InlineKeyboardButton(get_translation(sessions[session_id]["lang"], "join"), callback_data=f"join_o_{session_id}")
    reply_markup = InlineKeyboardMarkup([[join_button]])
    msg = await message.reply_text(
        f"{get_translation(sessions[session_id]["lang"], "session_id")}: {session_id}\n{get_translation(sessions[session_id]["lang"], "x")}: @{sessions[session_id]['x']['name']}\n{get_translation(sessions[session_id]["lang"], "wait")}",
        reply_markup=reply_markup
    )
    sessions[session_id]["message_id"] = msg.id
    return sessions[session_id]["x"]["id"], sessions[session_id]["x"]["name"], msg.id

async def join_ttt_o(session_id, sessions, client, callback_query, get_translation):
    user = callback_query.from_user

    if user.id == sessions[session_id]["x"]["id"]:
            await callback_query.answer(
                get_translation(sessions[session_id]["lang"], "incorrect_join0") +
                get_translation(sessions[session_id]["lang"], "x").lower() +
                get_translation(sessions[session_id]["lang"], "incorrect_join1") +
                get_translation(sessions[session_id]["lang"], "o").lower()
            )
    elif not sessions[session_id]["o"]["id"]:
        sessions[session_id]["o"]["id"] = user.id
        sessions[session_id]["o"]["name"] = user.username if user.username else user.first_name
        logging.debug(f"Session {session_id}: Join game: {sessions[session_id]['o']['name']}")
        await callback_query.message.edit_text(
            f"{get_translation(sessions[session_id]["lang"], "x")}: @{sessions[session_id]['x']['name']}\n{get_translation(sessions[session_id]["lang"], "o")}: @{sessions[session_id]['o']['name']}\n{get_translation(sessions[session_id]["lang"], "start_game")}"
        )
        await send_ttt_board(session_id, client, callback_query.message.id, callback_query.message.chat.id, "❌", sessions[session_id], get_translation)
    else:
        await callback_query.answer(get_translation(sessions[session_id]["lang"], "game_started"))

async def remove_expired_ttt_session(session_id, sessions, selected_squares, available_session_ids, client):
    await asyncio.sleep(300)
    if not sessions[session_id]["o"]["id"]:
        chat_id = sessions[session_id]["chat_id"]
        message_id = sessions[session_id]["message_id"]
        await client.delete_messages(chat_id, message_id)
        del sessions[session_id]
        del selected_squares[session_id]
        available_session_ids.append(session_id)
        logging.debug(f"Session {session_id} expired and was removed.")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
