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
from aiogram.types.message import (
	ContentType,
	Message
)
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import api.config_api as cp
import api.dp_api as db 
from api import (
	dialog_cal_callback,
	DialogCalendar
)
from api.sumOfDigits import sumOfDigits
import datetime

API_TOKEN = cp.get_value("TOKEN")

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

prices = {
	"bday" : 2500,
	"key": 2100
}


class YearSelection(StatesGroup):
	new_year = State()
	old_year = State()

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
		key_energy = types.InlineKeyboardButton(text=cp.get_value("key_en", filep=cp.get_value("L_CODE")), callback_data=f'paid_key')
		year_task = types.InlineKeyboardButton(text=cp.get_value("year_task", filep=cp.get_value("L_CODE")), callback_data=f'paid_yeartask')
		your_task = types.InlineKeyboardButton(text=cp.get_value("your_mission", filep=cp.get_value("L_CODE")), callback_data=f'paid_yourtask')
		back_btn = types.InlineKeyboardButton(text=cp.get_value("back", filep=cp.get_value("L_CODE")), callback_data=f'back')
		keyboard.add(bday_energy, back_btn)#year_task, your_task, 
		return keyboard	
	
	async def year_selection(name):
		keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
		old = types.InlineKeyboardButton(text=cp.get_value("old_y", filep=cp.get_value("L_CODE")), callback_data=f'year_old_{name}')
		new = types.InlineKeyboardButton(text=cp.get_value("old_n", filep=cp.get_value("L_CODE")), callback_data=f'year_new_{name}')
		keyboard.add(old, new)
		return keyboard	

	async def day_selection(name):
		keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
		old = types.InlineKeyboardButton(text=cp.get_value("old_d", filep=cp.get_value("L_CODE")), callback_data=f'day_old_{name}')
		new = types.InlineKeyboardButton(text=cp.get_value("new_d", filep=cp.get_value("L_CODE")), callback_data=f'day_new_{name}')
		keyboard.add(old, new)
		return keyboard	

async def create_order(message: types.Message, order_name, order_info, cost, feature):
	if cp.get_value("PAYMENT_TOKEN").split(':')[1] == 'TEST':
		await bot.send_message(message.chat.id, cp.get_value("pre_buy_demo_alert", filep=cp.get_value("L_CODE")))

	await bot.send_invoice(message.chat.id,
						   title=order_name,
						   description=order_info,
						   provider_token=cp.get_value("PAYMENT_TOKEN"),
						   currency='usd',
						   prices=[types.LabeledPrice(label=order_name, amount=cost*100)],
						   start_parameter=f'null',
						   payload=f'neworder_{message.from_user.id}_{feature}'
						   )

@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
	await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
	pmnt = message.successful_payment.to_python()

	# for key, val in pmnt.items():
	# 	print(f'{key} = {val}')

	buy_name = pmnt["invoice_payload"].split("_")[-1]

	if buy_name == "bday":
		await bot.send_message(

			message.chat.id,
			cp.get_value(
				"select_year_type",
				filep=cp.get_value("L_CODE")
			),
			reply_markup=await Keyboards.year_selection("bday")
		)
	elif buy_name == "key":
		await bot.send_message(
			message.chat.id,
			cp.get_value(
				"",
				filep=cp.get_value("L_CODE")
			),
			reply_markup=await Keyboards.day_selection("key")
		)

	#MESSAGES['successful_payment'].format(
	#       total_amount=message.successful_payment.total_amount // 100,
	#       currency=message.successful_payment.currency
	
@dp.message_handler(commands=["test"])
async def test_event(message: types.Message, state: FSMContext):
	# await message.reply(cp.get_value("code_2_1_m", filep=cp.get_value("L_CODE")))
	await message.reply(cp.get_value("code_8_1", filep=cp.get_value("L_CODE")))

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

@dp.callback_query_handler(dialog_cal_callback.filter(), state=["*"])#GrabName.bday
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
	selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
	if selected:
		async with state.proxy() as data:
			if "new_date" not in data:
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
			else:
				data["year"] = date.strftime("%d/%m/%Y")
				del data["new_date"]
				if data["feature"] == "bday":

					allready_sum = await calcerYear(int(date.strftime("%Y")), int(date.strftime("%m")), int(date.strftime("%d")))

					key_list = cp.get_key_list(filep="ru_RU")

					key_values = []
					for i in key_list:
						if f"code_{allready_sum}" in i[1]:
							if "m" in i[1] or "w" in i[1]:
								user_obj = await db.find_q("users", {"telegram_id":callback_query.from_user.id})
								if user_obj["gender"][0] == i[1][-1]:
									key_values.append(i[1])
							else:
								key_values.append(i[1])

					for i in key_values:
						await callback_query.message.answer(cp.get_value(i, filep="ru_RU"))

					await callback_query.message.answer(cp.get_value("welcome_text", filep=cp.get_value("L_CODE")), reply_markup=await Keyboards.mainmenu_board())


async def calcerYear(user_bday_year, user_bday_mon, user_bday_day):
	user_sum = await sumOfDigits(user_bday_year)
	if user_sum > 22:
		while user_sum > 22:
			user_sum = user_sum - 22

	now = datetime.datetime.now()
	world_sum = await sumOfDigits(now.year)
	if world_sum > 22:
		while world_sum > 22:
			world_sum = world_sum - 22

	all_sum = user_sum + world_sum
	if all_sum > 22:
		while all_sum > 22:
			all_sum = all_sum - 22

	if user_bday_mon > now.month:
		all_sum = all_sum - 1

	day_sum = user_bday_mon + user_bday_day

	if day_sum > 9:
		while day_sum > 9:
			day_sum = await sumOfDigits(day_sum)
	
	allready_sum = all_sum + day_sum

	if allready_sum > 9:
		while allready_sum > 9:
			allready_sum = await sumOfDigits(allready_sum)
	
	return allready_sum


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
		
		elif callback_query.data[0:5] == "paid_":
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
			feature = callback_query.data.split("_")[1]
			# print(cp.get_value(feature+"_lab", filep=cp.get_value("L_CODE")))

			await create_order(
				callback_query.message,
				str(
					cp.get_value(
						feature+"_lab",
						 filep=cp.get_value("L_CODE")
						)
				),
				str(
					cp.get_value(
						feature+"_desc",
						filep=cp.get_value("L_CODE")
						)
				),
				prices[feature],
				feature)

		elif callback_query.data[0:4] == "day_":
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

		elif callback_query.data[0:5] == "year_":
			await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
			if callback_query.data.split("_")[1] == "old":

				feature = callback_query.data.split("_")[-1]
				user_obj = await db.find_q("users", {"telegram_id":callback_query.from_user.id})
				user_bday_year = int(user_obj["bday"].split("/")[-1])
				user_bday_mon = int(user_obj["bday"].split("/")[1])
				user_bday_day = int(user_obj["bday"].split("/")[0])

				data["feature"] = feature
				data["year"] = user_bday_year

				allready_sum = await calcerYear(user_bday_year, user_bday_mon, user_bday_day)

				key_list = cp.get_key_list(filep="ru_RU")

				key_values = []
				for i in key_list:
					if f"code_{allready_sum}" in i[1]:
						if "m" in i[1] or "w" in i[1]:
							user_obj = await db.find_q("users", {"telegram_id":callback_query.from_user.id})
							if user_obj["gender"][0] == i[1][-1]:
								key_values.append(i[1])
						else:
							key_values.append(i[1])
								
				for i in key_values:
					await callback_query.message.answer(cp.get_value(i, filep="ru_RU"))

				await callback_query.message.answer(cp.get_value("welcome_text", filep=cp.get_value("L_CODE")), reply_markup=await Keyboards.mainmenu_board())

			elif callback_query.data.split("_")[1] == "new":
				feature = callback_query.data.split("_")[-1]
				data["new_date"] = "0"
				data["feature"] = feature
				await callback_query.message.answer(cp.get_value("pls_select_date", filep=cp.get_value("L_CODE")), reply_markup=await DialogCalendar().start_calendar())

@dp.message_handler(commands=['terms'])
async def process_terms_command(message: types.Message):
	await message.reply(cp.get_value("terms", filep=cp.get_value("L_CODE")), reply=False)

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)