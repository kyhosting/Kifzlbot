from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from commands.vip_system import get_user_role, get_user_data, update_user_data, OWNER_ID
from commands.menu import get_main_menu_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
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
🎌  KIFZL DEV BOT  
(BY @KIFZLDEV)
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
    
    keyboard = get_main_menu_keyboard(user_id)
    
    if not update.message:
        return
    
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos and photos.total_count > 0:
            await update.message.reply_photo(
                photo=photos.photos[0][0].file_id,
                caption=text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
    except:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
