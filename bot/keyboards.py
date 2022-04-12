from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
    )


en = InlineKeyboardButton(text="English", callback_data="en")
ru = InlineKeyboardButton(text="Russian", callback_data="ru")
uz = InlineKeyboardButton(text="Uzbek", callback_data="uz")

language = InlineKeyboardMarkup(resize_keyboard=True)
language.add(en, ru , uz)

Infos = KeyboardButton(text="Infos")
Language = KeyboardButton(text="Language")
Phone = KeyboardButton(text="Phone", request_contact=True)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(Infos, Language, Phone)


change_en = InlineKeyboardButton(text="English", callback_data="change_en")
change_ru = InlineKeyboardButton(text="Russian", callback_data="change_ru")
change_uz = InlineKeyboardButton(text="Uzbek", callback_data="change_uz")

change_language = InlineKeyboardMarkup(resize_keyboard=True)
change_language.add(change_en, change_ru , change_uz)

phone = InlineKeyboardButton(text="Your phone", callback_data="phone", request_contact=True)
contact = InlineKeyboardMarkup(resize_keyboard=True).add(phone, Language)


phone_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(Phone, Language)
