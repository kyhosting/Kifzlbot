from telegram import Update
from telegram.ext import ContextTypes
import os
from io import BytesIO

async def send_with_banner(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode="Markdown"):
    try:
        # Get the absolute path to banner
        banner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_banner.png")
        
        if os.path.exists(banner_path) and os.path.getsize(banner_path) > 0:
            # Send photo with file path
            await update.message.reply_photo(
                photo=open(banner_path, "rb"),
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
        # Get the absolute path to banner
        banner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_banner.png")
        
        if os.path.exists(banner_path) and os.path.getsize(banner_path) > 0:
            await query.edit_message_media(
                media={"type": "photo", "media": open(banner_path, "rb")},
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
