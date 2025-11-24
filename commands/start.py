from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from commands.vip_system import get_user_role, get_user_data, update_user_data, OWNER_ID
from commands.menu import get_main_menu_keyboard
from commands.banner_helper import send_with_banner

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        status = "✅ AKTIF"
    else:
        expired_str = "Tidak ada"
        remaining_days = 0
        status = "❌ TIDAK AKTIF"
        if role in ["VIP", "PREMIUM"]:
            role = "FREE"
            update_user_data(user_id, {"role": "FREE", "expired": None})
    
    total_ops = user_data.get("total_operations", 0)
    
    text = f"""🎌 **KIFZL DEV BOT** 🎌
_(BY @KIFZLDEV)_

**📍 STATUS AKUN**
• **Nama**: {name}
• **ID**: {user_id}
• **Username**: {username}
• **Role**: {role}
• **Status**: {status}
• **Masa Aktif**: {expired_str}
• **Hari Tersisa**: {remaining_days} hari

**⚡ FITUR UTAMA**
🔹 STATUS • MSG↔TXT • TXT↔VCF • VCF↔TXT
🔹 ADM & NAVY • RAPIKAN TXT • XLSX↔VCF
🔹 GABUNG • HITUNG KONTAK • CEK KONTAK
🔹 SPLIT FILE • REDEEM CODE • OWNER MENU"""
    
    keyboard_main = get_main_menu_keyboard(user_id)
    is_owner = (user_id == OWNER_ID)
    is_verified = role in ["VIP", "PREMIUM"]
    
    # Send photo with text caption combined
    try:
        with open("project_banner.png", "rb") as banner:
            await update.message.reply_photo(photo=banner, caption=text, parse_mode="Markdown", reply_markup=keyboard_main)
    except:
        # Fallback to text only if photo fails
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard_main)
    
    if not is_owner and not is_verified and role == "FREE":
        verify_keyboard = [
            [InlineKeyboardButton("✅ VERIFIKASI", callback_data="verify_user")],
            [
                InlineKeyboardButton("👥 JOIN GRUP 1", url="https://t.me/agentviber12"),
                InlineKeyboardButton("👥 JOIN GRUP 2", url="https://t.me/channelviber")
            ]
        ]
        verify_markup = InlineKeyboardMarkup(verify_keyboard)
        await update.message.reply_text(
            "```\n✨ Silakan tekan tombol di bawah untuk verifikasi\n```",
            parse_mode="Markdown",
            reply_markup=verify_markup
        )
