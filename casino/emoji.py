import re, asyncio
from db.emoji import add_emoji, get_emoji
from casino.antispam import antispam_group

from config import logging_config
logging = logging_config.setup_logging(__name__)

SET_COMMAND_PATTERN = re.compile(r'(?:[^:]+:[^\.]+\.\s*){4}')

async def set_emoji_command(message, get_translation):
    user_language = message.from_user.language_code
    chat_id = message.chat.id
    chat_name = message.chat.title or get_translation(user_language, "none_chatname")
    text = message.text[len("/set "):]
    spam_check = await antispam_group(chat_id, 900)

    if isinstance(spam_check, int):
        msg_wait = await message.reply_text(f"{get_translation(user_language, "antispam")} {spam_check} {get_translation(user_language, "antispam_min")}")
        await asyncio.sleep(10)
        await msg_wait.delete()
        return

    if not SET_COMMAND_PATTERN.fullmatch(text):
        await message.reply(get_translation(user_language, "invalid_set_format"))
        return

    matches = re.findall(r'([^:]+):([^\.]+)\.', text)

    responses = []
    for match in matches:
        emoji = match[0].strip()
        phrase = match[1].strip()
        response = await add_emoji(chat_id, emoji, phrase)
        responses.append(response["data"])

    await message.reply(f"{get_translation(user_language, "successful_set")} {chat_name} {get_translation(user_language, "successful_set2")}")

async def get_emoji_command(message, get_translation):
    user_language = message.from_user.language_code
    chat_id = message.chat.id
    logging.debug(chat_id)
    chat_name = message.chat.title or get_translation(user_language, "none_chatname")
    result = await get_emoji(chat_id)

    emoji_phrase_pairs = [f"{emoji} - {phrase}" for emoji, phrase in zip(result['emoji'], result['phrases'])]
    response_message = f"{get_translation(user_language, "response_get")} {chat_name}:\n" + "\n".join(emoji_phrase_pairs)

    await message.reply(response_message)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
