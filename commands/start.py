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
    
    text = f"""```
🎌  KIFZL DEV CV BOTS  
(BY KIFZL DEV)
───────────────────────────────────────

"KONNICHIWA, WATASHI WA KIFZL_BOT DESU"
Saya siap bantu convert file & management kontak.
✦ Created by: @KIFZLDEV

───────────────────────────────────────
📍 STATUS AKUN
───────────────────────────────────────
• NAMA          : {name}
• ID            : {user_id}
• USERNAME      : {username}
• ROLE          : {role}
• STATUS        : {status}
• MASA AKTIF    : {expired_str}
• HARI TERSISA  : {remaining_days} hari
• TOTAL OPSI    : {total_ops}

───────────────────────────────────────
⚡ FITUR UTAMA
───────────────────────────────────────
🜲 STATUS               — Cek akses  
🜲 MSG → TXT            — Convert  
🜲 TXT → VCF            — Convert  
🜲 VCF → TXT            — Ekstrak  
🜲 CREATE ADM & NAVY    — Buat kontak admin/navy  
🜲 RAPIKAN TXT          — Bersihkan format  
🜲 XLS → VCF            — Convert XLS  
🜲 GABUNG FILE          — Gabungkan  
🜲 HITUNG KONTAK        — Hitung kontak  
🜲 CEK NAMA KONTAK      — Validasi nama  
🜲 SPLIT FILE           — Bagi file  
🎁 REDEEM CODE          — Aktivasi  
🜲 MENU OWNER           — Khusus owner  

───────────────────────────────────────
```"""
    
    keyboard_main = get_main_menu_keyboard(user_id)
    is_owner = (user_id == OWNER_ID)
    is_verified = role in ["VIP", "PREMIUM"]
    
    # Send banner photo first
    try:
        with open("project_banner.png", "rb") as banner:
            await update.message.reply_photo(photo=banner, caption="🎌 KIFZL PROJECT BOT")
    except:
        pass
    
    # Send text with menu
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
