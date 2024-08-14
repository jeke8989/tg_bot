from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.models import Channel
from bot.database import requests as rq
from config import bot


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔰 Мои каналы", callback_data='my_channels')]
    # [InlineKeyboardButton(text="⚙️ Подписка", callback_data='subscription')],
    # [InlineKeyboardButton(text="💰 Кошелек", callback_data='wallet')]
    
] )  

create_chanel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить канал", callback_data='add_chanel'), InlineKeyboardButton(text="◀️ Назад", callback_data='back_main')]
    
] )  

cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data='back_main')]
    
] )  

# Билдер клавиатуры для каналов 
async def create_channel_buttons(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="➕ Добавить канал",
        callback_data='add_chanel'
    )
    for channel in channels:
        builder.button(
            text=f'▶️ {channel.name}',  # Название канала на кнопке
            callback_data=f"setting_channel_{channel.id_channel}"  # Данные для обратного вызова
        )
    
    # Добавляем дополнительные кнопки
    
    builder.button(
        text="◀️ Назад",
        callback_data='back_main'
    )
    builder.adjust(1)
    
    # Генерируем разметку клавиатуры
    return builder.as_markup()

# Билдер клавиатуры удаления и редактирования
async def edit_channel_buttons(channel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="➕ Удалить канал",
        callback_data=f'delete_channel_{channel_id}'
    )
    builder.button(
        text="◀️ Назад",
        callback_data='back_main'
    )
    builder.adjust(1)
    # Генерируем разметку клавиатуры
    return builder.as_markup()

# Билдер клавиатуры для отправки сообщения в канал
async def channel_btn_to_send_post(user_id: str, message: Message) -> InlineKeyboardMarkup:
    """_summary_

    Args:
        user_id (str): _description_

    Returns:
        InlineKeyboardMarkup: _description_
    """
    builder = InlineKeyboardBuilder()
    channels = await rq.get_user_channel_new(user_id=user_id)
    
    # Фильтруем список по значению defaul=True
    # filtered_channels = list(filter(lambda channel: getattr(channel, 'defaul', True), channels))
    list_chan =[]
    for chan in channels:
        var = await rq.check_bot_admin_channel(channel_id=chan.id_channel, bot=bot)
        if var:
            list_chan.append(chan)
    
    for channel in list_chan:
        builder.button(
            text=f'📨 {channel.name}',  # Название канала на кнопке
            callback_data=f"send_{channel.id_channel}@mess_{message.message_id}",  # Данные для обратного вызова
        )
    # builder.button(
    #         text=f'✏️ Редактировать', 
    #         callback_data=f"message_edit_{message.message_id}@chat_{message.chat.id}",  # Данные для обратного вызова
    #     )
    builder.button(
            text=f'🗑️ Удалить', 
            callback_data=f"message_delete_{message.message_id}@chat_{message.chat.id}",  # Данные для обратного вызова
        )
    builder.adjust(1)
    # Генерируем разметку клави
    return builder.as_markup()
