from db.models import EmojiPhrase

DEFAULT_EMOJIS = ['🍒', '🍋', '🍏', '🍆']
DEFAULT_PHRASES = [
    'Вишня! Поздравляю!', 
    'Лови лимон!', 
    'Яблоко база.', 
    'БАКЛАЖАН! У вас ДЖЕКПОТ! Вставьте его поглубже...'
]

last_replaced_index = {}

async def add_emoji(chat_id: int, emoji: str, phrase: str):
    emoji_phrases = await EmojiPhrase.filter(chat_id=chat_id).order_by('id')

    if len(emoji_phrases) < 4:
        await EmojiPhrase.create(chat_id=chat_id, emoji=emoji, phrase=phrase)
    else:
        if chat_id not in last_replaced_index:
            last_replaced_index[chat_id] = 0
        
        replace_index = last_replaced_index[chat_id]
        emoji_phrases[replace_index].emoji = emoji
        emoji_phrases[replace_index].phrase = phrase
        await emoji_phrases[replace_index].save()

        last_replaced_index[chat_id] = (replace_index + 1) % 4

    return {"status": "success", "data": {"chat_id": chat_id, "emoji": emoji, "phrase": phrase}}

async def get_emoji(chat_id: int):
    emoji_phrases = await EmojiPhrase.filter(chat_id=chat_id)
    
    if emoji_phrases:
        emojis = [ep.emoji for ep in emoji_phrases]
        phrases = [ep.phrase for ep in emoji_phrases]
        return {"emoji": emojis, "phrases": phrases}
    
    return {"emoji": DEFAULT_EMOJIS, "phrases": DEFAULT_PHRASES}

async def del_emoji(chat_id: int):
    await EmojiPhrase.filter(chat_id=chat_id).delete()
    return {"status": "success", "message": f"All emojis and phrases for chat_id {chat_id} have been deleted."}
