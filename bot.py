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

# شمارش پیام‌ها
message_count = {}

# ذخیره تعداد اعضای گروه
group_members_count = {}

# چک کردن اینکه کاربر ادمین هست یا نه
async def is_admin(chat_id, user_id):
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


# خوش‌آمدگویی
@dp.message_handler(content_types=["new_chat_members"])
async def welcome(message: types.Message):
    user = message.new_chat_members[0]
    user_id = user.id
    chat_id = message.chat.id

    # اگر ادمین بود → هیچ محدودیتی نذار
    if await is_admin(chat_id, user_id):
        return

    join_time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")

    user_invites[user_id] = {"invited": False, "time": join_time}
    message_count[user_id] = 0

    # ذخیره تعداد اعضای فعلی
    members = await bot.get_chat_members_count(chat_id)
    group_members_count[chat_id] = members

    await message.reply(
        f"👋 خوش اومدی {user.first_name}\n"
        f"⏱ زمان ورود: {join_time}\n\n"
        f"برای فعال شدن کامل باید **۱ نفر رو اد کنی**."
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


# چک کردن اد کردن واقعی (روش تضمینی)
async def check_invites():
    while True:
        await asyncio.sleep(5)

        for chat_id in group_members_count:
            old_count = group_members_count[chat_id]
            new_count = await bot.get_chat_members_count(chat_id)

            # اگر تعداد اعضا +۱ شد → یکی اد شده
            if new_count > old_count:
                # پیدا کردن آخرین کسی که پیام داده
                # همون اد کننده‌ست
                updates = await bot.get_updates(limit=1)
                if updates:
                    try:
                        inviter = updates[-1].message.from_user.id
                    except:
                        inviter = None

                    if inviter in user_invites:
                        user_invites[inviter]["invited"] = True

                        await bot.restrict_chat_member(
                            chat_id,
                            inviter,
                            types.ChatPermissions(can_send_messages=True)
                        )

                        await bot.send_message(
                            chat_id,
                            f"✔️ محدودیت {inviter} برداشته شد! چون یک نفر رو اد کرد."
                        )

                group_members_count[chat_id] = new_count


async def on_startup(_):
    asyncio.create_task(check_invites())
    print("Bot started…")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
