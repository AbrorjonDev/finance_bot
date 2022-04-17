from aiogram import Dispatcher, Bot, executor, types
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()
#local imports
from keyboards import language, main_keyboard, phone_keyboard, contact, change_language
from database import update_user_object, get_admins_contact, get_user_infos, get_user_lang, set_user_lang

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def welcome(message:types.Message):
    first_name = message.from_user.first_name or ''
    last_name = message.from_user.last_name or ''

    lang = await get_user_lang(user_id=message.from_user.id)
    lang_res = {
        'en': f'Welcome,{first_name} {last_name}.\nPlease choose your language.',
        'ru': f'Добро пожаловать, {first_name} {last_name}. \nВыберите язык.',
        'uz': f'Xush kelibsiz, {first_name} {last_name}. \nIltimos tilni tanlang. '
    }
    await bot.send_message(
        chat_id=message.chat.id,
        text=lang_res[lang],
        reply_markup=language
        )

@dp.callback_query_handler(text=["en", "ru", "uz"])
async def set_user_language(callback: types.CallbackQuery):
    lang_res = {
        'en':'Language has been set to English.',
        'ru':'Язык установлен Русский.',
        'uz':'Til O\'zbek tiliga sozlandi.'
    }

    lang = await set_user_lang(user_id=callback.from_user.id, lang=callback.data)
    
    
    lang_res_2 = {
        'en':'Share your phone number so the bot can recognize you.',
        'ru':'Поделитесь своим номером телефона, чтобы бот мог вас узнать.',
        'uz':'Bot sizni tanishi uchun telefon raqamingizni ulashing.'
    }
    await callback.answer(lang_res[callback.data])
    # await bot.send_message(callback['message']['chat']['id'], f"{lang_res[callback.data]}")
    await bot.send_message(callback['message']['chat']['id'], lang_res_2[callback.data], reply_markup=phone_keyboard)



    await bot.delete_message(callback['message']['chat']['id'], callback['message']['message_id'])
    
@dp.message_handler(content_types=['contact'])
async def set_user_by_phone(message:types.ContentType.ANY):
    phone_number = message['contact']['phone_number']
    user_id = message.from_user.id
    contact_id = message.contact.user_id
    if user_id == contact_id: 
        if not phone_number.startswith('+'):
            phone_number = '+'+''.join(str(phone_number))
        user = await update_user_object(user_id=message['from']['id'], phone=phone_number)
        await bot.send_chat_action(message['chat']['id'], action="typing")
        if user:
            await bot.send_message(message['chat']['id'], "Succesful! {0}".format(user), reply_markup=main_keyboard)
        else:
            await bot.send_message(message['chat']['id'], "Authentication failed!\nPlease contact with admins", reply_markup=phone_keyboard)
            for phone in await get_admins_contact():
                await bot.send_contact(message['chat']['id'], phone_number=phone[0], first_name=phone[1])
    else:
        await bot.send_message(message['chat']['id'], "Authentication failed!\nPlease contact with admins", reply_markup=phone_keyboard)

        for phone in await get_admins_contact():
            await bot.send_contact(message['chat']['id'], phone_number=phone[0], first_name=phone[1])
@dp.callback_query_handler(text=["change_en", "change_ru", "change_uz"])
async def set_user_changed_language(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    msg_id = callback.message.message_id
    lang = callback.data[-2:]
    lang_res = {
        'en':'Language has been set to English.',
        'ru':'Язык установлен Русский.',
        'uz':'Til O\'zbek tiliga sozlandi.'
    }
    
    lang = await set_user_lang(user_id=user_id, lang=lang)
    await bot.send_message(chat_id, lang_res[lang])
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)

@dp.message_handler(text=["Infos", "Language"])
async def get_student_infos(message:types.Message):
    lang = await get_user_lang(user_id=message['from']['id'], )

    if message["text"] == "Infos":
        await bot.send_chat_action(message['chat']['id'], action='typing')
        new_message = await get_user_infos(user_id=message['from']['id'], lang=lang)
        await bot.send_message(message['chat']['id'], new_message)
    else:
        
        lang_res = {
        'en': '\nPlease choose your language. ',
        'ru': '\nВыберите язык. ',
        'uz': '\nIltimos tilni tanlang. '
        }
        await message.answer(
        lang_res[lang],
        reply_markup=change_language
        )
    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
