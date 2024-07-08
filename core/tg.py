from pyrogram import Client, filters
from config.config import Config
from casino.spin import spin_func
from casino.point import check_wins, top_command
from casino.emoji import set_emoji_command, get_emoji_command
from core.trans import get_translation
from config import logging_config
logging = logging_config.setup_logging(__name__)

app = Client("bot", api_id=Config.tg_id, api_hash=Config.tg_hash, bot_token=Config.tg_token)

@app.on_message(filters.command("help"))
async def hanlde_help(_, message):
    user_language = message.from_user.language_code
    logging.debug(f"{message.from_user.id}: {user_language}")
    text = get_translation(user_language, "help")
    await message.reply_text(text)

@app.on_message(filters.text & filters.command("spin", prefixes="/"))
async def handle_spin(_, message):
    await spin_func(message)

@app.on_message(filters.text & filters.command("wins", prefixes="/"))
async def handle_wins(_, message):
    await check_wins(message)

@app.on_message(filters.text & filters.command("top", prefixes="/"))
async def handle_top(client, message):
    await top_command(client, message)

@app.on_message(filters.text & filters.command("set", prefixes="/"))
async def handle_set(_, message):
    await set_emoji_command(message)

@app.on_message(filters.text & filters.command("get", prefixes="/"))
async def handle_get(_, message):
    await get_emoji_command(message)

async def start_bot():
    logging.info("Launching the bot...")
    await app.start()

async def stop_bot():
    logging.info("Stopping the bot...")
    await app.stop()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
