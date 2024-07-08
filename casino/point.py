from db.point import get_points, get_all_points
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def check_wins(message):
    user_id = message.from_user.id
    wins_points = str(await get_points(user_id))
    await message.reply_text(f"Ваши победы: {wins_points}")

async def top_command(client, message):
    user_scores = await get_all_points()
    logging.debug(list(user_scores.keys()))
    users = await client.get_users(user_ids=list(user_scores.keys()))

    user_dict = {}
    for user in users:
        if user.username:
            user_dict[user.id] = user.username
        else:
            full_name = user.first_name
            if user.last_name:
                full_name += f" {user.last_name}"
            user_dict[user.id] = full_name

    sorted_users = sorted(user_scores.items(), key=lambda item: item[1], reverse=True)
    top_message = "Топ победителей:\n"
    for index, (user_id, num) in enumerate(sorted_users, start=1):
        username = user_dict.get(user_id, str(user_id))
        top_message += f"{index}) {username} - {num}\n"

    await message.reply_text(top_message, disable_notification=True)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
