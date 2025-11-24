from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from commands.banner_helper import send_with_banner

async def aksesvip_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """```
🎟 AKSES VIP GRATIS
────────────────────
───────────────────────────────────────

Anda dapat memperoleh akses VIP melalui:

• Redeem Code dari Owner  
• Event Giveaway  
• Join Grup VIP (1 Minggu Gratis!)

────────────────────────────────────────
```"""
    
    keyboard = [
        [InlineKeyboardButton("📩 Chat Owner", url="https://t.me/KIFZLDEV")],
        [
            InlineKeyboardButton("👥 Join Grup 1", url="https://t.me/agentviber12"),
            InlineKeyboardButton("👥 Join Grup 2", url="https://t.me/channelviber")
        ],
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="akses_redeem")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_aksesvip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "akses_redeem":
        from commands.menu import get_main_menu_keyboard
        from commands.banner_helper import send_with_banner
        keyboard = get_main_menu_keyboard(update.effective_user.id)
        await query.message.reply_text("")
        await send_with_banner(query.from_user, context, "```\nSilakan pilih 🎁 REDEEM CODE dari menu utama\n```", parse_mode="Markdown", reply_markup=keyboard)
