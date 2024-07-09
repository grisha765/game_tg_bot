# game_tg_bot
This Python script is a Telegram bot that simulates a slot machine game. It allows users to trigger the slot machine by sending certain messages containing specific keywords related to gambling. The bot then displays a spinning animation of slot machine reels and announces the result, whether the user has won or lost.

### Initial Setup

1. **Clone the repository**: Clone this repository using `git clone`.
2. **Create Virtual Env**: Create a Python Virtual Env `venv` to download the required dependencies and libraries.
3. **Download Dependencies**: Download the required dependencies into the Virtual Env `venv` using `pip`.

```shell
git clone https://github.com/grisha765/casino_tg_bot.git
cd casino_tg_bot
python3 -m venv .venv
.venv/bin/pip3 install -r requirements.txt
```

## Usage

### Deploy

- Run the bot:
    ```bash
    TG_TOKEN="telegram_bot_token" python main.py
    ```

- Other working env's:
    ```env
    LOG_LEVEL="INFO"
    TG_ID="your_telegram_api_id"
    TG_HASH="your_telegram_api_hash"
    TG_TOKEN="your_telegram_bot_token"
    DB_PATH="sqlite://:memory:"
    ```

## Features

- Simulates a slot machine game within the Telegram messaging platform.
- Supports multi-user interaction.
- Implements cooldown functionality to prevent spamming of the slot machine.
- You can set emojis and winning phrases for them for each group.
