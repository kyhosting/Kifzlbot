from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from commands.vip_system import get_user_role, get_user_data, update_user_data, OWNER_ID

async def handle_verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    
    user_id = query.from_user.id
    user = query.from_user
    
    if user_id == OWNER_ID:
        await query.edit_message_text(
            "```\n👑 Anda adalah OWNER, verifikasi tidak diperlukan.\n```",
            parse_mode="Markdown"
        )
        return
    
    expired_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    
    update_user_data(user_id, {
        "role": "VIP",
        "expired": expired_date,
        "verified": True,
        "expiry_notified_soon": False,
        "expiry_notified": False
    })
    
    role = get_user_role(user_id)
    expired_str = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y %H:%M")
    
    text = f"""```
✅ VERIFIKASI BERHASIL!

👤 PROFIL
────────────────────────────────────────
Nama         : {user.full_name}
ID           : {user_id}
Username     : @{user.username if user.username else 'Tidak ada'}

📊 STATUS VIP
────────────────────────────────────────
Role         : {role}
Status       : ✅ AKTIF
Masa Aktif   : {expired_str}
Sisa Hari    : 7 hari

🎉 Selamat! Anda telah mendapatkan
akses VIP GRATIS 7 hari!

Nikmati semua fitur premium bot kami.
Kami akan mengirim notifikasi sebelum
masa aktif Anda berakhir.
```"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="verify_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text,
                parse_mode="Markdown", reply_markup=reply_markup)

async def handle_verify_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    
    from commands.menu import get_main_menu_keyboard
    keyboard = get_main_menu_keyboard(query.from_user.id)
    
    if query.message:
        await query.message.reply_text("")
        await query.message.reply_text("```\n🎌 Silakan pilih menu di bawah\n```",
                    parse_mode="Markdown", reply_markup=keyboard)

async def handle_member_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.my_chat_member
    if not chat_member_update:
        return
    
    if chat_member_update.new_chat_member.status == ChatMember.MEMBER:
        user = chat_member_update.from_user
        if not user:
            return
        user_id = user.id
        
        if user_id == OWNER_ID:
            return
        
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
            await user.send_message(text,
                parse_mode="Markdown", reply_markup=reply_markup)
        except:
            pass
