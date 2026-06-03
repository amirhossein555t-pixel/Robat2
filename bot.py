import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8959678138:AAEMlwk9UHWBASE-R5ZLk8V9Wyqk7DT6KqI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

BANNED_WORDS = ["بیو", "بیوم", "بیوگرافی", "کانفینگ", "گیگ"]
LINK_REGEX = r"(https?://|t\.me/|@[\w_]+|bit\.ly|tinyurl)"

message_count = {}
user_invites = {}
group_member_count = {}

async def is_admin(chat_id, user_id):
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


@dp.message_handler(content_types=["new_chat_members"])
async def welcome(message: types.Message):
    user = message.new_chat_members[0]
    user_id = user.id
    chat_id = message.chat.id

    if await is_admin(chat_id, user_id):
        return

    join_time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")

    message_count[user_id] = 0
    user_invites[user_id] = False

    group_member_count[chat_id] = await bot.get_chat_members_count(chat_id)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("من اد کردم ✔️", callback_data=f"check_{user_id}"))

    await message.reply(
        f"👋 خوش اومدی {user.first_name}\n"
        f"⏱ زمان ورود: {join_time}\n\n"
        f"برای فعال شدن کامل باید **۱ نفر رو اد کنی**.",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def check_invite(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    chat_id = callback.message.chat.id

    old_count = group_member_count.get(chat_id, 0)
    new_count = await bot.get_chat_members_count(chat_id)

    if new_count > old_count:
        user_invites[user_id] = True

        await bot.restrict_chat_member(
            chat_id,
            user_id,
            types.ChatPermissions(can_send_messages=True)
        )

        await callback.message.edit_text("✔️ محدودیتت برداشته شد! مرسی که اد کردی ❤️")
    else:
        await callback.answer("داداش هنوز کسی رو اد نکردی 😐", show_alert=True)


@dp.message_handler()
async def filter_messages(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower() if message.text else ""

    if await is_admin(chat_id, user_id):
        return

    if re.search(LINK_REGEX, text):
        await message.delete()
        return

    for word in BANNED_WORDS:
        if word in text:
            await message.delete()
            return

    if user_id not in message_count:
        message_count[user_id] = 0

    message_count[user_id] += 1

    if message_count[user_id] == 3:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("من اد کردم ✔️", callback_data=f"check_{user_id}"))

        await message.reply(
            "🚫 **محدود شدی!**\n\n"
            "برای ادامه پیام دادن باید **۱ نفر رو اد کنی**.\n"
            "بعد از اد کردن روی دکمه زیر بزن:",
            reply_markup=keyboard
        )

        await bot.restrict_chat_member(
            chat_id,
            user_id,
            types.ChatPermissions(can_send_messages=False)
        )

    if message_count[user_id] > 3 and not user_invites.get(user_id, False):
        await message.delete()
        return


async def on_startup(_):
    print("Bot started…")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
