import re
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

# شمارش پیام‌ها
message_count = {}

# چک کردن اینکه کاربر ادمین هست یا نه
async def is_admin(chat_id, user_id):
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


# یک هندلر برای ورود و اد کردن
@dp.message_handler(content_types=["new_chat_members"])
async def handle_new_member(message: types.Message):
    chat_id = message.chat.id
    new_member = message.new_chat_members[0]
    inviter = message.from_user.id

    # اگر ادمین بود → هیچ محدودیتی نذار
    if await is_admin(chat_id, new_member.id):
        return

    # اگر خودش وارد شده (inviter == new_member)
    if inviter == new_member.id:
        join_time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")

        user_invites[new_member.id] = {"invited": False, "time": join_time}
        message_count[new_member.id] = 0

        await message.reply(
            f"👋 خوش اومدی {new_member.first_name}\n"
            f"⏱ زمان ورود: {join_time}\n\n"
            f"برای فعال شدن کامل باید **۱ نفر رو اد کنی**."
        )
        return

    # اگر کسی رو اد کرده
    if inviter in user_invites:
        user_invites[inviter]["invited"] = True

        # برداشتن محدودیت
        await bot.restrict_chat_member(
            chat_id,
            inviter,
            types.ChatPermissions(can_send_messages=True)
        )

        await message.reply(
            f"✔️ {message.from_user.first_name} یک نفر اد کرد و محدودیتش برداشته شد!"
        )


# پاک کردن لینک و کلمات ممنوعه + محدودیت ۳ پیام
@dp.message_handler()
async def filter_messages(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower() if message.text else ""

    # اگر ادمین بود → هیچ محدودیتی اعمال نشه
    if await is_admin(chat_id, user_id):
        return

    # پاک کردن لینک
    if re.search(LINK_REGEX, text):
        await message.delete()
        return

    # پاک کردن کلمات ممنوعه
    for word in BANNED_WORDS:
        if word in text:
            await message.delete()
            return

    # شمارش پیام‌ها
    if user_id not in message_count:
        message_count[user_id] = 0

    message_count[user_id] += 1

    # اگر ۳ پیام داد → هشدار بزرگ
    if message_count[user_id] == 3:
        await message.reply(
            "🚫 **محدود شدی!**\n\n"
            "📌 برای ادامه پیام دادن باید **۱ نفر رو به گروه اضافه کنی**.\n"
            "بعد از اد کردن، ربات خودش محدودیت رو برمی‌داره.\n\n"
            "⚠️ بدون اد کردن، پیام‌هات ارسال نمی‌شن."
        )

    # اگر بیشتر از ۳ پیام بده → پاک کن
    if message_count[user_id] > 3:
        await message.delete()
        return


async def on_startup(_):
    print("Bot started…")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
