import time
from core.vars import active_spins

last_command_usage_user = {}

async def antispam_user(user_id, sec):
    current_time = time.time()

    if user_id in active_spins:
        return "active_spin"

    if user_id in last_command_usage_user and current_time - last_command_usage_user[user_id] < sec:
        wait_time = int(sec - (current_time - last_command_usage_user[user_id]))
        return wait_time

    last_command_usage_user[user_id] = current_time
    return None

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
