from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def aksesvip_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """```
🎟 AKSES VIP GRATIS
────────────────────────────────────────

Pilih salah satu cara untuk mendapatkan
akses VIP:

1️⃣ KODE REDEEM
   Gunakan kode dari Owner

2️⃣ VERIFIKASI
   Join grup VIP dan dapatkan akses
   VIP GRATIS selama 7 hari! ✨

────────────────────────────────────────
```"""
    
    keyboard = [
        [
            InlineKeyboardButton("🎁 Kode Redeem", callback_data="akses_redeem"),
            InlineKeyboardButton("✅ Verifikasi", callback_data="akses_verify")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_aksesvip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    
    if query.data == "akses_redeem":
        text = """```
🎁 REDEEM CODE
────────────────────────────────────────

Silakan pilih menu:
🎁 REDEEM CODE

dari menu utama untuk
memasukkan kode Anda.
────────────────────────────────────────
```"""
        keyboard = [
            [InlineKeyboardButton("🏠 Kembali", callback_data="akses_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif query.data == "akses_verify":
        text = """```
✅ VERIFIKASI VIP
────────────────────────────────────────

Untuk mendapatkan akses VIP selama
7 hari, silakan:

1. Join grup VIP kami
2. Klik tombol VERIFIKASI di bawah
3. Dapatkan akses VIP otomatis!

────────────────────────────────────────
```"""
        keyboard = [
            [InlineKeyboardButton("👥 Join Grup VIP", url="https://t.me/agentviber12")],
            [InlineKeyboardButton("✅ VERIFIKASI SEKARANG", callback_data="verify_user")],
            [InlineKeyboardButton("🏠 Kembali", callback_data="akses_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif query.data == "akses_back":
        await aksesvip_show(update, context)
