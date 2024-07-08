import re, asyncio
from db.emoji import add_emoji, get_emoji
from casino.antispam import antispam_group

from config import logging_config
logging = logging_config.setup_logging(__name__)

SET_COMMAND_PATTERN = re.compile(r'(?:[^:]+:[^\.]+\.\s*){4}')

async def set_emoji_command(message):
    chat_id = message.chat.id
    chat_name = message.chat.title or "this chat"
    text = message.text[len("/set "):]
    spam_check = await antispam_group(chat_id, 900)

    if isinstance(spam_check, int):
        msg_wait = await message.reply_text(f"Пожалуйста, подождите {spam_check} минут перед повторным выполнением команды.")
        await asyncio.sleep(10)
        await msg_wait.delete()
        return

    if not SET_COMMAND_PATTERN.fullmatch(text):
        await message.reply("Invalid format. Use exactly 4 emoji and phrase pairs in the format: /set 🍒:Вишня. 🍋:Лимон. 🍏:Яблоко. 🍆:Баклажан.")
        return

    matches = re.findall(r'([^:]+):([^\.]+)\.', text)

    responses = []
    for match in matches:
        emoji = match[0].strip()
        phrase = match[1].strip()
        response = await add_emoji(chat_id, emoji, phrase)
        responses.append(response["data"])

    await message.reply(f"Emoji and phrases set for {chat_name}.")

async def get_emoji_command(message):
    chat_id = message.chat.id
    logging.debug(chat_id)
    chat_name = message.chat.title or "this chat"
    result = await get_emoji(chat_id)

    emoji_phrase_pairs = [f"{emoji} - {phrase}" for emoji, phrase in zip(result['emoji'], result['phrases'])]
    response_message = f"Emojis for {chat_name}:\n" + "\n".join(emoji_phrase_pairs)

    await message.reply(response_message)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
