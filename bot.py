```python
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiohttp import web

import config
from texts import *
from keyboards import *
from utils import get_random_wisdom

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class BuildStates(StatesGroup):
    waiting_goal = State()
    waiting_audience = State()
    waiting_technique = State()

@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(START_TEXT, reply_markup=main_menu_keyboard())

@dp.message(Command("techniques"))
async def command_techniques(message: Message):
    await message.answer(TECHNIQUES_MENU_TEXT, reply_markup=techniques_keyboard())

@dp.callback_query(F.data == "menu_techniques")
async def callback_techniques(callback: CallbackQuery):
    await callback.message.edit_text(TECHNIQUES_MENU_TEXT, reply_markup=techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "menu_build")
async def callback_build(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(BUILD_START)
    await callback.message.answer(BUILD_GOAL)
    await state.set_state(BuildStates.waiting_goal)
    await callback.answer()

@dp.callback_query(F.data == "menu_wisdom")
async def callback_wisdom(callback: CallbackQuery):
    wisdom = get_random_wisdom()
    await callback.message.edit_text(wisdom, reply_markup=back_to_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "menu_train")
async def callback_train(callback: CallbackQuery):
    await callback.message.edit_text(TRAIN_TEXT, reply_markup=back_to_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "tech_truisms")
async def callback_truisms(callback: CallbackQuery):
    await callback.message.edit_text(TRUISMS_TEXT, reply_markup=back_to_techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "tech_choice")
async def callback_choice(callback: CallbackQuery):
    await callback.message.edit_text(CHOICE_TEXT, reply_markup=back_to_techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "tech_yeschain")
async def callback_yeschain(callback: CallbackQuery):
    await callback.message.edit_text(YESCHAIN_TEXT, reply_markup=back_to_techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "tech_because")
async def callback_because(callback: CallbackQuery):
    await callback.message.edit_text(BECAUSE_TEXT, reply_markup=back_to_techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "tech_utilization")
async def callback_utilization(callback: CallbackQuery):
    await callback.message.edit_text(UTILIZATION_TEXT, reply_markup=back_to_techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_to_techniques")
async def callback_back_to_techniques(callback: CallbackQuery):
    await callback.message.edit_text(TECHNIQUES_MENU_TEXT, reply_markup=techniques_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(START_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.message(Command("build"))
async def command_build(message: Message, state: FSMContext):
    await message.answer(BUILD_START)
    await message.answer(BUILD_GOAL)
    await state.set_state(BuildStates.waiting_goal)

@dp.message(Command("cancel"))
async def command_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Конструктор отменён. Возвращаюсь в главное меню.", reply_markup=main_menu_keyboard())

@dp.message(BuildStates.waiting_goal)
async def process_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.answer(BUILD_AUDIENCE)
    await state.set_state(BuildStates.waiting_audience)

@dp.message(BuildStates.waiting_audience)
async def process_audience(message: Message, state: FSMContext):
    await state.update_data(audience=message.text)
    await message.answer(BUILD_TECHNIQUE)
    await state.set_state(BuildStates.waiting_technique)

@dp.message(BuildStates.waiting_technique)
async def process_technique(message: Message, state: FSMContext):
    data = await state.get_data()
    goal = data.get('goal', 'не указана')
    audience = data.get('audience', 'не указан')
    technique = message.text
    generated = generate_phrase(goal, audience, technique)
    result = BUILD_RESULT_TEMPLATE.format(goal=goal, audience=audience, technique=technique, generated_phrase=generated)
    await message.answer(result)
    await state.clear()
    await message.answer("Что делаем дальше?", reply_markup=main_menu_keyboard())

@dp.message(Command("wisdom"))
async def command_wisdom(message: Message):
    wisdom = get_random_wisdom()
    await message.answer(wisdom, reply_markup=back_to_main_keyboard())

@dp.message(Command("train"))
async def command_train(message: Message):
    await message.answer(TRAIN_TEXT, reply_markup=back_to_main_keyboard())

@dp.message()
async def handle_other(message: Message):
    await message.answer("Используй команды из меню или кнопки ниже.", reply_markup=main_menu_keyboard())

async def web_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text='Bot is running'))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")
    await asyncio.Event().wait()

async def main():
    bot_task = asyncio.create_task(dp.start_polling(bot))
    server_task = asyncio.create_task(web_server())
    await asyncio.gather(bot_task, server_task)

if __name__ == '__main__':
    asyncio.run(main())
```
