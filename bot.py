import re
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8959678138:AAEMlwk9UHWBASE-R5ZLk8V9Wyqk7DT6KqI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# کلمات ممنوعه
BANNED_WORDS = ["بیو", "بیوم", "بیوگرافی", "کانفینگ", "گیگ"]

# تشخیص لینک
LINK_REGEX = r"(https?://|t\.me/|@[\w_]+|bit\.ly|tinyurl)"

# ذخیره وضعیت اد کردن
user_invites = {}

# خوش‌آمدگویی
@dp.message_handler(content_types=["new_chat_members"])
async def welcome(message: types.Message):
    user = message.new_chat_members[0]
    user_id = user.id
    chat_id = message.chat.id

    join_time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")

    user_invites[user_id] = {"invited": False, "time": join_time}

    await message.reply(
        f"👋 خوش اومدی {user.first_name}\n"
        f"⏱ زمان ورود: {join_time}\n\n"
        f"برای فعال شدن کامل باید **۱ نفر رو اد کنی**."
    )


# تشخیص اد کردن عضو جدید
@dp.message_handler(content_types=["new_chat_members"])
async def detect_invite(message: types.Message):
    inviter = message.from_user.id

    if inviter in user_invites:
        user_invites[inviter]["invited"] = True
        await message.reply(
            f"✔️ {message.from_user.first_name} یک نفر اد کرد و محدودیتش برداشته شد!"
        )


# پاک کردن لینک و کلمات ممنوعه
@dp.message_handler()
async def filter_messages(message: types.Message):
    text = message.text.lower() if message.text else ""

    # پاک کردن لینک
    if re.search(LINK_REGEX, text):
        await message.delete()
        return

    # پاک کردن کلمات ممنوعه
    for word in BANNED_WORDS:
        if word in text:
            await message.delete()
            return


# حالت B → هر ۵ دقیقه چک کنه کی اد نکرده
async def check_invites():
    while True:
        await asyncio.sleep(300)
        for user_id, data in list(user_invites.items()):
            if not data["invited"]:
                pass  # فعلاً کاری نمی‌کنیم، فقط حالت B فعال است


async def on_startup(_):
    asyncio.create_task(check_invites())
    print("Bot started…")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
