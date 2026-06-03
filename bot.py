from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import re

TOKEN = "8959678138:AAEMlwk9UHWBASE-R5ZLk8V9Wyqk7DT6KqI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

BANNED_WORDS = ["بیو", "بیوم", "بیوگرافی", "کانفینگ", "گیگ"]
LINK_REGEX = r"(https?://|t\.me/|@[\w_]+|bit\.ly|tinyurl)"

async def is_admin(chat_id, user_id):
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


# وقتی تازه وارد میشه → کامل محدود میشه
@dp.message_handler(content_types=["new_chat_members"])
async def welcome(message: types.Message):
    user = message.new_chat_members[0]
    user_id = user.id
    chat_id = message.chat.id

    # ادمین‌ها محدود نشن
    if await is_admin(chat_id, user_id):
        return

    # بستن کامل پیام دادن
    await bot.restrict_chat_member(
        chat_id,
        user_id,
        types.ChatPermissions(can_send_messages=False)
    )

    # دکمه برای آزاد شدن
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("من اد کردم ✔️", callback_data=f"unlock_{user_id}"))

    await message.reply(
        f"👋 خوش اومدی {user.first_name}\n\n"
        f"برای فعال شدن باید **۱ نفر رو اد کنی**.\n"
        f"بعد از اد کردن روی دکمه زیر بزن:",
        reply_markup=keyboard
    )


# دکمه آزادسازی
@dp.callback_query_handler(lambda c: c.data.startswith("unlock_"))
async def unlock(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    chat_id = callback.message.chat.id

    # آزاد کردن کامل
    await bot.restrict_chat_member(
        chat_id,
        user_id,
        types.ChatPermissions(can_send_messages=True)
    )

    await callback.message.edit_text("✔️ محدودیتت برداشته شد! ❤️")


# فیلتر پیام‌ها (برای کسانی که هنوز محدودن)
@dp.message_handler()
async def filter_messages(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower() if message.text else ""

    # ادمین‌ها آزاد
    if await is_admin(chat_id, user_id):
        return

    # اگر محدود بود → پیام حذف بشه
    member = await bot.get_chat_member(chat_id, user_id)
    if not member.can_send_messages:
        await message.delete()
        return

    # پاک کردن لینک و کلمات ممنوعه
    if re.search(LINK_REGEX, text):
        await message.delete()
        return

    for word in BANNED_WORDS:
        if word in text:
            await message.delete()
            return


async def on_startup(_):
    print("Bot started…")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
