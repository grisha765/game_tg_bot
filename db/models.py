from tortoise import fields
from tortoise.models import Model

class Wins(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    point = fields.BigIntField()

    class Meta:
        table = "wins"
        unique_together = ("user_id",)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
