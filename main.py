from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import random
import time
from argparse import ArgumentParser
import asyncio
import re

parser = ArgumentParser(description='Telegram-бот с аргументом токена и потоками процессора.')
parser.add_argument('-t', '--token', type=str, help='Токен Telegram-бота')
args = parser.parse_args()
if not args.token:
    parser.error('Аргумент токена является обязательным. (-t TOKEN или --token TOKEN), --help для дополнительной информации.')
api_id = 1
api_hash = 'b6b154c3707471f5339bd661645ed3d6'
bot_token = args.token
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

last_command_usage = {}
rangecount = 0.1
symbols = ['🍒', '🍋', '🍏', '🍆']
filter_words = ["казино", "спин", "казик", "слот", "рулетк", "став", "джекпот", "азарт", "барабан", "выигрыш", "автомат", "побед", "перемо"]
filter_regex = re.compile(r'\b(?:' + '|'.join(filter_words) + r')(?:[а-я]*\b)', flags=re.IGNORECASE)

@app.on_message(filters.regex(filter_regex))
async def spin(_, message):
    global last_command_usage
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in last_command_usage and current_time - last_command_usage[user_id] < 10:
        wait_time = int(10 - (current_time - last_command_usage[user_id]))
        msg_wait = await message.reply_text(f"Пожалуйста, подождите {wait_time} секунд перед повторным прокрутом.")
        return
    last_command_usage[user_id] = current_time

    prev_spin_display = None
    msg = await message.reply_text("Вращение барабанов...")
    await asyncio.sleep(1)
    try:
        for _ in range(random.randint(4, 8)):
            spin_display = prev_spin_display
            while spin_display == prev_spin_display:
                spin_display = [random.choice(symbols) for _ in range(3)]
            prev_spin_display = spin_display
            await msg.edit_text("🎰 "+' - '.join(spin_display)+" 🎰")
            await asyncio.sleep(rangecount)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await msg.edit_text("🎰 "+"⛔️ - ⛔️ - ⛔️"+" 🎰"+"\n"+"Автомат заклинило! Повторите ещё раз!")
        return

    result = [random.choice(symbols) for _ in range(3)]
    if len(set(result)) == 1:
        if result[0] == '🍆':
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+"БАКЛАЖАН! У вас ДЖЕКПОТ! Вставьте его поглубже...")
        else:
            await asyncio.sleep(rangecount)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+"Поздравляем! Вы выиграли!")
    else:
        await asyncio.sleep(rangecount)
        await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+"Увы, вы проиграли. Попробуйте ещё раз!")

app.run()
