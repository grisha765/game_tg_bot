# casino_tg_bot
This Python script is a Telegram bot that simulates a slot machine game. It allows users to trigger the slot machine by sending certain messages containing specific keywords related to gambling. The bot then displays a spinning animation of slot machine reels and announces the result, whether the user has won or lost.

### Initial Setup

1. **Clone the repository**: Clone this repository using `git clone`.
2. **Create Virtual Env**: Create a Python Virtual Env `venv` to download the required dependencies and libraries.
3. **Download Dependencies**: Download the required dependencies into the Virtual Env `venv` using `pip`.

```shell
git clone https://github.com/grisha765/casino_tg_bot.git
cd casino_tg_bot
python3 -m venv venv
venv/bin/pip3 install pyrofork tgcrypto aiohttp
```

### Run Bot

1. **Start an Instance**: Start an instance from the `venv` virtual environment by entering your `TOKEN` using the `-t` argument received from @BotFather.

```shell
venv/bin/python3 main.py -t TOKEN
```

### Features

1. Simulates a slot machine game within the Telegram messaging platform.
2. Supports multi-user interaction.
3. Implements cooldown functionality to prevent spamming of the slot machine.
4. You can set emojis and winning phrases for them for each group.
