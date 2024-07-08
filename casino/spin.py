import asyncio
import random
from db.point import add_points, get_points, get_all_points
from pyrogram.errors import FloodWait
from casino.antispam import antispam_user
from core.vars import active_spins

from config import logging_config
logging = logging_config.setup_logging(__name__)

async def spin_func(message):
    chat_id = message.chat.id
    data = {"emoji": ['🍒', '🍋', '🍏', '🍆'], "phrases": ['Вишня! Поздравляю!', 'Лови лимон!', 'Яблоко база.', 'БАКЛАЖАН! У вас ДЖЕКПОТ! Вставьте его поглубже...']}
    user_id = message.from_user.id

    spam_check = await antispam_user(user_id, 60)

    if spam_check == "active_spin":
        try:
            msg_wait = await message.reply_text("Вы уже вращаете барабан. Подождите, пока текущее вращение завершится.")
            await asyncio.sleep(10)
            await msg_wait.delete()
        except:
            del active_spins[user_id]
        return

    if isinstance(spam_check, int):
        try:
            msg_wait = await message.reply_text(f"Пожалуйста, подождите {spam_check} секунд перед повторным прокрутом.")
            await asyncio.sleep(10)
            await msg_wait.delete()
        except:
            del active_spins[user_id]
        return

    active_spins[user_id] = True

    prev_spin_display = None
    try:
        msg = await message.reply_text("Вращение барабанов...")
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
        await msg.edit_text("🎰 "+"⛔️ - ⛔️ - ⛔️"+" 🎰"+"\n"+"Автомат заклинило! Повторите ещё раз!")
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
        await msg.edit_text(f"🎰 {' - '.join(result)} 🎰\nУвы, вы проиграли. Попробуйте ещё раз!")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
