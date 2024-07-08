from tortoise import fields
from tortoise.models import Model

class Wins(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    point = fields.BigIntField()

    class Meta:
        table = "wins"
        unique_together = ("user_id",)

class EmojiPhrase(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.IntField()
    emoji = fields.CharField(max_length=10)
    phrase = fields.CharField(max_length=255)

    class Meta:
        table = "EmojiPhrase"
        unique_together = ("chat_id", "emoji")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
