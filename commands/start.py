from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from commands.vip_system import get_user_role, get_user_data, update_user_data, OWNER_ID
from commands.menu import get_main_menu_keyboard

async def check_and_restore_vip(user_id, bot, context):
    """Check if user in BOTH VIP groups and grant/revoke access accordingly"""
    vip_groups = ["agentviber12", "channelviber"]
    groups_count = 0
    
    # Check if user is in BOTH groups
    for group in vip_groups:
        try:
            member = await bot.get_chat_member(f"@{group}", user_id)
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                groups_count += 1
        except:
            pass
    
    user_data = get_user_data(user_id)
    
    # If in BOTH groups and currently FREE -> grant VIP access
    if groups_count == 2 and user_data.get("role") == "FREE":
        expired_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        update_user_data(user_id, {
            "role": "VIP",
            "expired": expired_date,
            "verified": True
        })
    
    # If in BOTH groups and VIP but expired -> restore VIP access
    elif groups_count == 2 and user_data.get("role") == "VIP":
        expired = user_data.get("expired")
        if isinstance(expired, str):
            try:
                expired = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
            except:
                expired = None
        
        if not expired or expired <= datetime.now():
            expired_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            update_user_data(user_id, {
                "role": "VIP",
                "expired": expired_date,
                "verified": True
            })
    
    # If NOT in BOTH groups and has VIP/PREMIUM -> revoke access
    elif groups_count < 2 and user_data.get("role") in ["VIP", "PREMIUM"]:
        update_user_data(user_id, {
            "role": "FREE",
            "expired": None,
            "verified": False
        })
    
    # Return groups_count so we can show message if needed
    return groups_count

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
    
    groups_count = await check_and_restore_vip(user_id, context.bot, context)
    role = get_user_role(user_id)
    
    # Check if user is NOT in both groups - show warning and RETURN
    if groups_count < 2 and role == "FREE":
        warning_text = """```
⚠️ ANDA BELUM BISA MENGGUNAKAN FITUR VIP

Untuk mendapatkan akses VIP GRATIS 7 hari,
silakan join ke KEDUA grup kami terlebih dahulu:

📌 Grup 1: @agentviber12
📌 Grup 2: @channelviber

Setelah join KEDUA grup, gunakan /start lagi
untuk mendapatkan akses VIP otomatis!

✨ Akses akan diberikan secara otomatis
setelah join kedua grup.
```"""
        keyboard = get_main_menu_keyboard(user_id)
        try:
            await update.message.reply_text(warning_text, parse_mode="Markdown", reply_markup=keyboard)
        except:
            pass
        return
    
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
    
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
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
