from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8959678138:AAEMlwk9UHWBASE-R5ZLk8V9Wyqk7DT6KqI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def is_admin(chat_id, user_id):
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


# وقتی تازه وارد میشه → نصفه محدود میشه (دکمه کار می‌کنه)
@dp.message_handler(content_types=["new_chat_members"])
async def welcome(message: types.Message):
    new_user = message.new_chat_members[0]
    chat_id = message.chat.id

    if await is_admin(chat_id, new_user.id):
        return

    # نصفه محدود (فقط پیام نمی‌تونه بده)
    await bot.restrict_chat_member(
        chat_id,
        new_user.id,
        types.ChatPermissions(
            can_send_messages=False,      # پیام ممنوع
            can_send_media_messages=True, # دکمه کار می‌کنه
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("من اد کردم ✔️", callback_data=f"unlock_{new_user.id}"))

    await message.reply(
        f"👋 خوش اومدی {new_user.first_name}\n\n"
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
