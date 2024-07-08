from db.models import EmojiPhrase

DEFAULT_EMOJIS = ['🍒', '🍋', '🍏', '🍆']
DEFAULT_PHRASES = [
    'Вишня! Поздравляю!', 
    'Лови лимон!', 
    'Яблоко база.', 
    'БАКЛАЖАН! У вас ДЖЕКПОТ! Вставьте его поглубже...'
]

async def add_emoji(chat_id: int, emoji: str, phrase: str):
    emoji_phrase, created = await EmojiPhrase.get_or_create(chat_id=chat_id, emoji=emoji, defaults={'phrase': phrase})
    if not created:
        emoji_phrase.phrase = phrase
        await emoji_phrase.save()
    return {"status": "success", "data": {"chat_id": chat_id, "emoji": emoji, "phrase": phrase}}

async def get_emoji(chat_id: int):
    emoji_phrases = await EmojiPhrase.filter(chat_id=chat_id)
    
    if emoji_phrases:
        emojis = [ep.emoji for ep in emoji_phrases]
        phrases = [ep.phrase for ep in emoji_phrases]
        return {"emoji": emojis, "phrases": phrases}
    
    return {"emoji": DEFAULT_EMOJIS, "phrases": DEFAULT_PHRASES}
