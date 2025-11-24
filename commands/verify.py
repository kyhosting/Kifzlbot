from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ContextTypes
from commands.vip_system import get_user_role, OWNER_ID

async def handle_verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    role = get_user_role(user_id)
    
    text = f"""```
✅ VERIFIKASI BERHASIL

Nama      : {query.from_user.full_name}
ID        : {user_id}
Username  : @{query.from_user.username if query.from_user.username else 'Tidak ada'}
Role      : {role}
Status    : {'✅ AKTIF' if role in ['VIP', 'PREMIUM'] else '❌ TIDAK AKTIF'}

Anda sudah terverifikasi!
Selamat menggunakan bot kami 🎉
```"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="verify_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_verify_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    from commands.menu import get_main_menu_keyboard
    keyboard = get_main_menu_keyboard(query.from_user.id)
    
    await query.message.reply_text(
        "```\n🎌 Silakan pilih menu di bawah\n```",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_member_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.my_chat_member
    
    if chat_member_update.new_chat_member.status == ChatMember.MEMBER:
        user = chat_member_update.from_user
        user_id = user.id
        
        text = f"""```
🎉 SELAMAT BERGABUNG!

Halo {user.full_name}! 👋
Terima kasih sudah join grup kami.

Silakan verifikasi akun Anda untuk
mendapatkan akses VIP gratis 1 minggu!
```"""
        
        keyboard = [
            [InlineKeyboardButton("✅ VERIFIKASI SEKARANG", callback_data="verify_user")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await user.send_message(text, parse_mode="Markdown", reply_markup=reply_markup)
        except:
            pass
