from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8959678138:AAEMlwk9UHWBASE-R5ZLk8V9Wyqk7DT6KqI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def is_admin(chat_id, user_id):
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


# وقتی تازه وارد میشه → کامل بسته میشه
@dp.message_handler(content_types=["new_chat_members"])
async def welcome(message: types.Message):
    new_user = message.new_chat_members[0]
    chat_id = message.chat.id

    if await is_admin(chat_id, new_user.id):
        return

    await bot.restrict_chat_member(
        chat_id,
        new_user.id,
        types.ChatPermissions(can_send_messages=False)
    )

    await message.reply(
        f"👋 خوش اومدی {new_user.first_name}\n\n"
        f"برای فعال شدن باید **۱ نفر رو اد کنی**."
    )


# تشخیص اد کردن واقعی (تنها روش درست)
@dp.chat_member_handler()
async def detect_invite(update: types.ChatMemberUpdated):
    chat_id = update.chat.id

    # کسی که اد شده
    new_user = update.new_chat_member.user

    # کسی که اد کرده
    inviter = update.from_user.id

    # اگر خودش وارد شده → اد نیست
    if inviter == new_user.id:
        return

    # اگر ادمین بود → کاری نکن
    if await is_admin(chat_id, inviter):
        return

    # آزاد کردن اد کننده
    await bot.restrict_chat_member(
        chat_id,
        inviter,
        types.ChatPermissions(can_send_messages=True)
    )

    await bot.send_message(
        chat_id,
        f"✔️ {update.from_user.first_name} یک نفر رو اد کرد و محدودیتش برداشته شد!"
    )


# جلوگیری از پیام دادن افراد محدود
@dp.message_handler()
async def block_limited(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if await is_admin(chat_id, user_id):
        return

    member = await bot.get_chat_member(chat_id, user_id)

    if not member.can_send_messages:
        await message.delete()
        return


async def on_startup(_):
    print("Bot started…")


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
