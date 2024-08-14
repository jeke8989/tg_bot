from bot.database.models import async_session
import json
from bot.database.models import User, Channel
from sqlalchemy import select, delete
from aiogram.types import Message
from aiogram.enums.chat_member_status import ChatMemberStatus
from bot.database.models import Channel
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from bot.database.models import Channel, async_session, Post

import bot.keyboards.user_keybords as kb

class Status:
    def __init__(self, code: int):
        self.code = code


#Получения списка подключенных каналов пользователя      
async def get_user_channels (user_id: str):
    async with async_session() as session:
        result = await session.scalars(
            select(Channel).where(Channel.user == user_id)
        )
        channels = result.all()
        return channels
    
#Проверка существует ли канал в базе
async def check_channel_exists(async_session: AsyncSession, message: Message) -> bool:
    async with async_session() as session:
        result = await session.scalar(
            select(Channel).where(
                Channel.id_channel == message.forward_origin.chat.id,
                Channel.user == message.from_user.id
            )
        )
        exist = result is not None
        return exist
    
#Проверка существует ли пост в базе
async def check_post_exists(async_session: AsyncSession, message: Message) -> bool:
    async with async_session() as session:
        result = await session.scalar(
            select(Post).where(
                Post.message_ob == json.dumps(message),
                Post.user == message.from_user.id
            )
        )
        exist = result is not None
        return exist

async def set_user(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()
            
"""Добавление чата к списку пользователя
"""            
async def add_chanel(message: Message) -> Status:
    try: 
        # Проверяем наличие канала в базе
        channel_exists = await check_channel_exists(async_session, message)
            
        # Если канал существует. Отправляем собщение что канал существует
        if channel_exists:
            await message.answer('Такой канал уже существует', reply_markup=kb.create_chanel)
        
        # Если канал не сущестует. Добавляем канал в базу данных
        else: 
            async with async_session() as session:
                new_chanel = Channel(
                    name=message.forward_origin.chat.title,
                    id_channel=message.forward_origin.chat.id,
                    user=message.from_user.id
                )
                session.add(new_chanel)
                await session.commit()
                
                user_channels = await get_user_channels(message.from_user.id)
                
                
                await message.answer('Ваш канал успешно добавлен', reply_markup=await kb.create_channel_buttons(channels=user_channels))
                return Status(code=200)
    except Exception as e:
        await message.answer(f'Что-то пошло не так, поробуйте снова\n\n{e}', reply_markup=kb.create_chanel)
        return Status(code=400)
    

    
    
#Получаем callback с ID канала для удаления
async def get_user_channels_by_id (user_id: str, id_channel: str) -> Channel:
    async with async_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.user == user_id, Channel.id_channel == id_channel)
        )
        return channel

#Получаем колличесво подключенных каналов
async def get_count_channel(user_id: str, channel_id: str) -> int:
    async with async_session() as session:
        result = await session.scalars(
            select(Channel).where(Channel.user == user_id, Channel.id_channel == channel_id)
        )
        count = len(result.all())
        return count

#Проверям подключен явлеяется Bot админом канала
async def check_bot_admin_channel(channel_id: str, bot: Bot) -> bool:
    try:
        # Получаем информацию о боте в указанном канале
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        
        # Проверяем, является ли бот администратором или создателем
        if chat_member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}:
            return True
        else: 
            return False
    except Exception as e:
        return False
    
#Удаляем channel из базы
async def delete_channel(user_id: str, channel_id: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            # Удаление каналов по user_id и channel_id
            result = await session.execute(
                delete(Channel).where(Channel.id_channel == channel_id, Channel.user == user_id)
            )
            if result.rowcount > 0:
                return True
            return False

#Получаем каналы подклюненные к юзеру
async def get_user_channel_new(user_id: str) -> list[Channel]:
    """_summary_

    Args:
        user_id (str): _description_
        channel_id (str): _description_

    Returns:
        list[Channel]: _description_
    """
    async with async_session() as session:
        result = await session.scalars(
            select(Channel).where(Channel.user == user_id)
        )
        channel_result = result.all()
        return channel_result
    