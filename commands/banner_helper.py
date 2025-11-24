from telegram import Update
from telegram.ext import ContextTypes
import os

async def send_with_banner(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode="Markdown"):
    try:
        # Read banner file into bytes
        banner_path = "project_banner.png"
        if os.path.exists(banner_path):
            with open(banner_path, "rb") as banner_file:
                banner_bytes = banner_file.read()
            
            # Send photo with banner bytes
            await update.message.reply_photo(
                photo=banner_bytes,
                caption=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            # Fallback to text if banner doesn't exist
            await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        # Fallback to text on any error
        try:
            await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        except:
            pass

async def edit_with_banner(query, text: str, reply_markup=None, parse_mode="Markdown"):
    try:
        banner_path = "project_banner.png"
        if os.path.exists(banner_path):
            with open(banner_path, "rb") as banner_file:
                banner_bytes = banner_file.read()
            
            await query.edit_message_media(
                media={"type": "photo", "media": banner_bytes},
                reply_markup=reply_markup
            )
            await query.edit_message_caption(
                caption=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except:
        try:
            await query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        except:
            pass
