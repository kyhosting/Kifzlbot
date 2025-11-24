from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
from commands.vip_system import get_user_role, get_user_data, update_user_data, OWNER_ID
from commands.menu import get_main_menu_keyboard

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    name = user.full_name or "User"
    username = f"@{user.username}" if user.username else "Tidak ada"
    
    user_data = get_user_data(user_id)
    if not user_data:
        update_user_data(user_id, {
            "name": name,
            "username": username,
            "role": "FREE",
            "expired": None,
            "total_operations": 0
        })
        user_data = get_user_data(user_id)
    
    role = get_user_role(user_id)
    
    expired = user_data.get("expired")
    if expired:
        if isinstance(expired, str):
            try:
                expired = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
            except:
                expired = None
    
    if expired and expired > datetime.now():
        expired_str = expired.strftime("%d-%m-%Y %H:%M")
        remaining_days = (expired - datetime.now()).days
        remaining_hours = (expired - datetime.now()).seconds // 3600
        status = "✅ AKTIF"
    else:
        expired_str = "Tidak ada"
        remaining_days = 0
        remaining_hours = 0
        status = "❌ TIDAK AKTIF"
        if role in ["VIP", "PREMIUM"]:
            role = "FREE"
            update_user_data(user_id, {"role": "FREE", "expired": None})
    
    total_ops = user_data.get("total_operations", 0)
    is_owner = (user_id == OWNER_ID)
    
    status_info = f"""```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ CEK STATUS AKUN ANDA ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 INFORMASI AKUN:
   • NAMA          : {name}
   • ID            : {user_id}
   • USERNAME      : {username}
   
💎 STATUS LANGGANAN:
   • ROLE          : {role}
   • STATUS        : {status}
   • MASA AKTIF    : {expired_str}
   • HARI TERSISA  : {remaining_days} hari
   • JAM TERSISA   : {remaining_hours} jam
   
📊 STATISTIK:
   • TOTAL OPERASI : {total_ops}
"""
    
    if is_owner:
        status_info += "   • TIPE AKUN    : 👑 OWNER\n"
    
    status_info += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    if role == "FREE":
        status_info += """
🎯 CARA DAPATKAN AKSES LEBIH:
   • 💎 Beli Premium (1/7/30 hari)
   • 🎟  Redeem Code gratis dari owner
   
"""
    
    status_info += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n```"
    
    keyboard = get_main_menu_keyboard(user_id)
    
    await update.message.reply_text(status_info, parse_mode="Markdown", reply_markup=keyboard)
