from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from commands.vip_system import get_user_role, get_user_data, update_user_data, OWNER_ID

async def handle_verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
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
        "verified": True
    })
    
    role = get_user_role(user_id)
    expired_str = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y %H:%M")
    
    text = f"""```
✅ VERIFIKASI BERHASIL!

Nama         : {user.full_name}
ID           : {user_id}
Username     : @{user.username if user.username else 'Tidak ada'}
Role         : {role}
Status       : ✅ AKTIF
Masa Aktif   : {expired_str}
Sisa Hari    : 7 hari

🎉 Selamat! Anda telah mendapatkan
akses VIP GRATIS 7 hari!

Nikmati semua fitur premium bot kami.

Ketik /start untuk mulai menggunakan bot!
```"""
    
    keyboard = [
        [InlineKeyboardButton("▶️ /start", callback_data="verify_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text,
                parse_mode="Markdown", reply_markup=reply_markup)

async def handle_verify_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    from commands.menu import get_main_menu_keyboard
    keyboard = get_main_menu_keyboard(query.from_user.id)
    
    await query.message.reply_text("")
    await query.message.reply_text("```\n🎌 Silakan pilih menu di bawah\n```",
                parse_mode="Markdown", reply_markup=keyboard)

async def handle_member_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.my_chat_member
    
    if chat_member_update.new_chat_member.status == ChatMember.MEMBER:
        user = chat_member_update.from_user
        user_id = user.id
        
        if user_id == OWNER_ID:
            return
        
        # Check if user already has active VIP/PREMIUM
        current_role = get_user_role(user_id)
        user_data = get_user_data(user_id)
        
        # If user already has VIP or PREMIUM access
        if current_role in ["VIP", "PREMIUM"]:
            expired_str = "Tidak ada"
            remaining_days = 0
            
            if user_data and user_data.get("expired"):
                try:
                    if isinstance(user_data.get("expired"), str):
                        expired_dt = datetime.strptime(user_data.get("expired"), "%Y-%m-%d %H:%M:%S")
                    else:
                        expired_dt = user_data.get("expired")
                    
                    if expired_dt > datetime.now():
                        expired_str = expired_dt.strftime("%d-%m-%Y %H:%M")
                        remaining_days = (expired_dt - datetime.now()).days
                except:
                    pass
            
            text = f"""```
👋 SELAMAT BERGABUNG!

Halo {user.full_name}!
Anda sudah memiliki akses VIP aktif.

Akses      : {current_role}
Masa Aktif : {expired_str}
Sisa Hari  : {remaining_days} hari

Terima kasih sudah menjadi bagian dari grup kami!

Ketik /start untuk mulai menggunakan bot!
```"""
            
            keyboard = [
                [InlineKeyboardButton("▶️ /start", url="https://t.me/KIFZLBOT?start=1")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            # New user - show verification button
            text = f"""```
🎉 SELAMAT BERGABUNG!

Halo {user.full_name}! 👋
Terima kasih sudah join grup kami.

Silakan verifikasi akun Anda untuk
mendapatkan akses VIP gratis 7 hari!

Ketik /start setelah verifikasi!
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
