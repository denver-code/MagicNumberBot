from aiogram import (
	Bot,
	Dispatcher,
	types
)
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import (
	State, 
	StatesGroup
)
from aiogram.dispatcher import FSMContext
from api import dialog_cal_callback, DialogCalendar
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import api.config_api as cp
import api.dp_api as db 

API_TOKEN = cp.get_value("TOKEN")

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class GrabName(StatesGroup):
	name = State()
	gender = State()
	bday = State()

class Keyboards():

	async def ygender():
		keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
		man_btn = types.InlineKeyboardButton(text=cp.get_value("man", filep=cp.get_value("L_CODE")), callback_data=f'gender_man')
		woman_btn = types.InlineKeyboardButton(text=cp.get_value("woman", filep=cp.get_value("L_CODE")), callback_data=f'gender_woman')
		keyboard.add(man_btn, woman_btn)
		return keyboard	

	async def mainmenu_board():
		keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
		paidnumber_btn = types.InlineKeyboardButton(text=cp.get_value("paid_rec", filep=cp.get_value("L_CODE")), callback_data=f'paidnumber_menu')
		faq_btn = types.InlineKeyboardButton(text=cp.get_value("faq", filep=cp.get_value("L_CODE")), callback_data=f'faq_text')
		keyboard.add(paidnumber_btn, faq_btn)
		return keyboard

	async def secmenu_board():
		keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
		back_btn = types.InlineKeyboardButton(text=cp.get_value("back", filep=cp.get_value("L_CODE")), callback_data=f'back')
		keyboard.add(back_btn)
		return keyboard	
	
	async def paid_board():
		keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
		bday_energy = types.InlineKeyboardButton(text=cp.get_value("bday_en", filep=cp.get_value("L_CODE")), callback_data=f'paid_bday')
		year_task = types.InlineKeyboardButton(text=cp.get_value("year_task", filep=cp.get_value("L_CODE")), callback_data=f'paid_yeartask')
		your_task = types.InlineKeyboardButton(text=cp.get_value("your_mission", filep=cp.get_value("L_CODE")), callback_data=f'paid_yourtask')
		back_btn = types.InlineKeyboardButton(text=cp.get_value("back", filep=cp.get_value("L_CODE")), callback_data=f'back')
		keyboard.add(year_task, your_task, bday_energy, back_btn)
		return keyboard	

@dp.message_handler(commands=["start"])
async def start_event(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		user_obj = await  db.find_q("users", {"telegram_id":message.from_user.id})
		if user_obj:
			await message.answer(f"Рады вас видеть, {user_obj['name']}!")
			await message.answer(cp.get_value("welcome_text", filep=cp.get_value("L_CODE")), reply_markup=await Keyboards.mainmenu_board())
		else:
			await GrabName.name.set()
			await message.answer(cp.get_value("your_name", filep=cp.get_value("L_CODE")))

@dp.message_handler(state=[GrabName.name], content_types=["text"])
async def name_event(message, state):
	async with state.proxy() as data:
		data["name"] = message.text
		await GrabName.next()
	await message.answer(f"Приятно познакомиться, {message.text}!")
	await message.answer(f"Вы", reply_markup=await Keyboards.ygender())

@dp.callback_query_handler(dialog_cal_callback.filter(), state=[GrabName.bday])#
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
	selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
	if selected:
		async with state.proxy() as data:
			data["b_date"] = date.strftime("%d/%m/%Y")
			await db.insert_db("users", {
				"telegram_id":callback_query.from_user.id,
				"name": data["name"],
				"bday": data["b_date"],
				"gender": data["gender"],
				"history": []
			})
		await callback_query.message.answer(
			f'{cp.get_value("complete_reg", filep=cp.get_value("L_CODE"))}',
		)
		await callback_query.message.answer(cp.get_value("welcome_text", filep=cp.get_value("L_CODE")), reply_markup=await Keyboards.mainmenu_board())
		await state.finish()

@dp.callback_query_handler(lambda c: c.data and c.data, state=["*"])
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:

		if callback_query.data == "faq_text":
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
			await callback_query.message.answer(cp.get_value("faq_text", filep=cp.get_value("L_CODE")))
			await callback_query.message.answer("Меню", reply_markup=await Keyboards.secmenu_board())
		
		elif "gender_" in callback_query.data:
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
			data["gender"] = callback_query.data.split("_")[1]
			await GrabName.bday.set()
			await callback_query.message.answer(cp.get_value("pls_select_date", filep=cp.get_value("L_CODE")), reply_markup=await DialogCalendar().start_calendar())

		elif callback_query.data == "back":
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
			await callback_query.message.answer(cp.get_value("welcome_text", filep=cp.get_value("L_CODE")), reply_markup=await Keyboards.mainmenu_board())
			
		elif callback_query.data == "paidnumber_menu":
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
			await callback_query.message.answer(cp.get_value("paid_rec", filep=cp.get_value("L_CODE")), reply_markup=await Keyboards.paid_board())

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)