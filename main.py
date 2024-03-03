from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from argparse import ArgumentParser
import random
import time
import asyncio
import re
import json
import unicodedata
import os
if not os.path.exists("bd"):
    os.makedirs("bd")

parser = ArgumentParser(description='Telegram-бот с аргументом токена и потоками процессора.')
parser.add_argument('-t', '--token', type=str, help='Токен Telegram-бота')
args = parser.parse_args()
if not args.token:
    parser.error('Аргумент токена является обязательным. (-t TOKEN или --token TOKEN), --help для дополнительной информации.')
api_id = 1
api_hash = 'b6b154c3707471f5339bd661645ed3d6'
bot_token = args.token
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

last_command_usage_user = {}
last_command_usage_group = {}
active_spins = {}
wins_database = os.path.join("bd", "wins.json")

filter_words = ["казино", "спин", "казик", "слот", "рулетк", "став", "джекпот", "азарт", "барабан", "выигрыш", "автомат", "побед", "перемо", "рол"]
filter_regex = re.compile(r'\b(?:' + '|'.join(filter_words) + r')(?:[а-я]*\b)', flags=re.IGNORECASE)

#помощь команда /help
@app.on_message(filters.command("help"))
def check_help(_, message):
    message.reply_text("Команды бота:\n/help - помощь.\n/wins - победы.\n/status - посмотреть заданные эмодзи и фразы.\n/set - задать кастомные эмодзи и победные фразы.\nПример: /set 🍒:Вишня. 🍋:Лимон. 🍏:Яблоко. 🍆:Баклажан.\nЭмодзи Telegram Premium не поддерживаются")

def load_wins_database():
    try:
        with open(wins_database, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_wins_database(data):
    with open(wins_database, 'w') as file:
        json.dump(data, file)

def update_wins(user_id):
    wins_data = load_wins_database()
    if str(user_id) in wins_data:
        wins_data[str(user_id)] += 1
    else:
        wins_data[str(user_id)] = 1
    save_wins_database(wins_data)

#победы команда /wins
@app.on_message(filters.command("wins"))
def check_wins(_, message):
    user_id = message.from_user.id
    wins_data = load_wins_database()
    if str(user_id) in wins_data:
        wins_count = wins_data[str(user_id)]
        message.reply_text(f"Ваши победы: {wins_count}")
    else:
        message.reply_text("У вас пока нет побед.")

def load_emoji_database(chat_id):
    try:
        with open(os.path.join("bd", f"data_{chat_id}.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"emoji": ['🍒', '🍋', '🍏', '🍆'], "phrases": ['Вишня! Поздравляю!', 'Лови лимон!', 'Яблоко база.', 'БАКЛАЖАН! У вас ДЖЕКПОТ! Вставьте его поглубже...']}

def save_emoji_database(data, chat_id):
    with open(os.path.join("bd", f"data_{chat_id}.json"), "w") as file:
        json.dump(data, file, indent=4)

def is_emoji(s):
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+"
    )
    return bool(emoji_pattern.fullmatch(s))

#задать кастомные эмодзи команда /set
@app.on_message(filters.command("set", prefixes="/") & filters.group)
def set_emoji(client, message):
    chat_id = message.chat.id
    current_time = time.time()

    if chat_id in last_command_usage_group and current_time - last_command_usage_group[chat_id] < 900:
        wait_time = int((900 - (current_time - last_command_usage_group[chat_id])) / 60)
        msg_wait = message.reply_text(f"Пожалуйста, подождите {wait_time} минут перед повторным использованием команды.")
        time.sleep(10)
        msg_wait.delete()
        return
    last_command_usage_group[chat_id] = current_time

    if len(message.command) >= 2:
        data = load_emoji_database(chat_id)
        emojis_with_phrases = []
        for i in range(1, len(message.command)):
            if ':' in message.command[i]:
                emojis_with_phrases.append(message.command[i])
            elif i != 0:
                emojis_with_phrases[-1] += ' ' + message.command[i]
        count_colons = 0
        for item in emojis_with_phrases:
            count_colons += item.count(':')
        if count_colons != 4:
            msg_error = message.reply("Ошибка: Нужно 4 эмодзи и победных фраз.")
            del last_command_usage_group[chat_id]
            time.sleep(10)
            msg_error.delete()
            return
        print(emojis_with_phrases)
        new_emojis = []
        new_phrases = []
        for emoji_with_phrase in emojis_with_phrases:
            emoji, phrase = emoji_with_phrase.split(":")
            if len(emoji) > 2:
                msg_error = message.reply("Ошибка: Допускается вводить только одно эмодзи для каждой победной фразы.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                msg_error.delete()
                return
            if len(phrase) < 1:
                msg_error = message.reply("Ошибка: Отсутствуют победные фразы.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                msg_error.delete()
                return
            if is_emoji(emoji):
                new_emojis.append(emoji)
                new_phrases.append(phrase)
            else:
                msg_error = message.reply("Ошибка: Недопустимый символ эмодзи.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                msg_error.delete()
                return

        data["emoji"] = new_emojis
        data["phrases"] = new_phrases
        save_emoji_database(data, chat_id)
        message.reply("Новые эмодзи и победные фразы установлены успешно!")
    else:
        msg_error = message.reply("Неверный формат команды. Используйте: /set Эмодзи1:Фраза1. Эмодзи2:Фраза2. Эмодзи3:Фраза3. Эмодзи4:Фраза4.")
        del last_command_usage_group[chat_id]
        time.sleep(10)
        msg_error.delete()

#посмотреть эмодзи группы команда /status
@app.on_message(filters.command("status", prefixes="/") & filters.group)
def status(client, message):
    chat_id = message.chat.id
    data = load_emoji_database(chat_id)
    status_text = "Заданные эмодзи и фразы в этой группе:\n"
    for emoji, phrase in zip(data["emoji"], data["phrases"]):
        status_text += f"{emoji}: {phrase}\n"
    message.reply(status_text)

#игра
@app.on_message(filters.regex(filter_regex) & filters.group)
async def spin(_, message):
    chat_id = message.chat.id
    data = load_emoji_database(chat_id)
    current_time = time.time()
    user_id = message.from_user.id

    if user_id in active_spins:
        try:
            msg_wait = await message.reply_text("Вы уже вращаете барабан. Подождите, пока текущее вращение завершится.")
            await asyncio.sleep(10)
            await msg_wait.delete()
        except:
            del active_spins[user_id]
            return
        return
    active_spins[user_id] = True

    if user_id in last_command_usage_user and current_time - last_command_usage_user[user_id] < 10:
        wait_time = int(10 - (current_time - last_command_usage_user[user_id]))
        try:
            msg_wait = await message.reply_text(f"Пожалуйста, подождите {wait_time} секунд перед повторным прокрутом.")
            del active_spins[user_id]
            await asyncio.sleep(10)
            await msg_wait.delete()
        except:
            del active_spins[user_id]
            return
        return
    last_command_usage_user[user_id] = current_time

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
        if result[0] == data["emoji"][0]: #эмодзи1
            await asyncio.sleep(0.5)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+data["phrases"][0])
            update_wins(user_id)
            return
        if result[0] == data["emoji"][1]: #эмодзи2
            await asyncio.sleep(0.5)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+data["phrases"][1])
            update_wins(user_id)
            return
        if result[0] == data["emoji"][2]: #эмодзи3
            await asyncio.sleep(0.5)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+data["phrases"][2])
            update_wins(user_id)
            return
        if result[0] == data["emoji"][3]: #эмодзи4
            await asyncio.sleep(0.5)
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+data["phrases"][3])
            update_wins(user_id)
            return
        else:
            await asyncio.sleep(0.5) #победа
            await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+'Поздравляем! Вы выиграли!')
            update_wins(user_id)
            return
    else:
        await asyncio.sleep(0.5) #проигрыш
        await msg.edit_text("🎰 "+' - '.join(result)+" 🎰"+"\n"+'Увы, вы проиграли. Попробуйте ещё раз!')

app.run()
