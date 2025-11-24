from telegram import Update
from telegram.ext import ContextTypes

async def send_with_banner(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode="Markdown"):
    try:
        await update.message.reply_photo(
            photo=open("project_banner.png", "rb"),
            caption=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)

async def edit_with_banner(query, text: str, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_media(
            media={"type": "photo", "media": open("project_banner.png", "rb")},
            reply_markup=reply_markup
        )
        await query.edit_message_caption(
            caption=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except:
        try:
            await query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        except:
            pass
