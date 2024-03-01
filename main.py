from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import random
import time
from argparse import ArgumentParser
import asyncio
import re
import json

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
active_spins = {}
random_spins_info = {}
wins_database = "wins.json"

symbols = ['🍒', '🍋', '🍏', '🍆']
phrases = ['Вишня! Поздравляю!', 'Лови лимон!', 'Яблоко база.', 'БАКЛАЖАН! У вас ДЖЕКПОТ! Вставьте его поглубже...', 'Поздравляем! Вы выиграли!', 'Увы, вы проиграли. Попробуйте ещё раз!']

filter_words = ["казино", "спин", "казик", "слот", "рулетк", "став", "джекпот", "азарт", "барабан", "выигрыш", "автомат", "побед", "перемо"]
filter_regex = re.compile(r'\b(?:' + '|'.join(filter_words) + r')(?:[а-я]*\b)', flags=re.IGNORECASE)

def load_wins_database():
    try:
        with open(wins_database, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_wins_database(data):
    with open(wins_database, 'w') as file:
        json.dump(data, file)

@app.on_message(filters.regex(filter_regex))
async def spin(_, message):
    current_time = time.time()
    user_id = message.from_user.id

    if user_id in active_spins:
        try:
            msg_wait = await message.reply_text("Вы уже вращаете барабан. Подождите, пока текущее вращение завершится.")
        except:
            del active_spins[user_id]
            return
        return
    active_spins[user_id] = True

    if user_id in last_command_usage and current_time - last_command_usage[user_id] < (10 + random_spins_info[user_id]):
        wait_time = int((10 + random_spins_info[user_id]) - (current_time - last_command_usage[user_id]))
        try:
            msg_wait = await message.reply_text(f"Пожалуйста, подождите {wait_time} секунд перед повторным прокрутом.")
        except:
            del active_spins[user_id]
            return
        del active_spins[user_id]
        return
    last_command_usage[user_id] = current_time

    prev_spin_display = None
    try:
        msg = await message.reply_text("Вращение барабанов...")
    except:
        del active_spins[user_id]
        return
    await asyncio.sleep(1)
    try:
        random_spins = random.randint(4, 8)
        random_spins_info[user_id] = random_spins
        for _ in range(random_spins):
            spin_display = prev_spin_display
            while spin_display == prev_spin_display:
                spin_display = [random.choice(symbols) for _ in range(3)]
            prev_spin_display = spin_display
            await msg.edit_text("🎰 "+' - '.join(spin_display)+" 🎰")
            await asyncio.sleep(0.1)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await msg.edit_text("🎰 "+"⛔️ - ⛔️ - ⛔️"+" 🎰"+"\n"+"Автомат заклинило! Повторите ещё раз!")
        del active_spins[user_id]
        return

    del active_spins[user_id]
    result = [random.choice(symbols) for _ in range(3)]
    if len(set(result)) == 1:
        if result[0] == symbols[0]: #вишня
            await asyncio.sleep(0.1)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+phrases[0])
            update_wins(user_id)
            return
        if result[0] == symbols[1]: #лимон
            await asyncio.sleep(0.1)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+phrases[1])
            update_wins(user_id)
            return
        if result[0] == symbols[2]: #яблоко
            await asyncio.sleep(0.1)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+phrases[2])
            update_wins(user_id)
            return
        if result[0] == symbols[3]: #баклажан
            await asyncio.sleep(0.1)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+phrases[3])
            update_wins(user_id)
            return
        else:
            await asyncio.sleep(0.1) #победа
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+phrases[4])
            update_wins(user_id)
            return
    else:
        await asyncio.sleep(0.1) #проигрыш
        await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+phrases[5])

def update_wins(user_id):
    wins_data = load_wins_database()
    if str(user_id) in wins_data:
        wins_data[str(user_id)] += 1
    else:
        wins_data[str(user_id)] = 1
    save_wins_database(wins_data)

@app.on_message(filters.command("wins"))
async def check_wins(_, message):
    user_id = message.from_user.id
    wins_data = load_wins_database()
    if str(user_id) in wins_data:
        wins_count = wins_data[str(user_id)]
        await message.reply_text(f"Ваши победы: {wins_count}")
    else:
        await message.reply_text("У вас пока нет побед.")

app.run()
