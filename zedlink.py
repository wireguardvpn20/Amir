"""
🧬رایگان FREE🧬

@Confingfree2025
•-•-•-•-•-•
@botsaz04bot   رباتساز تیتان 
•-•-•-•-•-•
@TITAN0_10BOT  
•-•-•-•-•-•
@TITAN0_0BOT
•-•-•-•-•-•
@sourcetitan
•-•-•-•-•-•
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

import json

import os

from datetime import datetime, timedelta

import re

import asyncio

from collections import defaultdict



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)



# تنظیمات

BOT_TOKEN = "TITAN" # توکن بات

DATA_FILE = "group_data.json"



# دیتابیس

def load_data():

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, 'r', encoding='utf-8') as f:

            return json.load(f)

    return {}



def save_data(data):

    with open(DATA_FILE, 'w', encoding='utf-8') as f:

        json.dump(data, f, indent=4, ensure_ascii=False)



data = load_data()



# ذخیره موقت برای spam detection

user_messages = defaultdict(list)

user_warnings = defaultdict(int)



# تنظیمات پیش‌فرض گروه

DEFAULT_SETTINGS = {

    "anti_spam": True,

    "anti_link": True,

    "anti_forward": True,

    "anti_bot": True,

    "anti_arabic": False,

    "anti_sticker": False,

    "anti_gif": False,

    "anti_voice": False,

    "anti_video": False,

    "anti_photo": False,

    "welcome_msg": True,

    "goodbye_msg": True,

    "max_warnings": 3,

    "captcha": True,

    "auto_delete_commands": True,

    "lock_group": False,

    "anti_flood": True,

    "flood_limit": 5,

    "flood_time": 10,

    "ban_words": [],

    "whitelist_users": [],

    "mute_new_users": False,

    "verify_timeout": 120

}



# گرفتن تنظیمات گروه

def get_group_settings(chat_id):

    chat_id_str = str(chat_id)

    if chat_id_str not in data:

        data[chat_id_str] = {

            "settings": DEFAULT_SETTINGS.copy(),

            "admins": [],

            "banned_users": [],

            "muted_users": [],

            "warnings": {},

            "stats": {

                "total_messages": 0,

                "deleted_messages": 0,

                "banned_users": 0,

                "kicked_users": 0

            },

            "pending_verification": {}

        }

        save_data(data)

    return data[chat_id_str]



# بررسی ادمین بودن

async def is_admin(update: Update, user_id: int) -> bool:

    chat = update.effective_chat

    member = await chat.get_member(user_id)

    return member.status in ['creator', 'administrator']



# دستور Start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == 'private':

        keyboard = [

            [InlineKeyboardButton("➕ افزودن به گروه", url=f"https://t.me/{context.bot.username}?startgroup=true")],

            [InlineKeyboardButton("📚 راهنما", callback_data="help"), 

             InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings_private")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        text = """

🛡 <b>ربات ضد اسپم و مدیریت گروه حرفه‌ای</b>



✨ <b>امکانات:</b>

- 🚫 ضد اسپم هوشمند

- 🔗 حذف خودکار لینک

- 🤖 شناسایی و مسدودسازی ربات‌های مزاحم

- 📝 سیستم اخطار سه مرحله‌ای

- 🔐 تایید هویت با کپچا

- 📊 آمارگیری کامل

- 👋 پیام خوش‌آمدگویی سفارشی

- 🔒 قفل انواع محتوا

- ⚡️ ضد فلود

- 📋 لیست سفید کاربران

- 🗑 حذف خودکار دستورات



👨‍💼 <b>برای استفاده:</b>

ربات را به گروه خود اضافه کرده و ادمین کنید



⚠️ <b>دسترسی‌های لازم:</b>

- حذف پیام

- محدود کردن کاربران

- مسدود کردن کاربران

- دعوت کاربر

"""

        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

    else:

        await update.message.reply_text("✅ ربات آماده است! از /panel برای دسترسی به پنل مدیریت استفاده کنید.")



# پنل مدیریت

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == 'private':

        await update.message.reply_text("⚠️ این دستور فقط در گروه‌ها قابل استفاده است.")

        return

    

    if not await is_admin(update, update.effective_user.id):

        await update.message.reply_text("⛔️ فقط ادمین‌ها می‌توانند از این دستور استفاده کنند.")

        return

    

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    

    keyboard = [

        [InlineKeyboardButton("🚫 ضد اسپم", callback_data=f"toggle_anti_spam"),

         InlineKeyboardButton("🔗 ضد لینک", callback_data=f"toggle_anti_link")],

        [InlineKeyboardButton("📤 ضد فوروارد", callback_data=f"toggle_anti_forward"),

         InlineKeyboardButton("🤖 ضد ربات", callback_data=f"toggle_anti_bot")],

        [InlineKeyboardButton("🔐 کپچا", callback_data=f"toggle_captcha"),

         InlineKeyboardButton("⚡️ ضد فلود", callback_data=f"toggle_anti_flood")],

        [InlineKeyboardButton("🔒 قفل محتوا", callback_data="lock_content"),

         InlineKeyboardButton("📋 کلمات ممنوع", callback_data="ban_words")],

        [InlineKeyboardButton("👥 لیست سفید", callback_data="whitelist"),

         InlineKeyboardButton("📊 آمار", callback_data="stats")],

        [InlineKeyboardButton("⚙️ تنظیمات پیشرفته", callback_data="advanced_settings")]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    stats = settings['stats']

    s = settings['settings']

    

    text = f"""

🛡 <b>پنل مدیریت گروه</b>



📊 <b>وضعیت فعلی:</b>



🚫 ضد اسپم: {'✅' if s['anti_spam'] else '❌'}

🔗 ضد لینک: {'✅' if s['anti_link'] else '❌'}

📤 ضد فوروارد: {'✅' if s['anti_forward'] else '❌'}

🤖 ضد ربات: {'✅' if s['anti_bot'] else '❌'}

🔐 کپچا: {'✅' if s['captcha'] else '❌'}

⚡️ ضد فلود: {'✅' if s['anti_flood'] else '❌'}



📈 <b>آمار:</b>

💬 پیام‌ها: {stats['total_messages']}

🗑 حذف شده: {stats['deleted_messages']}

🚫 بن شده: {stats['banned_users']}

⚠️ اخطارها: {len(settings['warnings'])}



🔻 یک گزینه را انتخاب کنید:

"""

    

    msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

    

    if s['auto_delete_commands']:

        await asyncio.sleep(3)

        await update.message.delete()



# مدیریت callback ها

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    

    if not await is_admin(update, query.from_user.id):

        await query.answer("⛔️ شما ادمین نیستید!", show_alert=True)

        return

    

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    

    # Toggle تنظیمات

    if query.data.startswith("toggle_"):

        setting_name = query.data.replace("toggle_", "")

        settings['settings'][setting_name] = not settings['settings'][setting_name]

        save_data(data)

        

        status = "فعال ✅" if settings['settings'][setting_name] else "غیرفعال ❌"

        await query.answer(f"{setting_name} {status}", show_alert=True)

        

        # به‌روزرسانی پیام

        await update_panel_message(query, chat_id)

    

    elif query.data == "lock_content":

        await show_lock_content_menu(query, chat_id)

    

    elif query.data == "ban_words":

        await show_ban_words_menu(query, chat_id)

    

    elif query.data == "whitelist":

        await show_whitelist_menu(query, chat_id)

    

    elif query.data == "stats":

        await show_stats(query, chat_id)

    

    elif query.data == "advanced_settings":

        await show_advanced_settings(query, chat_id)

    

    elif query.data.startswith("lock_"):

        content_type = query.data.replace("lock_", "")

        settings['settings'][f'anti_{content_type}'] = not settings['settings'][f'anti_{content_type}']

        save_data(data)

        await show_lock_content_menu(query, chat_id)



async def update_panel_message(query, chat_id):

    settings = get_group_settings(chat_id)

    stats = settings['stats']

    s = settings['settings']

    

    keyboard = [

        [InlineKeyboardButton("🚫 ضد اسپم", callback_data=f"toggle_anti_spam"),

         InlineKeyboardButton("🔗 ضد لینک", callback_data=f"toggle_anti_link")],

        [InlineKeyboardButton("📤 ضد فوروارد", callback_data=f"toggle_anti_forward"),

         InlineKeyboardButton("🤖 ضد ربات", callback_data=f"toggle_anti_bot")],

        [InlineKeyboardButton("🔐 کپچا", callback_data=f"toggle_captcha"),

         InlineKeyboardButton("⚡️ ضد فلود", callback_data=f"toggle_anti_flood")],

        [InlineKeyboardButton("🔒 قفل محتوا", callback_data="lock_content"),

         InlineKeyboardButton("📋 کلمات ممنوع", callback_data="ban_words")],

        [InlineKeyboardButton("👥 لیست سفید", callback_data="whitelist"),

         InlineKeyboardButton("📊 آمار", callback_data="stats")],

        [InlineKeyboardButton("⚙️ تنظیمات پیشرفته", callback_data="advanced_settings")]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    text = f"""

🛡 <b>پنل مدیریت گروه</b>



📊 <b>وضعیت فعلی:</b>



🚫 ضد اسپم: {'✅' if s['anti_spam'] else '❌'}

🔗 ضد لینک: {'✅' if s['anti_link'] else '❌'}

📤 ضد فوروارد: {'✅' if s['anti_forward'] else '❌'}

🤖 ضد ربات: {'✅' if s['anti_bot'] else '❌'}

🔐 کپچا: {'✅' if s['captcha'] else '❌'}

⚡️ ضد فلود: {'✅' if s['anti_flood'] else '❌'}



📈 <b>آمار:</b>

💬 پیام‌ها: {stats['total_messages']}

🗑 حذف شده: {stats['deleted_messages']}

🚫 بن شده: {stats['banned_users']}

⚠️ اخطارها: {len(settings['warnings'])}



🔻 یک گزینه را انتخاب کنید:

"""

    

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')



async def show_lock_content_menu(query, chat_id):

    settings = get_group_settings(chat_id)

    s = settings['settings']

    

    keyboard = [

        [InlineKeyboardButton(f"{'✅' if s['anti_sticker'] else '❌'} استیکر", callback_data="lock_sticker"),

         InlineKeyboardButton(f"{'✅' if s['anti_gif'] else '❌'} GIF", callback_data="lock_gif")],

        [InlineKeyboardButton(f"{'✅' if s['anti_voice'] else '❌'} ویس", callback_data="lock_voice"),

         InlineKeyboardButton(f"{'✅' if s['anti_video'] else '❌'} ویدیو", callback_data="lock_video")],

        [InlineKeyboardButton(f"{'✅' if s['anti_photo'] else '❌'} عکس", callback_data="lock_photo"),

         InlineKeyboardButton(f"{'✅' if s['anti_arabic'] else '❌'} عربی", callback_data="lock_arabic")],

        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    text = """

🔒 <b>قفل محتوا</b>



با فعال کردن هر گزینه، آن نوع محتوا خودکار حذف می‌شود.



🔻 روی هر کدام کلیک کنید تا فعال/غیرفعال شود:

"""

    

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')



async def show_stats(query, chat_id):

    settings = get_group_settings(chat_id)

    stats = settings['stats']

    

    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    text = f"""

📊 <b>آمار کامل گروه</b>



💬 <b>پیام‌ها:</b>

- کل پیام‌ها: {stats['total_messages']}

- حذف شده: {stats['deleted_messages']}



👥 <b>کاربران:</b>

- بن شده: {stats['banned_users']}

- کیک شده: {stats['kicked_users']}

- در لیست اخطار: {len(settings['warnings'])}



🔒 <b>محدودیت‌ها:</b>

- کاربران سفید: {len(settings['settings']['whitelist_users'])}

- کلمات ممنوع: {len(settings['settings']['ban_words'])}

- کاربران میوت: {len(settings['muted_users'])}



📅 <b>زمان:</b>

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""

    

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')



async def show_advanced_settings(query, chat_id):

    settings = get_group_settings(chat_id)

    s = settings['settings']

    

    keyboard = [

        [InlineKeyboardButton("👋 پیام خوش‌آمد", callback_data="toggle_welcome_msg"),

         InlineKeyboardButton("👋 پیام خداحافظی", callback_data="toggle_goodbye_msg")],

        [InlineKeyboardButton("🗑 حذف دستورات", callback_data="toggle_auto_delete_commands"),

         InlineKeyboardButton("🔇 میوت تازه‌واردها", callback_data="toggle_mute_new_users")],

        [InlineKeyboardButton(f"⚠️ حد اخطار: {s['max_warnings']}", callback_data="set_max_warnings"),

         InlineKeyboardButton(f"⏱ تایم فلود: {s['flood_time']}s", callback_data="set_flood_time")],

        [InlineKeyboardButton(f"💬 حد فلود: {s['flood_limit']}", callback_data="set_flood_limit"),

         InlineKeyboardButton(f"⏰ تایم کپچا: {s['verify_timeout']}s", callback_data="set_verify_timeout")],

        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    text = f"""

⚙️ <b>تنظیمات پیشرفته</b>



👋 پیام خوش‌آمد: {'✅' if s['welcome_msg'] else '❌'}

👋 پیام خداحافظی: {'✅' if s['goodbye_msg'] else '❌'}

🗑 حذف خودکار دستورات: {'✅' if s['auto_delete_commands'] else '❌'}

🔇 میوت تازه‌واردها: {'✅' if s['mute_new_users'] else '❌'}



⚠️ حداکثر اخطار: {s['max_warnings']}

💬 حد پیام فلود: {s['flood_limit']} پیام

⏱ زمان بررسی فلود: {s['flood_time']} ثانیه

⏰ زمان تایید کپچا: {s['verify_timeout']} ثانیه



🔻 یک گزینه را انتخاب کنید:

"""

    

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')



# مدیریت پیام‌ها

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == 'private':

        return

    

    chat_id = update.effective_chat.id

    user_id = update.effective_user.id

    message = update.message

    

    settings = get_group_settings(chat_id)

    s = settings['settings']

    

    # به‌روزرسانی آمار

    settings['stats']['total_messages'] += 1

    save_data(data)

    

    # بررسی ادمین

    if await is_admin(update, user_id):

        return

    

    # بررسی لیست سفید

    if user_id in s['whitelist_users']:

        return

    

    # بررسی میوت

    if user_id in settings['muted_users']:

        await message.delete()

        return

    

    # ضد فلود

    if s['anti_flood']:

        current_time = datetime.now()

        user_messages[user_id].append(current_time)

        

        # حذف پیام‌های قدیمی

        user_messages[user_id] = [

            msg_time for msg_time in user_messages[user_id]

            if (current_time - msg_time).seconds < s['flood_time']

        ]

        

        if len(user_messages[user_id]) > s['flood_limit']:

            await message.delete()

            settings['stats']['deleted_messages'] += 1

            await add_warning(update, context, user_id, chat_id, "فلود")

            return

    

    # ضد لینک

    if s['anti_link']:

        url_pattern = r'(https?://|www\.|t\.me/|@\w+)'

        if re.search(url_pattern, message.text or message.caption or ''):

            await message.delete()

            settings['stats']['deleted_messages'] += 1

            await add_warning(update, context, user_id, chat_id, "ارسال لینک")

            return

    

    # ضد فوروارد

    if s['anti_forward'] and message.forward_date:

        await message.delete()

        settings['stats']['deleted_messages'] += 1

        await add_warning(update, context, user_id, chat_id, "فوروارد پیام")

        return

    

    # کلمات ممنوع

    if s['ban_words']:

        text_to_check = (message.text or message.caption or '').lower()

        for word in s['ban_words']:

            if word.lower() in text_to_check:

                await message.delete()

                settings['stats']['deleted_messages'] += 1

                await add_warning(update, context, user_id, chat_id, f"استفاده از کلمه ممنوع: {word}")

                return

    

    # ضد عربی

    if s['anti_arabic']:

        arabic_pattern = r'[\u0600-\u06FF]'

        text = message.text or message.caption or ''

        if re.search(arabic_pattern, text):

            await message.delete()

            settings['stats']['deleted_messages'] += 1

            return

    

    # قفل محتوا

    if s['anti_sticker'] and message.sticker:

        await message.delete()

        settings['stats']['deleted_messages'] += 1

        return

    

    if s['anti_gif'] and message.animation:

        await message.delete()

        settings['stats']['deleted_messages'] += 1

        return

    

    if s['anti_voice'] and message.voice:

        await message.delete()

        settings['stats']['deleted_messages'] += 1

        return

    

    if s['anti_video'] and message.video:

        await message.delete()

        settings['stats']['deleted_messages'] += 1

        return

    

    if s['anti_photo'] and message.photo:

        await message.delete()

        settings['stats']['deleted_messages'] += 1

        return



# سیستم اخطار

async def add_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int, reason: str):

    settings = get_group_settings(chat_id)

    

    user_id_str = str(user_id)

    if user_id_str not in settings['warnings']:

        settings['warnings'][user_id_str] = []

    

    settings['warnings'][user_id_str].append({

        "reason": reason,

        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    })

    

    warning_count = len(settings['warnings'][user_id_str])

    max_warnings = settings['settings']['max_warnings']

    

    if warning_count >= max_warnings:

        # بن کاربر

        try:

            await context.bot.ban_chat_member(chat_id, user_id)

            settings['stats']['banned_users'] += 1

            del settings['warnings'][user_id_str]

            save_data(data)

            

            await context.bot.send_message(

                chat_id,

                f"🚫 کاربر <a href='tg://user?id={user_id}'>#{user_id}</a> به دلیل دریافت {max_warnings} اخطار مسدود شد.\n\n"

                f"📝 دلیل آخرین اخطار: {reason}",

                parse_mode='HTML'

            )

        except Exception as e:

            logger.error(f"Error banning user: {e}")

    else:

        save_data(data)

        await context.bot.send_message(

            chat_id,

            f"⚠️ اخطار {warning_count}/{max_warnings} به <a href='tg://user?id={user_id}'>کاربر</a>\n\n"

            f"📝 دلیل: {reason}",

            parse_mode='HTML'

        )



# عضو جدید

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    s = settings['settings']

    

    for new_user in update.message.new_chat_members:

        # ضد ربات

        if s['anti_bot'] and new_user.is_bot:

            try:

                await context.bot.ban_chat_member(chat_id, new_user.id)

                await update.message.delete()

                settings['stats']['banned_users'] += 1

                save_data(data)

            except:

                pass

            return

        

        # کپچا

        if s['captcha'] and not new_user.is_bot:

            await show_captcha(update, context, new_user, chat_id)

        

        # پیام خوش‌آمد

        if s['welcome_msg']:

            welcome_text = f"""

👋 <b>خوش آمدید</b> <a href='tg://user?id={new_user.id}'>{new_user.first_name}</a>



به گروه ما خوش آمدید!



📋 لطفاً قوانین گروه را رعایت کنید.

"""

            msg = await context.bot.send_message(chat_id, welcome_text, parse_mode='HTML')

            await asyncio.sleep(30)

            await msg.delete()

        

        # میوت تازه‌واردها

        if s['mute_new_users']:

            settings['muted_users'].append(new_user.id)

            save_data(data)



# کپچا

async def show_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE, user, chat_id):

    import random

    

    num1 = random.randint(1, 10)

    num2 = random.randint(1, 10)

    answer = num1 + num2

    

    settings = get_group_settings(chat_id)

    settings['pending_verification'][str(user.id)] = {

        "answer": answer,

        "time": datetime.now().timestamp()

    }

    save_data(data)

    

    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"captcha_{user.id}_{i}") for i in range(answer-2, answer+3)]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    text = f"""

🔐 <b>تایید هویت</b>



سلام <a href='tg://user?id={user.id}'>{user.first_name}</a>



برای تایید اینکه ربات نیستید، به سوال زیر پاسخ دهید:



❓ {num1} + {num2} = ؟



⏰ زمان: {settings['settings']['verify_timeout']} ثانیه

"""

    

    msg = await context.bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode='HTML')

    

    # تایمر کپچا

    await asyncio.sleep(settings['settings']['verify_timeout'])

    

    if str(user.id) in settings['pending_verification']:

        try:

            await context.bot.ban_chat_member(chat_id, user.id)

            await msg.delete()

            settings['stats']['banned_users'] += 1

            del settings['pending_verification'][str(user.id)]

            save_data(data)

        except:

            pass



# پاسخ کپچا

async def captcha_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    

    data_parts = query.data.split('_')

    user_id = int(data_parts[1])

    user_answer = int(data_parts[2])

    

    if query.from_user.id != user_id:

        await query.answer("❌ این کپچا برای شما نیست!", show_alert=True)

        return

    

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    

    if str(user_id) not in settings['pending_verification']:

        return

    

    correct_answer = settings['pending_verification'][str(user_id)]['answer']

    

    if user_answer == correct_answer:

        del settings['pending_verification'][str(user_id)]

        save_data(data)

        await query.edit_message_text(

            f"✅ <a href='tg://user?id={user_id}'>کاربر</a> با موفقیت تایید شد!",

            parse_mode='HTML'

        )

        await asyncio.sleep(5)

        await query.message.delete()

    else:

        try:

            await context.bot.ban_chat_member(chat_id, user_id)

            del settings['pending_verification'][str(user_id)]

            settings['stats']['banned_users'] += 1

            save_data(data)

            await query.edit_message_text(

                f"❌ <a href='tg://user?id={user_id}'>کاربر</a> پاسخ اشتباه داد و مسدود شد!",

                parse_mode='HTML'

            )

            await asyncio.sleep(5)

            await query.message.delete()

        except Exception as e:

            logger.error(f"Error in captcha: {e}")



# خروج عضو

async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    s = settings['settings']

    

    left_user = update.message.left_chat_member

    

    if s['goodbye_msg']:

        goodbye_text = f"""

👋 <a href='tg://user?id={left_user.id}'>{left_user.first_name}</a> گروه را ترک کرد.



موفق باشید! 🌟

"""

        msg = await context.bot.send_message(chat_id, goodbye_text, parse_mode='HTML')

        await asyncio.sleep(20)

        await msg.delete()



# دستورات مدیریتی

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_name = update.message.reply_to_message.from_user.first_name

    

    try:

        await context.bot.ban_chat_member(chat_id, user_id)

        settings = get_group_settings(chat_id)

        settings['stats']['banned_users'] += 1

        settings['banned_users'].append(user_id)

        save_data(data)

        

        await update.message.reply_text(

            f"🚫 <a href='tg://user?id={user_id}'>{user_name}</a> با موفقیت مسدود شد!",

            parse_mode='HTML'

        )

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not context.args:

        await update.message.reply_text("⚠️ استفاده: /unban <user_id>")

        return

    

    chat_id = update.effective_chat.id

    user_id = int(context.args[0])

    

    try:

        await context.bot.unban_chat_member(chat_id, user_id)

        settings = get_group_settings(chat_id)

        if user_id in settings['banned_users']:

            settings['banned_users'].remove(user_id)

        save_data(data)

        

        await update.message.reply_text(

            f"✅ کاربر <code>{user_id}</code> از لیست مسدودی خارج شد.",

            parse_mode='HTML'

        )

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_name = update.message.reply_to_message.from_user.first_name

    

    try:

        await context.bot.ban_chat_member(chat_id, user_id)

        await context.bot.unban_chat_member(chat_id, user_id)

        

        settings = get_group_settings(chat_id)

        settings['stats']['kicked_users'] += 1

        save_data(data)

        

        await update.message.reply_text(

            f"👢 <a href='tg://user?id={user_id}'>{user_name}</a> از گروه اخراج شد!",

            parse_mode='HTML'

        )

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_name = update.message.reply_to_message.from_user.first_name

    

    # زمان میوت (پیش‌فرض: دائمی)

    mute_time = None

    if context.args:

        try:

            minutes = int(context.args[0])

            mute_time = datetime.now() + timedelta(minutes=minutes)

        except:

            pass

    

    try:

        permissions = ChatPermissions(can_send_messages=False)

        if mute_time:

            await context.bot.restrict_chat_member(chat_id, user_id, permissions, until_date=mute_time)

            time_text = f"برای {context.args[0]} دقیقه"

        else:

            await context.bot.restrict_chat_member(chat_id, user_id, permissions)

            time_text = "به صورت دائم"

            settings = get_group_settings(chat_id)

            settings['muted_users'].append(user_id)

            save_data(data)

        

        await update.message.reply_text(

            f"🔇 <a href='tg://user?id={user_id}'>{user_name}</a> {time_text} میوت شد!",

            parse_mode='HTML'

        )

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_name = update.message.reply_to_message.from_user.first_name

    

    try:

        permissions = ChatPermissions(

            can_send_messages=True,

            can_send_media_messages=True,

            can_send_polls=True,

            can_send_other_messages=True,

            can_add_web_page_previews=True,

            can_change_info=False,

            can_invite_users=True,

            can_pin_messages=False

        )

        await context.bot.restrict_chat_member(chat_id, user_id, permissions)

        

        settings = get_group_settings(chat_id)

        if user_id in settings['muted_users']:

            settings['muted_users'].remove(user_id)

        save_data(data)

        

        await update.message.reply_text(

            f"🔊 <a href='tg://user?id={user_id}'>{user_name}</a> آنمیوت شد!",

            parse_mode='HTML'

        )

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    reason = ' '.join(context.args) if context.args else "تخلف از قوانین"

    

    await add_warning(update, context, user_id, chat_id, reason)



async def unwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_id_str = str(user_id)

    

    settings = get_group_settings(chat_id)

    

    if user_id_str in settings['warnings'] and settings['warnings'][user_id_str]:

        settings['warnings'][user_id_str].pop()

        if not settings['warnings'][user_id_str]:

            del settings['warnings'][user_id_str]

        save_data(data)

        

        await update.message.reply_text(

            f"✅ یک اخطار از <a href='tg://user?id={user_id}'>کاربر</a> حذف شد.",

            parse_mode='HTML'

        )

    else:

        await update.message.reply_text("⚠️ این کاربر اخطاری ندارد.")



async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_id_str = str(user_id)

    user_name = update.message.reply_to_message.from_user.first_name

    

    settings = get_group_settings(chat_id)

    

    if user_id_str in settings['warnings'] and settings['warnings'][user_id_str]:

        warnings = settings['warnings'][user_id_str]

        text = f"⚠️ <b>اخطارهای</b> <a href='tg://user?id={user_id}'>{user_name}</a>\n\n"

        for i, warn in enumerate(warnings, 1):

            text += f"{i}. {warn['reason']} - {warn['time']}\n"

        text += f"\n📊 تعداد کل: {len(warnings)}/{settings['settings']['max_warnings']}"

    else:

        text = f"✅ <a href='tg://user?id={user_id}'>{user_name}</a> هیچ اخطاری ندارد."

    

    await update.message.reply_text(text, parse_mode='HTML')



async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام مورد نظر ریپلای کنید.")

        return

    

    try:

        await update.message.reply_to_message.pin()

        await update.message.reply_text("📌 پیام پین شد!")

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    chat_id = update.effective_chat.id

    

    try:

        await context.bot.unpin_all_chat_messages(chat_id)

        await update.message.reply_text("✅ تمام پیام‌های پین شده حذف شدند!")

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    chat_id = update.effective_chat.id

    

    try:

        permissions = ChatPermissions(can_send_messages=False)

        await context.bot.set_chat_permissions(chat_id, permissions)

        

        settings = get_group_settings(chat_id)

        settings['settings']['lock_group'] = True

        save_data(data)

        

        await update.message.reply_text("🔒 گروه قفل شد! فقط ادمین‌ها می‌توانند پیام بفرستند.")

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def unlock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    chat_id = update.effective_chat.id

    

    try:

        permissions = ChatPermissions(

            can_send_messages=True,

            can_send_media_messages=True,

            can_send_polls=True,

            can_send_other_messages=True,

            can_add_web_page_previews=True

        )

        await context.bot.set_chat_permissions(chat_id, permissions)

        

        settings = get_group_settings(chat_id)

        settings['settings']['lock_group'] = False

        save_data(data)

        

        await update.message.reply_text("🔓 گروه باز شد! همه می‌توانند پیام بفرستند.")

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام ابتدایی ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    start_message_id = update.message.reply_to_message.message_id

    end_message_id = update.message.message_id

    

    deleted = 0

    for msg_id in range(start_message_id, end_message_id + 1):

        try:

            await context.bot.delete_message(chat_id, msg_id)

            deleted += 1

            await asyncio.sleep(0.1)

        except:

            pass

    

    msg = await update.message.reply_text(f"🗑 {deleted} پیام حذف شد!")

    await asyncio.sleep(5)

    await msg.delete()



async def del_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام مورد نظر ریپلای کنید.")

        return

    

    try:

        await update.message.reply_to_message.delete()

        await update.message.delete()

    except Exception as e:

        await update.message.reply_text(f"❌ خطا: {str(e)}")



async def setwelcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not context.args:

        await update.message.reply_text(

            "⚠️ استفاده: /setwelcome <پیام>\n\n"

            "متغیرهای قابل استفاده:\n"

            "{name} - نام کاربر\n"

            "{username} - یوزرنیم کاربر\n"

            "{chat} - نام گروه"

        )

        return

    

    chat_id = update.effective_chat.id

    welcome_text = ' '.join(context.args)

    

    settings = get_group_settings(chat_id)

    settings['welcome_text'] = welcome_text

    save_data(data)

    

    await update.message.reply_text("✅ پیام خوش‌آمدگویی تنظیم شد!")



async def setgoodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not context.args:

        await update.message.reply_text(

            "⚠️ استفاده: /setgoodbye <پیام>\n\n"

            "متغیرهای قابل استفاده:\n"

            "{name} - نام کاربر\n"

            "{username} - یوزرنیم کاربر"

        )

        return

    

    chat_id = update.effective_chat.id

    goodbye_text = ' '.join(context.args)

    

    settings = get_group_settings(chat_id)

    settings['goodbye_text'] = goodbye_text

    save_data(data)

    

    await update.message.reply_text("✅ پیام خداحافظی تنظیم شد!")



async def addword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not context.args:

        await update.message.reply_text("⚠️ استفاده: /addword <کلمه>")

        return

    

    chat_id = update.effective_chat.id

    word = ' '.join(context.args)

    

    settings = get_group_settings(chat_id)

    if word not in settings['settings']['ban_words']:

        settings['settings']['ban_words'].append(word)

        save_data(data)

        await update.message.reply_text(f"✅ کلمه '{word}' به لیست ممنوع اضافه شد!")

    else:

        await update.message.reply_text("⚠️ این کلمه قبلاً اضافه شده است.")



async def removeword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not context.args:

        await update.message.reply_text("⚠️ استفاده: /removeword <کلمه>")

        return

    

    chat_id = update.effective_chat.id

    word = ' '.join(context.args)

    

    settings = get_group_settings(chat_id)

    if word in settings['settings']['ban_words']:

        settings['settings']['ban_words'].remove(word)

        save_data(data)

        await update.message.reply_text(f"✅ کلمه '{word}' از لیست ممنوع حذف شد!")

    else:

        await update.message.reply_text("⚠️ این کلمه در لیست نیست.")



async def listwords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    ban_words = settings['settings']['ban_words']

    

    if ban_words:

        text = "📋 <b>لیست کلمات ممنوع:</b>\n\n"

        for i, word in enumerate(ban_words, 1):

            text += f"{i}. {word}\n"

    else:

        text = "⚠️ هیچ کلمه ممنوعی تنظیم نشده است."

    

    await update.message.reply_text(text, parse_mode='HTML')



async def whitelist_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_name = update.message.reply_to_message.from_user.first_name

    

    settings = get_group_settings(chat_id)

    if user_id not in settings['settings']['whitelist_users']:

        settings['settings']['whitelist_users'].append(user_id)

        save_data(data)

        await update.message.reply_text(

            f"✅ <a href='tg://user?id={user_id}'>{user_name}</a> به لیست سفید اضافه شد!",

            parse_mode='HTML'

        )

    else:

        await update.message.reply_text("⚠️ این کاربر قبلاً در لیست سفید است.")



async def whitelist_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_admin(update, update.effective_user.id):

        return

    

    if not update.message.reply_to_message:

        await update.message.reply_text("⚠️ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")

        return

    

    chat_id = update.effective_chat.id

    user_id = update.message.reply_to_message.from_user.id

    user_name = update.message.reply_to_message.from_user.first_name

    

    settings = get_group_settings(chat_id)

    if user_id in settings['settings']['whitelist_users']:

        settings['settings']['whitelist_users'].remove(user_id)

        save_data(data)

        await update.message.reply_text(

            f"✅ <a href='tg://user?id={user_id}'>{user_name}</a> از لیست سفید حذف شد!",

            parse_mode='HTML'

        )

    else:

        await update.message.reply_text("⚠️ این کاربر در لیست سفید نیست.")



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    text = """

📚 <b>راهنمای کامل ربات</b>



<b>🔰 دستورات مدیریتی:</b>

/panel - پنل مدیریت

/ban - مسدود کردن کاربر

/unban - رفع مسدودی

/kick - اخراج کاربر

/mute - میوت کاربر

/unmute - آنمیوت کاربر

/warn - اخطار به کاربر

/unwarn - حذف اخطار

/warns - مشاهده اخطارهای کاربر

/pin - پین کردن پیام

/unpin - حذف پین

/lock - قفل گروه

/unlock - باز کردن گروه

/purge - حذف دسته‌جمعی پیام

/del - حذف پیام



<b>⚙️ تنظیمات:</b>

/setwelcome - تنظیم پیام خوش‌آمد

/setgoodbye - تنظیم پیام خداحافظی

/addword - افزودن کلمه ممنوع

/removeword - حذف کلمه ممنوع

/listwords - لیست کلمات ممنوع

/whitelistadd - افزودن به لیست سفید

/whitelistremove - حذف از لیست سفید



<b>ℹ️ اطلاعات:</b>

/help - نمایش این راهنما

/stats - آمار گروه

"""

    

    if update.callback_query:

        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    else:

        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')



async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == 'private':

        await update.message.reply_text("⚠️ این دستور فقط در گروه‌ها قابل استفاده است.")

        return

    

    chat_id = update.effective_chat.id

    settings = get_group_settings(chat_id)

    stats = settings['stats']

    

    text = f"""

📊 <b>آمار کامل گروه</b>



💬 <b>پیام‌ها:</b>

- کل پیام‌ها: {stats['total_messages']}

- حذف شده: {stats['deleted_messages']}



👥 <b>کاربران:</b>

- بن شده: {stats['banned_users']}

- کیک شده: {stats['kicked_users']}

- در لیست اخطار: {len(settings['warnings'])}



🔒 <b>محدودیت‌ها:</b>

- کاربران سفید: {len(settings['settings']['whitelist_users'])}

- کلمات ممنوع: {len(settings['settings']['ban_words'])}

- کاربران میوت: {len(settings['muted_users'])}



📅 <b>زمان:</b>

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""

    

    await update.message.reply_text(text, parse_mode='HTML')



# مدیریت callback بازگشت

async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    

    if query.data == "back_to_main":

        await update_panel_message(query, update.effective_chat.id)



# مدیریت خطاها

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    logger.error(f"Exception while handling an update: {context.error}")



# اجرای ربات

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    

    # Handler ها

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("panel", panel))

    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CommandHandler("stats", stats_command))

    

    # دستورات مدیریتی

    app.add_handler(CommandHandler("ban", ban_command))

    app.add_handler(CommandHandler("unban", unban_command))

    app.add_handler(CommandHandler("kick", kick_command))

    app.add_handler(CommandHandler("mute", mute_command))

    app.add_handler(CommandHandler("unmute", unmute_command))

    app.add_handler(CommandHandler("warn", warn_command))

    app.add_handler(CommandHandler("unwarn", unwarn_command))

    app.add_handler(CommandHandler("warns", warns_command))

    app.add_handler(CommandHandler("pin", pin_command))

    app.add_handler(CommandHandler("unpin", unpin_command))

    app.add_handler(CommandHandler("lock", lock_command))

    app.add_handler(CommandHandler("unlock", unlock_command))

    app.add_handler(CommandHandler("purge", purge_command))

    app.add_handler(CommandHandler("del", del_command))

    

    # تنظیمات

    app.add_handler(CommandHandler("setwelcome", setwelcome_command))

    app.add_handler(CommandHandler("setgoodbye", setgoodbye_command))

    app.add_handler(CommandHandler("addword", addword_command))

    app.add_handler(CommandHandler("removeword", removeword_command))

    app.add_handler(CommandHandler("listwords", listwords_command))

    app.add_handler(CommandHandler("whitelistadd", whitelist_add_command))

    app.add_handler(CommandHandler("whitelistremove", whitelist_remove_command))

    

    # Callback handlers

    app.add_handler(CallbackQueryHandler(captcha_callback, pattern=r"^captcha_"))

    app.add_handler(CallbackQueryHandler(back_callback, pattern=r"^back_to_main$"))

    app.add_handler(CallbackQueryHandler(button_callback))

    

    # Message handlers

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    

    # Error handler

    app.add_error_handler(error_handler)

    

    # اجرای ربات

    logger.info("🤖 ربات شروع به کار کرد...")

    app.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == '__main__':

    main()