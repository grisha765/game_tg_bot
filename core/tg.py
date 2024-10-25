import asyncio, random, uuid
from pyrogram import Client, filters
from config.config import Config
from casino.spin import spin_func
from casino.point import check_wins, top_command
from casino.emoji import set_emoji_command, get_emoji_command, del_emoji_command
from core.trans import get_translation
from chesse.invite import chess_start, join_chess_black, remove_expired_chess_session
from tictactoe.invite import ttt_start, remove_expired_ttt_session, join_ttt_o, update_buttons
from chesse.game import move_chess
from tictactoe.game import move_ttt
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
session_cleanup_tasks = {}
available_session_ids = []

@app.on_message(filters.text & filters.command("chess", prefixes="/") & filters.group)
async def handle_chess_start(client, message):
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
    asyncio.create_task(remove_expired_chess_session(session_id, sessions, selected_squares, available_session_ids, client))

@app.on_callback_query(filters.regex(r"join_black_(\d+)"))
async def handle_chess_join(client, callback_query):
    session_id = int(callback_query.data.split('_')[-1])
    await join_chess_black(session_id, sessions, client, callback_query)

@app.on_callback_query(filters.regex(r"^(\d+)_([a-h][1-8])$"))
async def handle_chess_move(client, callback_query):
    session_id, position = callback_query.data.split('_')
    session_id = int(session_id)
    selected_squares[session_id] = await move_chess(client, callback_query, sessions[session_id], selected_squares[session_id])

def gen_session(message, chat_id):
    session_id = uuid.uuid4().hex[:12]
    sessions[session_id] = {
        "x": {"id": None, "name": None},
        "o": {"id": None, "name": None},
        "next_move": random.choice(["X", "O"]),
        "x_points": 0,
        "o_points": 0,
        "combos": [],
        "message_id": None,
        "chat_id": chat_id,
        "board_size": 3,
        "game_mode": 0,
        "lang": message.from_user.language_code
    }
    selected_squares[session_id] = None
    return sessions, session_id

async def gen_remove_session(client, sessions, session_id):
    cleanup_task = asyncio.create_task(remove_expired_ttt_session(session_id, sessions, selected_squares, available_session_ids, client))
    session_cleanup_tasks[session_id] = cleanup_task
    logging.debug(f"Session {session_id}: Add cleanup Task {session_cleanup_tasks[session_id]}.")
    logging.debug(f"All cleanup tasks: {session_cleanup_tasks}")

@app.on_inline_query()
async def answer_inline(_, inline_query):
    sessions, session_id = gen_session(inline_query, None)
    sessions[session_id]["x"]["id"], sessions[session_id]["x"]["name"], results = await ttt_start(session_id, sessions, inline_query, get_translation)

    # await gen_remove_session(client, sessions, session_id)

    await inline_query.answer(results, cache_time=1)

@app.on_message(filters.text & filters.command("ttt", prefixes="/") & filters.group)
async def handle_ttt_start(client, message):
    sessions, session_id = gen_session(message, message.chat.id)
    sessions[session_id]["x"]["id"], sessions[session_id]["x"]["name"], message_id = await ttt_start(session_id, sessions, message, get_translation)
    sessions[session_id]["message_id"] = message_id

    # await gen_remove_session(client, sessions, session_id)

@app.on_callback_query(filters.regex(r"^board_size_(\d+)_([a-zA-Z0-9]+)$"))
async def handle_board_size_selection(client, callback_query):
    size = int(callback_query.data.split('_')[2])
    session_id = str(callback_query.data.split('_')[3])
    if sessions.get(session_id) == None:
        await callback_query.answer(get_translation(callback_query.from_user.language_code, 'complete'))
        return
    
    if sessions[session_id]["x"]["id"] != callback_query.from_user.id:
        await callback_query.answer(get_translation(sessions[session_id]["lang"], "unavailable"))
        return

    if sessions[session_id].get("board_size") == size:
        await callback_query.answer(f"{get_translation(sessions[session_id]["lang"], "size_already_selected")} {size}x{size}.")
        return

    if size == 3:
        sessions[session_id]["game_mode"] = 0
        logging.debug(f"Session {session_id}: selected board size {size}, mod is selected {sessions[session_id]["game_mode"]}")
    
    sessions[session_id]["board_size"] = size
    await update_buttons(client, session_id, sessions[session_id], callback_query, size, sessions[session_id]["game_mode"], get_translation)
    await callback_query.answer(f"{get_translation(sessions[session_id]["lang"], "select_size")}: {size}x{size}.")

@app.on_callback_query(filters.regex(r"^game_mode_(\d+)_([a-zA-Z0-9]+)$"))
async def handle_game_mode_selection(client, callback_query):
    mode = int(callback_query.data.split('_')[2])
    session_id = str(callback_query.data.split('_')[3])
    if sessions.get(session_id) == None:
        await callback_query.answer(get_translation(callback_query.from_user.language_code, 'complete'))
        return

    if sessions[session_id]["x"]["id"] != callback_query.from_user.id:
        await callback_query.answer(get_translation(sessions[session_id]["lang"], "unavailable"))
        return

    if sessions[session_id].get("game_mode") == mode:
        await callback_query.answer(get_translation(sessions[session_id]["lang"], "mode_already_selected"))
        return

    sessions[session_id]["game_mode"] = mode
    await update_buttons(client, session_id, sessions[session_id], callback_query, sessions[session_id]["board_size"], mode, get_translation)
    await callback_query.answer(f"{get_translation(sessions[session_id]["lang"], "select_mode")}: {get_translation(sessions[session_id]["lang"], f"mode_{mode}").lower()}")

def save_points(session_id, x_points=None, o_points=None, combos=None):
    if x_points != None:
        sessions[session_id]["x_points"] = x_points
    if o_points != None:
        sessions[session_id]["o_points"] = o_points
    if combos != None:
        sessions[session_id]["combos"].extend(combos)

@app.on_callback_query(filters.regex(r"join_o_([a-zA-Z0-9]+)"))
async def handle_ttt_join(client, callback_query):
    session_id = callback_query.data.split('_')[-1]
    await join_ttt_o(session_id, sessions, client, callback_query, get_translation, session_cleanup_tasks)

@app.on_callback_query(filters.regex(r"^([a-zA-Z0-9]+)_(\d+)$"))
async def handle_ttt_move(client, callback_query):
    session_id, position = callback_query.data.split('_')
    session_id = str(session_id)
    session = sessions.get(session_id)
    if session != None:
        await move_ttt(client, callback_query, sessions[session_id], int(position), session_id, get_translation, save_points)
    else:
        await callback_query.answer(get_translation(callback_query.from_user.language_code, 'complete'))

async def start_bot():
    logging.info("Launching the bot...")
    await app.start()

async def stop_bot():
    logging.info("Stopping the bot...")
    await app.stop()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
