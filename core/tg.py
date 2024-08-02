import asyncio
from pyrogram import Client, filters
from config.config import Config
from casino.spin import spin_func
from casino.point import check_wins, top_command
from casino.emoji import set_emoji_command, get_emoji_command, del_emoji_command
from core.trans import get_translation
from chesse.invite import chess_start, join_black, remove_expired_session
from chesse.game import move
from config import logging_config
logging = logging_config.setup_logging(__name__)

app = Client("bot", api_id=Config.tg_id, api_hash=Config.tg_hash, bot_token=Config.tg_token)

@app.on_message(filters.command("help"))
async def hanlde_help(_, message):
    user_language = message.from_user.language_code
    logging.debug(f"{message.from_user.id}: {user_language}")
    text = get_translation(user_language, "help")
    await message.reply_text(text)

@app.on_message(filters.text & filters.command("spin", prefixes="/") & filters.group)
async def handle_spin(_, message):
    await spin_func(message, get_translation)

@app.on_message(filters.text & filters.command("wins", prefixes="/"))
async def handle_wins(_, message):
    await check_wins(message, get_translation)

@app.on_message(filters.text & filters.command("top", prefixes="/") & filters.group)
async def handle_top(client, message):
    await top_command(client, message, get_translation)

@app.on_message(filters.text & filters.command("set", prefixes="/") & filters.group)
async def handle_set(_, message):
    await set_emoji_command(message, get_translation)

@app.on_message(filters.text & filters.command("get", prefixes="/") & filters.group)
async def handle_get(_, message):
    await get_emoji_command(message, get_translation)

@app.on_message(filters.text & filters.command("del", prefixes="/") & filters.group)
async def handle_del(_, message):
    await del_emoji_command(message, get_translation)

sessions = {}
selected_squares = {}
available_session_ids = []

@app.on_message(filters.text & filters.command("chess", prefixes="/") & filters.group)
async def handle_start(client, message):
    if available_session_ids:
        session_id = available_session_ids.pop(0)
    else:
        session_id = len(sessions) + 1
    sessions[session_id] = {
        "white": {"id": None, "name": None},
        "black": {"id": None, "name": None},
        "message_id": None,
        "chat_id": message.chat.id
    }
    selected_squares[session_id] = None
    sessions[session_id]["white"]["id"], sessions[session_id]["white"]["name"], message_id = await chess_start(session_id, sessions, message)
    sessions[session_id]["message_id"] = message_id
    asyncio.create_task(remove_expired_session(session_id, sessions, selected_squares, available_session_ids, client))

@app.on_callback_query(filters.regex(r"join_black_(\d+)"))
async def handle_join(client, callback_query):
    session_id = int(callback_query.data.split('_')[-1])
    await join_black(session_id, sessions, client, callback_query)

@app.on_callback_query(filters.regex(r"^(\d+)_([a-h][1-8])$"))
async def handle_chess_move(client, callback_query):
    session_id, position = callback_query.data.split('_')
    session_id = int(session_id)
    selected_squares[session_id] = await move(client, callback_query, sessions[session_id], selected_squares[session_id])

async def start_bot():
    logging.info("Launching the bot...")
    await app.start()

async def stop_bot():
    logging.info("Stopping the bot...")
    await app.stop()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
