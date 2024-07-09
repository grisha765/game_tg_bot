import asyncio
import random
from db.point import add_points, get_points, get_all_points
from db.emoji import get_emoji
from pyrogram.errors import FloodWait
from casino.antispam import antispam_user
from core.vars import active_spins

from config import logging_config
logging = logging_config.setup_logging(__name__)

async def spin_func(message, get_translation):
    user_language = message.from_user.language_code
    chat_id = message.chat.id
    data = await get_emoji(chat_id)
    user_id = message.from_user.id

    spam_check = await antispam_user(user_id, 60)

    if spam_check == "active_spin":
        try:
            msg_wait = await message.reply_text(get_translation(user_language, "active_spin"))
            await asyncio.sleep(10)
            await msg_wait.delete()
        except:
            del active_spins[user_id]
        return

    if isinstance(spam_check, int):
        try:
            msg_wait = await message.reply_text(f"{get_translation(user_language, "antispam")} {spam_check} {get_translation(user_language, "antispam_sec")}")
            await asyncio.sleep(10)
            await msg_wait.delete()
        except:
            del active_spins[user_id]
        return

    active_spins[user_id] = True

    prev_spin_display = None
    try:
        msg = await message.reply_text(get_translation(user_language, "start_spin"))
    except:
        del active_spins[user_id]
        return

    await asyncio.sleep(1)

    try:
        spins = 4
        for _ in range(spins):
            spin_display = prev_spin_display
            while spin_display == prev_spin_display:
                spin_display = [random.choice(data["emoji"]) for _ in range(3)]
            prev_spin_display = spin_display
            await msg.edit_text("🎰 "+' - '.join(spin_display)+" 🎰")
            await asyncio.sleep(0.5)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await msg.edit_text("🎰 "+"⛔️ - ⛔️ - ⛔️"+" 🎰"+"\n"+get_translation(user_language, "floodwait_spin"))
        del active_spins[user_id]
        return
    except:
        del active_spins[user_id]
        return

    del active_spins[user_id]
    result = [random.choice(data["emoji"]) for _ in range(3)]
    if len(set(result)) == 1:
        phrase_index = data["emoji"].index(result[0])
        await asyncio.sleep(0.5)
        await msg.edit_text(f"🎰 {' - '.join(result)} 🎰\n{data['phrases'][phrase_index]}")
        log_point = await add_points(user_id, 1)
        logging.debug(log_point)
        logging.debug(f"{user_id}: Points - {await get_points(user_id)}")
    else:
        await asyncio.sleep(0.5)
        await msg.edit_text(f"🎰 {' - '.join(result)} 🎰\n{get_translation(user_language, "loss_spin")}")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
