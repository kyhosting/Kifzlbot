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
```"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="verify_back")]
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
    user = chat_member_update.from_user
    user_id = user.id
    new_status = chat_member_update.new_chat_member.status
    
    if user_id == OWNER_ID:
        return
    
    if new_status == ChatMember.MEMBER:
        # Check if user is in BOTH groups now
        vip_groups = ["agentviber12", "channelviber"]
        groups_count = 0
        
        for group in vip_groups:
            try:
                member = await context.bot.get_chat_member(f"@{group}", user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                    groups_count += 1
            except:
                pass
        
        # If in BOTH groups, tell user to use /start to verify
        if groups_count == 2:
            text = f"""```
🎉 SELAMAT BERGABUNG!

Halo {user.full_name}! 👋
Terima kasih sudah join kedua grup kami.

Sekarang gunakan command berikut untuk
mendapatkan akses VIP gratis 7 hari:

/start

Kemudian klik tombol untuk verifikasi!
```"""
            try:
                await user.send_message(text, parse_mode="Markdown")
            except:
                pass
        else:
            # Still waiting for user to join second group
            text = f"""```
🎉 SELAMAT BERGABUNG!

Halo {user.full_name}! 👋
Terima kasih sudah join grup kami.

Untuk mendapatkan akses VIP gratis,
silakan join ke KEDUA grup kami terlebih dahulu:

📌 @agentviber12
📌 @channelviber

Setelah join kedua grup, gunakan command:
/start

Maka Anda akan mendapat akses VIP 7 hari!
```"""
            try:
                await user.send_message(text, parse_mode="Markdown")
            except:
                pass
    
    elif new_status in [ChatMember.LEFT, ChatMember.KICKED]:
        # User left a group - check remaining groups
        vip_groups = ["agentviber12", "channelviber"]
        groups_count = 0
        
        for group in vip_groups:
            try:
                member = await context.bot.get_chat_member(f"@{group}", user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                    groups_count += 1
            except:
                pass
        
        # If not in both groups, revoke access
        if groups_count < 2:
            update_user_data(user_id, {
                "role": "FREE",
                "expired": None,
                "verified": False
            })
            
            try:
                text = """```
⚠️ AKSES DICABUT

Anda telah keluar dari salah satu grup VIP kami.
Akses VIP Anda telah dihapus otomatis.

Untuk mendapatkan akses kembali:
1. Join ulang ke KEDUA grup kami
2. Gunakan command /start
3. Verifikasi akun Anda

Grup VIP:
📌 @agentviber12
📌 @channelviber
```"""
                await user.send_message(text, parse_mode="Markdown")
            except:
                pass
