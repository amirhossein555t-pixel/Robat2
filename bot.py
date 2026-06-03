import re
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ChatPermissions

TOKEN = "8959678138:AAEMlwk9UHWBASE-R5ZLk8V9Wyqk7DT6KqI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# لیست کلمات ممنوعه
BANNED_WORDS = ["بیو", "بیوم", "بیوگرافی", "کانفینگ", "گیگ"]

# تشخیص لینک
LINK_REGEX = r"(https?://|t\.me/|@[\w_]+|bit\.ly|tinyurl)"

# ذخیره وضعیت اد کردن
user_invites = {}

# خوش‌آمدگویی
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("ربات مدیریت گروه فعال است ✔️")


# وقتی کسی وارد گروه می‌شود
@dp.chat_member()
async def on_user_join(event: types.ChatMemberUpdated):
    if event.new_chat_member.status == "member":
        user_id = event.new_chat_member.user.id
        chat_id = event.chat.id

        # محدودیت اولیه (فقط خواندن)
        await bot.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )

        # ذخیره زمان ورود
        join_time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
        user_invites[user_id] = {"invited": False, "time": join_time}

        await bot.send_message(
            chat_id,
            f"👋 خوش اومدی {event.new_chat_member.user.first_name}\n"
            f"⏱ زمان ورود: {join_time}\n\n"
            f"برای فعال شدن پیام‌دادن باید **۱ نفر رو اد کنی**."
        )


# تشخیص اد کردن عضو جدید
@dp.chat_member()
async def detect_invite(event: types.ChatMemberUpdated):
    if event.new_chat_member.status == "member":
        inviter = event.from_user.id
        if inviter in user_invites:
            user_invites[inviter]["invited"] = True

            # برداشتن محدودیت
            await bot.restrict_chat_member(
                event.chat.id,
                inviter,
                ChatPermissions(can_send_messages=True)
            )

            await bot.send_message(
                event.chat.id,
                f"✔️ {event.from_user.first_name} یک نفر اد کرد و محدودیتش برداشته شد!"
            )


# پاک کردن لینک و کلمات ممنوعه
@dp.message()
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


# حالت B → اگر ۵ دقیقه گذشت و کسی رو اد نکرد، محدود بمونه
async def check_invites():
    while True:
        await asyncio.sleep(300)  # هر ۵ دقیقه
        for user_id, data in list(user_invites.items()):
            if not data["invited"]:
                # هنوز کسی رو اد نکرده → محدودیت باقی می‌مونه
                pass


async def main():
    asyncio.create_task(check_invites())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
