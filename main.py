from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from argparse import ArgumentParser
import random
import time
import asyncio
import re
import json
import unicodedata
import os
import tracemalloc
tracemalloc.start()
if not os.path.exists("bd"):
    os.makedirs("bd")

parser = ArgumentParser(description='Telegram-бот с аргументом токена')
parser.add_argument('-t', '--token', type=str, help='Токен Telegram-бота')
args = parser.parse_args()
if not args.token:
    parser.error('Аргумент токена является обязательным. (-t TOKEN или --token TOKEN), --help для дополнительной информации.')
api_id = 1
api_hash = 'b6b154c3707471f5339bd661645ed3d6'
bot_token = args.token
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# спины
last_command_usage_user = {}
last_command_usage_group = {}
active_spins = {}
wins_database = os.path.join("bd", "wins.json")

filter_words = ["казино", "спин", "казик", "слот", "рулетк", "ставка", "джекпот", "азарт", "барабан", "выигрыш", "автомат", "победа", "перемога", "рол"]

#помощь команда /help
@app.on_message(filters.command("help"))
async def check_help(_, message):
    await message.reply_text("Команды бота:\n/help - помощь.\n/spin - крутить барабан.\n/wins - победы.\n/top - топ победителей.\n/status - посмотреть заданные эмодзи и фразы.\n/set - задать кастомные эмодзи и победные фразы.\nПример: /set 🍒:Вишня. 🍋:Лимон. 🍏:Яблоко. 🍆:Баклажан.\nЭмодзи Telegram Premium не поддерживаются")

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
async def check_wins(_, message):
    user_id = message.from_user.id
    wins_data = load_wins_database()
    if str(user_id) in wins_data:
        wins_count = wins_data[str(user_id)]
        await message.reply_text(f"Ваши победы: {wins_count}")
    else:
        await message.reply_text("У вас пока нет побед.")

@app.on_message(filters.command("top") & filters.group)
async def top_command(client, message):
    wins_data = load_wins_database()
    sorted_data = sorted(wins_data.items(), key=lambda x: x[1], reverse=True)
    top_message = "Топ победителей:\n"
    top_count = 0
    for i, (user_id, victories) in enumerate(sorted_data, start=1):
        try:
            user = await client.get_users(user_id)
            if user.username:
                username = f"{user.username}"
            elif user.first_name and user.last_name:
                username = f"{user.first_name} {user.last_name}"
            elif user.first_name:
                username = user.first_name
            else:
                username = f"user{user_id}"
            top_count += 1
            top_message += f"{top_count}) {username}: {victories}\n"
        except Exception as e:
            continue

    await message.reply_text(top_message, disable_notification=True)

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
async def set_emoji(client, message):
    chat_id = message.chat.id
    current_time = time.time()

    if chat_id in last_command_usage_group and current_time - last_command_usage_group[chat_id] < 900:
        wait_time = int((900 - (current_time - last_command_usage_group[chat_id])) / 60)
        msg_wait = await message.reply_text(f"Пожалуйста, подождите {wait_time} минут перед повторным использованием команды.")
        time.sleep(10)
        await msg_wait.delete()
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
            msg_error = await message.reply("Ошибка: Нужно 4 эмодзи и победных фраз.")
            del last_command_usage_group[chat_id]
            time.sleep(10)
            await msg_error.delete()
            return
        emoji_set = set()
        for item in emojis_with_phrases:
            emoji, _ = item.split(":")
            if emoji in emoji_set:
                msg_error = await message.reply("Ошибка: Обнаружены повторяющиеся эмодзи.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                await msg_error.delete()
                return
            else:
                emoji_set.add(emoji)
        new_emojis = []
        new_phrases = []
        for emoji_with_phrase in emojis_with_phrases:
            emoji, phrase = emoji_with_phrase.split(":")
            if len(emoji) > 2:
                msg_error = await  message.reply("Ошибка: Допускается вводить только одно эмодзи для каждой победной фразы.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                await msg_error.delete()
                return
            if len(phrase) < 1:
                msg_error = await message.reply("Ошибка: Отсутствуют победные фразы.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                await msg_error.delete()
                return
            if is_emoji(emoji):
                new_emojis.append(emoji)
                new_phrases.append(phrase)
            else:
                msg_error = await message.reply("Ошибка: Недопустимый символ эмодзи.")
                del last_command_usage_group[chat_id]
                time.sleep(10)
                await msg_error.delete()
                return
        data["emoji"] = new_emojis
        data["phrases"] = new_phrases
        save_emoji_database(data, chat_id)
        await message.reply("Новые эмодзи и победные фразы установлены успешно!")
    else:
        msg_error = await message.reply("Неверный формат команды. Используйте: /set Эмодзи1:Фраза1. Эмодзи2:Фраза2. Эмодзи3:Фраза3. Эмодзи4:Фраза4.")
        del last_command_usage_group[chat_id]
        time.sleep(10)
        await msg_error.delete()

#посмотреть эмодзи группы команда /status
@app.on_message(filters.command("status", prefixes="/") & filters.group)
async def status(client, message):
    chat_id = message.chat.id
    data = load_emoji_database(chat_id)
    status_text = "Заданные эмодзи и фразы в этой группе:\n"
    for emoji, phrase in zip(data["emoji"], data["phrases"]):
        status_text += f"{emoji}: {phrase}\n"
    await message.reply(status_text)

#игра #filters.create(lambda _, __, m: len(m.text.lower().split()) == 1 and m.text.lower().split()[0] in filter_words)
@app.on_message(filters.text & filters.group & filters.command("spin", prefixes="/"))
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

    if user_id in last_command_usage_user and current_time - last_command_usage_user[user_id] < 60:
        wait_time = int(60 - (current_time - last_command_usage_user[user_id]))
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

# Дуэли
player1 = {}
player2 = {}

def load_players_hp_database(filename):
    try:
        with open(os.path.join(filename), 'r') as file:
            data = json.load(file)
            return {int(key): int(value) for key, value in data.items()}
    except FileNotFoundError:
        return {}

def save_players_hp_database(filename, data):
    with open(os.path.join(filename), 'w') as file:
        json.dump(data, file, separators=(',', ':'))

def update_players_hp_database(filename, user_id, player_hp):
    hp_data = load_players_hp_database(filename)
    hp_data[user_id] = player_hp
    save_players_hp_database(filename, hp_data)
hp_file = 'bd/players_hp.json'
players_hp = load_players_hp_database(hp_file)

accepted_challenges = {}
active_players = {}
# Обработчик команды /start
@app.on_message(filters.command(["start"]))
async def start_command(client, message):
    chat_id = message.chat.id
    message_id = message.id
    user = message.from_user #тот кто написал /start
    replied_user = message.reply_to_message.from_user #тот кому ответили

    player1[message_id] = replied_user.id
    player2[message_id] = user.id

    if player1 == player2:
        msg_error = await client.send_message(
            chat_id=chat_id,
            text=f"Ошибка: Нельзя вызвать на поединок самого себя.",
            reply_to_message_id=message.id
        )
        await asyncio.sleep(10)
        await msg_error.delete()
        return
    if active_players.get(player1.get(message_id)) or active_players.get(player2.get(message_id)):
        msg_error = await client.send_message(
            chat_id=chat_id,
            text=f"Ошибка: Поединок уже идёт.",
            reply_to_message_id=message.id
        )
        await asyncio.sleep(10)
        await msg_error.delete()
        return

    active_players[player1.get(message_id)] = True
    active_players[player2.get(message_id)] = True

    if player1[message_id] not in players_hp:
        players_hp[player1[message_id]] = 100
    if player2[message_id] not in players_hp:
        players_hp[player2[message_id]] = 100

    player1_getuser = await app.get_users(player1.get(message_id))
    player2_getuser = await app.get_users(player2.get(message_id))

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Принять вызов!", callback_data="start")]])
    msg = await client.send_message(
        chat_id=chat_id,
        text=f"Вы вызвали @{player1_getuser.username} на поединок!\nОппоненту нужно принять вызов в течении 10 секунд иначе он будет отклонен.",
        reply_to_message_id=message.id,
        reply_markup=reply_markup
    )

    await asyncio.sleep(10)
    if accepted_challenges.get(message_id) == True:
        pass
    else:
        await msg.delete()
        active_players.clear()
# Обработчик нажатия кнопки "Принять вызов!"
@app.on_callback_query(filters.regex("start"))
async def attack_callback(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id

    Player1 = player1.get(message_id - 1)
    Player2 = player2.get(message_id - 1)
    Player1_hp = players_hp.get(Player1)
    Player2_hp = players_hp.get(Player2)

    player1_getuser = await app.get_users(player1.get(message_id - 1))
    player2_getuser = await app.get_users(player2.get(message_id - 1))

    if user_id == Player1:
        accepted_challenges[message_id - 1] = True
        await client.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Атаковать пользователя {player2_getuser.username or player2_getuser.first_name}...", callback_data="attack")]
        ])
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"{player1_getuser.username or player1_getuser.first_name} (HP: {Player1_hp}) ⚔️ {player2_getuser.username or player2_getuser.first_name} (HP: {Player2_hp})\nПользователь {player1_getuser.username or player1_getuser.first_name} принял вызов пользователя {player2_getuser.username or player2_getuser.first_name}",
            reply_markup=reply_markup
        )

    else:
        await callback_query.answer(text=f"Это только для {player1_getuser.username or player1_getuser.first_name}.")

    await callback_query.answer()

@app.on_callback_query(filters.regex("attack"))
async def battle_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id
    user_id = callback_query.from_user.id

    attacking_player = player1.get(message_id - 1)
    defending_player = player2.get(message_id - 1)
    attacking_player_hp = players_hp.get(attacking_player)
    defending_player_hp = players_hp.get(defending_player)

    attacking_getuser = await app.get_users(attacking_player)
    defending_getuser = await app.get_users(defending_player)

    if user_id == attacking_player:
        damage = random.randint(1, 20)
        #damage = 50
        defending_player_hp -= damage
        print("Attack:", attacking_getuser.username or attacking_getuser.first_name, "HP:", attacking_player_hp,"\nDefending:", defending_getuser.username or defending_getuser.first_name, "HP:", defending_player_hp)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Атаковать пользователя {attacking_getuser.username or attacking_getuser.first_name}...", callback_data="attack")]
        ])
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"🗡: {attacking_getuser.username or attacking_getuser.first_name} (HP: {attacking_player_hp}) ⚔️ {defending_getuser.username or defending_getuser.first_name} (HP: {defending_player_hp}) :🛡\nПользователь {attacking_getuser.username or attacking_getuser.first_name} атакует пользователя {defending_getuser.username or defending_getuser.first_name} и наносит {damage} урона.",
            reply_markup=reply_markup
        )
        player1[message_id - 1] = defending_player
        player2[message_id - 1] = attacking_player
        players_hp[player1[message_id - 1]] = defending_player_hp
        players_hp[player2[message_id - 1]] = attacking_player_hp
    else:
        await callback_query.answer(text=f"Это только для {attacking_getuser.username or attacking_getuser.first_name}.")
    if defending_player_hp <= 0:
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Пользователь @{attacking_getuser.username or attacking_getuser.first_name} побеждает пользователя @{defending_getuser.username or defending_getuser.first_name}."
        )
        del accepted_challenges[message_id - 1]
        active_players.clear()
        update_players_hp_database(hp_file, attacking_player, attacking_player_hp)
        update_players_hp_database(hp_file, defending_player, defending_player_hp)

    await callback_query.answer()

app.run()
