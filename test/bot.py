import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from api import dialog_cal_callback, DialogCalendar


logging.basicConfig(level=logging.INFO)

bot = Bot(token="1952028129:AAGtd81js1WYT67ssowviByS3t9wensBlig")
dp = Dispatcher(bot)


@dp.message_handler(Text(equals=['dialog'], ignore_case=True))
async def simple_cal_handler(message: Message):
    await message.answer("Пожалуйста выберете дату рождения: ", reply_markup=await DialogCalendar().start_calendar())


@dp.callback_query_handler(dialog_cal_callback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'[Logger]: Date {date.strftime("%d/%m/%Y")}',
        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)