from aiogram.filters import CommandStart, Command
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from bot.database import requests as rq
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.keyboards import user_keybords as kb


from bot.database.requests import check_bot_admin_channel
import config

bot = config.bot

class Reg(StatesGroup):
        chanel = State()
        name = State()
        number = State()
       

router = Router()

async def start_func(message: Message, user_name: str):
        await message.answer(f'Привет, {user_name}\n\nЭтот бот предназначен для помощи в ведении Telegram каналов.\n\nПересылай сюда посты с других каналов, которые хочешь переслать в свои канала, от имни админа', reply_markup=kb.main)

#Старт
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
        """ Команда старт
        """
        await rq.set_user(tg_id=message.from_user.id, name=message.from_user.full_name)
        await start_func(message=message, user_name=message.from_user.full_name)
        
#Команада помощь
@router.message(Command('help'))
async def get_help(message: Message) -> None:
        await message.answer("Нужна помощь?")

#Мои каналы. Пункт меню
@router.callback_query(F.data == "my_channels")
async def my_channel(callback: CallbackQuery) -> None:
    user_channels = await rq.get_user_channels(callback.from_user.id)
    
    if user_channels:
        # Формируем сообщение со списком каналов  
        response_message = 'Ваши каналы:'
        keyboard = await kb.create_channel_buttons(user_channels)
        await callback.message.answer(response_message, reply_markup=keyboard)
    else: 
        response_message = "У вас пока нет подключенных каналов."
        keyboard =kb.create_chanel
        await callback.message.answer(response_message, reply_markup=keyboard)
    
        
#Вводим название канала
@router.callback_query(F.data == "add_chanel")
async def my_channel_one(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(Reg.chanel)
        await callback.message.answer("Перешлите сообщение из вашего канала, чтобы добавить его в список", reply_markup=kb.cancel)
             
@router.message(Reg.chanel)
async def my_channel_one(message: Message, state: FSMContext):
        await rq.add_chanel(message=message)
        
#Кнопка назад
@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, state: FSMContext) -> None:
        await start_func(message=callback.message, user_name=callback.from_user.full_name)
        await state.clear()
        
#Меню удаления или редактирования канла
@router.callback_query(F.data.contains("setting_channel_"))
async def setting_channel(callback: CallbackQuery, state: FSMContext) -> None:
        chat_id = callback.data.replace('setting_channel_', '')
        channel = await rq.get_user_channels_by_id(id_channel=chat_id, user_id=callback.from_user.id)
        status_bot = await check_bot_admin_channel(channel_id=chat_id, bot=bot)
        text = ''
        if status_bot is True:
                text = '✅ Бот успешно подключен к каналу\n'
        else: 
                text = '❌ Бот не подключен к каналу.\nВам необходимо добать бота в качестве адмистратора канала\n'
                
        await callback.message.answer(f'Текущий канал:\n{channel.name}\n{text}', reply_markup=await kb.edit_channel_buttons(channel_id=chat_id))
        await state.clear()

#Удаляем канал
@router.callback_query(F.data.contains("delete_channel_"))
async def del_channel(callback: CallbackQuery, state: FSMContext) -> None:
        channel_id = callback.data.replace('delete_channel_', '')
        
        result = await rq.delete_channel(channel_id=channel_id, user_id=callback.from_user.id)
        if result is True:
                await callback.message.answer('Канал удален', reply_markup=kb.main)
        else: 
                await callback.message.answer('Что то пошла не так', reply_markup=kb.main) 
        await state.clear()

#Ловим любое сообщение пересылаемое в чат
@router.message(F.content_type.ANY)
async def get_forward_message(message: Message) -> None:
        if message.forward_origin.type == "channel":
                try:
                        await build_message(message=message)
                except Exception as e:
                        await message.answer('Что то не так', reply_markup=kb.main)        
        else:
                await message.answer('Что то не так', reply_markup=kb.main)

#Формируем пересылаемое сообщение
async def build_message(message: Message) -> None:
        caption = message.caption or message.text or ''
        keybord = await kb.channel_btn_to_send_post(message.from_user.id, message=message)
        entities = message.caption_entities if message.caption else message.entities
        # Пересылка медиа сообщений с текстом
        if message.photo:
            mes = await message.answer_photo(photo=message.photo[-1].file_id, caption=caption, caption_entities=entities, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)  
        elif message.video:
            mes = await message.answer_video(video=message.video.file_id, caption=caption, caption_entities=entities, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)
        elif message.document:
            mes = await message.answer_document(document=message.document.file_id, caption_entities=entities, caption=caption, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)
        elif message.audio:
            mes = await message.answer_audio(audio=message.audio.file_id, caption=caption, caption_entities=entities, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)
        elif message.voice:
            mes = await message.answer_voice(voice=message.voice.file_id, caption=caption, caption_entities=entities, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)
        elif message.animation:
            mes = await message.answer_animation(animation=message.animation.file_id, caption=caption, caption_entities=entities, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)
        else:
            # Если это просто текстовое сообщение
            mes = await message.answer(caption, entities=entities, reply_markup=keybord)
            await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            key = await kb.channel_btn_to_send_post(message.from_user.id, message=mes)
            await bot.edit_message_reply_markup(message_id=mes.message_id, reply_markup=key, chat_id=mes.chat.id)

#Формируем пересылаемое сообщение для бота в канал
async def build_message_to_bot_send(message: Message, chat_id: str) -> None:
        caption = message.caption or message.text or ''
        # keybord = await kb.channel_btn_to_send_post(message.from_user.id, message=message)
        entities = message.caption_entities if message.caption else message.entities
        # Пересылка медиа сообщений с текстом
        if message.photo:
            await bot.send_photo(photo=message.photo[-1].file_id, chat_id=chat_id, caption=caption, caption_entities=entities)
        elif message.video:
            await bot.send_video(video=message.video.file_id, chat_id=chat_id, caption=caption, caption_entities=entities)
        elif message.document:
            await bot.send_document(document=message.document.file_id, chat_id=chat_id, caption_entities=entities, caption=caption)
        elif message.audio:
            await bot.send_audio(audio=message.audio.file_id, chat_id=chat_id, caption=caption, caption_entities=entities)
        elif bot.voice:
            await bot.send_voice(voice=message.voice.file_id, chat_id=chat_id, caption=caption, caption_entities=entities)
        elif bot.animation:
            await bot.send_animation(animation=message.animation.file_id, chat_id=chat_id, caption=caption, caption_entities=entities)
        else:
            # Если это просто текстовое сообщение
            await bot.send_message(caption, entities=entities)

# #Отправляем сообщение в канал
@router.callback_query(F.data.contains("send_"))
async def send_message(callback: CallbackQuery) -> None:
        channel_id = callback.data.split('@')[0].replace('send_', '')
        message_id = callback.data.split('@')[-1].replace('mess_', '')
        
        try:
                await build_message_to_bot_send(message=callback.message, chat_id=channel_id)
 
        except Exception as e:
                print(e)
                await callback.message.answer('Что-то пошло не так')
                
# Удаляем сообщение
@router.callback_query(F.data.contains("message_delete_"))
async def del_message(callback: CallbackQuery) -> None:
        chat_id = callback.data.split('@')[-1].replace('chat_', '')
        message_id = callback.data.split('@')[0].replace('message_delete_', '')
        try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
                await callback.message.answer('Сообщение удалено')
                
        except Exception as e:
                await callback.message.answer(f'Что-то пошло не так\n{e}')
        