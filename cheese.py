import chess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Client("bot")

# Идентификаторы и имена игроков (инициализируются при запуске игры)
WHITE_PLAYER_ID = None
BLACK_PLAYER_ID = None
WHITE_PLAYER_NAME = None
BLACK_PLAYER_NAME = None

# Инициализация шахматной доски
board = chess.Board()

# Словарь для отображения шахматных фигур
PIECE_SYMBOLS = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', '.': '⬜'
}

# Генерация клавиатуры шахматной доски
def generate_chessboard():
    board_keyboard = []
    for row in range(8):
        board_row = []
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            symbol = PIECE_SYMBOLS[piece.symbol()] if piece else PIECE_SYMBOLS['.']
            callback_data = f"{chess.square_name(chess.square(col, 7 - row))}"
            button = InlineKeyboardButton(text=symbol, callback_data=callback_data)
            board_row.append(button)
        board_keyboard.append(board_row)
    return board_keyboard

# Отправка шахматной доски в группу
async def send_chessboard(client, chat_id, message_id=None):
    chessboard = generate_chessboard()
    white_display = f"@{WHITE_PLAYER_NAME} <==" if board.turn == chess.WHITE else f"@{WHITE_PLAYER_NAME}"
    black_display = f"@{BLACK_PLAYER_NAME} <==" if board.turn == chess.BLACK else f"@{BLACK_PLAYER_NAME}"
    text = f"Шахматная доска:\nЧерные: {black_display}\nБелые: {white_display}"
    if message_id:
        try:
            return await client.edit_message_text(chat_id, message_id, text=text, reply_markup=InlineKeyboardMarkup(chessboard))
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                return None
            else:
                raise e
    else:
        return await client.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(chessboard))

# Обработчик команды /start
@app.on_message(filters.command("start") & filters.group)
async def start(client, message):
    global WHITE_PLAYER_ID, WHITE_PLAYER_NAME, BLACK_PLAYER_ID, BLACK_PLAYER_NAME
    if not WHITE_PLAYER_ID:
        WHITE_PLAYER_ID = message.from_user.id
        WHITE_PLAYER_NAME = message.from_user.username if message.from_user.username else message.from_user.first_name
        join_button = InlineKeyboardButton("Присоединиться к игре за черных", callback_data="join_black")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text(f"Белые: @{WHITE_PLAYER_NAME}\nОжидание игрока за черных.", reply_markup=reply_markup)
    else:
        await message.reply_text("Игра уже началась.")

# Обработчик нажатия на инлайн-кнопку для присоединения второго игрока
@app.on_callback_query(filters.regex("join_black"))
async def join_black(client, callback_query):
    global BLACK_PLAYER_ID, BLACK_PLAYER_NAME, WHITE_PLAYER_ID, WHITE_PLAYER_NAME
    user_id = callback_query.from_user.id
    if user_id == WHITE_PLAYER_ID:
        await callback_query.answer("Вы не можете присоединиться к игре за черных, если вы уже играете за белых.", show_alert=True)
    elif not BLACK_PLAYER_ID:
        BLACK_PLAYER_ID = user_id
        BLACK_PLAYER_NAME = callback_query.from_user.username if callback_query.from_user.username else callback_query.from_user.first_name
        await callback_query.message.edit_text(f"Черные: @{BLACK_PLAYER_NAME}\nОжидание начала игры.")
        await send_chessboard(client, callback_query.message.chat.id)
    else:
        await callback_query.answer("Игра уже началась.", show_alert=True)

# Переменные для хранения хода
selected_square = None

# Обработчик нажатия на кнопку
@app.on_callback_query()
async def button(client, callback_query):
    global selected_square

    user_id = callback_query.from_user.id
    position = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id

    if position == "join_black":
        await join_black(client, callback_query)
        return

    if (board.turn == chess.WHITE and user_id == WHITE_PLAYER_ID) or (board.turn == chess.BLACK and user_id == BLACK_PLAYER_ID):
        if selected_square:
            move = chess.Move.from_uci(selected_square + position)
            if move in board.legal_moves:
                board.push(move)
                selected_square = None
                await send_chessboard(client, chat_id, message_id=message_id)
                if board.is_checkmate():
                    await client.send_message(chat_id, "Мат!")
                elif board.is_stalemate():
                    await client.send_message(chat_id, "Пат!")
            else:
                await callback_query.answer(f"Неправильный ход {selected_square + position}. Попробуйте еще раз.", show_alert=True)
                selected_square = None
        else:
            selected_square = position
            await callback_query.answer(f"Выбрано {position}", show_alert=True)
    else:
        await callback_query.answer("Сейчас не ваш ход", show_alert=True)

app.run()

