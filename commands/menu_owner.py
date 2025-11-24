import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from commands.vip_system import OWNER_ID, load_users, save_users
from commands.menu import get_main_menu_keyboard
from commands.banner_helper import send_with_banner
from commands.redeem_utils import generate_random_code, format_duration_readable, format_code_expiry_readable

ASK_ACTION, ASK_USER_ID, ASK_ROLE, ASK_DURATION, ASK_REDEEM_MODE, ASK_REDEEM_CODE, ASK_REDEEM_DURATION, ASK_CODE_EXPIRY = range(8)

async def menu_owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("```\n❌ Anda bukan owner!\n```", parse_mode="Markdown")
        return ConversationHandler.END
    
    action_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("👥 LIHAT USERS")],
        [KeyboardButton("➕ TAMBAH USER"), KeyboardButton("✏️ EDIT USER")],
        [KeyboardButton("🎁 BUAT REDEEM"), KeyboardButton("📊 STATISTIK")],
        [KeyboardButton("🔙 KEMBALI")]
    ], resize_keyboard=True)
    
    text = """```
🜲 MENU OWNER
───────────────────────────────────────

Selamat datang, Owner!

Pilih aksi yang ingin dilakukan:

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=action_keyboard)
    return ASK_ACTION

async def menu_owner_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 KEMBALI":
        keyboard = get_main_menu_keyboard(update.effective_user.id)
        await update.message.reply_text("```\n🔙 Kembali ke menu utama\n```",
                parse_mode="Markdown", reply_markup=keyboard)
        return ConversationHandler.END
    
    action = update.message.text
    
    if action == "👥 LIHAT USERS":
        users = load_users()
        
        if not users:
            await update.message.reply_text("```\n❌ Belum ada user terdaftar\n```", parse_mode="Markdown")
            return ASK_ACTION
        
        user_list = []
        for uid, data in list(users.items())[:20]:
            name = data.get('name', 'Unknown')
            role = data.get('role', 'FREE')
            user_list.append(f"{uid}: {name} ({role})")
        
        text = "```\n👥 DAFTAR USERS\n───────────────────────────────────────\n\n"
        text += '\n'.join(user_list)
        text += f"\n\nTotal: {len(users)} users\n```"
        
        await update.message.reply_text(text, parse_mode="Markdown")
        return ASK_ACTION
    
    elif action == "📊 STATISTIK":
        users = load_users()
        
        total_users = len(users)
        free_count = sum(1 for u in users.values() if u.get('role') == 'FREE')
        vip_count = sum(1 for u in users.values() if u.get('role') == 'VIP')
        premium_count = sum(1 for u in users.values() if u.get('role') == 'PREMIUM')
        
        text = f"""```
📊 STATISTIK BOT
───────────────────────────────────────

Total Users  : {total_users}
FREE         : {free_count}
VIP          : {vip_count}
PREMIUM      : {premium_count}
OWNER        : 1

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown")
        return ASK_ACTION
    
    elif action == "🎁 BUAT REDEEM":
        mode_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("🎲 RANDOM"), KeyboardButton("✍️ CUSTOM")],
            [KeyboardButton("❌ BATAL ❌")]
        ], resize_keyboard=True)
        
        text = """```
🎁 BUAT REDEEM CODE
───────────────────────────────────────

Pilih cara membuat kode redeem:

🎲 RANDOM - Bot generate otomatis
✍️ CUSTOM - Ketik sendiri

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=mode_keyboard)
        return ASK_REDEEM_MODE
    
    elif action == "➕ TAMBAH USER" or action == "✏️ EDIT USER":
        context.user_data['owner_action'] = action
        cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
        
        text = """```
👤 USER ID
───────────────────────────────────────

Masukkan User ID Telegram

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
        return ASK_USER_ID
    
    return ASK_ACTION

async def menu_owner_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    try:
        user_id = int(update.message.text.strip())
        context.user_data['target_user_id'] = user_id
    except:
        await update.message.reply_text("```\n❌ User ID harus angka!\n```", parse_mode="Markdown")
        return ASK_USER_ID
    
    role_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("FREE"), KeyboardButton("VIP")],
        [KeyboardButton("PREMIUM")],
        [KeyboardButton("❌ BATAL ❌")]
    ], resize_keyboard=True)
    
    text = """```
🎭 ROLE
───────────────────────────────────────

Pilih role untuk user:

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=role_keyboard)
    return ASK_ROLE

async def menu_owner_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    role = update.message.text
    if role not in ["FREE", "VIP", "PREMIUM"]:
        await update.message.reply_text("```\n❌ Role tidak valid!\n```", parse_mode="Markdown")
        return ASK_ROLE
    
    context.user_data['target_role'] = role
    
    cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
    
    text = """```
⏰ DURASI
───────────────────────────────────────

Masukkan durasi dalam hari
(untuk VIP/PREMIUM)

Contoh: 7
(untuk 7 hari)

Ketik 0 untuk permanent/FREE

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
    return ASK_DURATION

async def menu_owner_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    try:
        duration = int(update.message.text.strip())
    except:
        await update.message.reply_text("```\n❌ Durasi harus angka!\n```", parse_mode="Markdown")
        return ASK_DURATION
    
    user_id = context.user_data.get('target_user_id')
    role = context.user_data.get('target_role')
    
    users = load_users()
    
    if duration > 0:
        expired = datetime.now() + timedelta(days=duration)
    else:
        expired = None
    
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    
    users[user_str]['role'] = role
    users[user_str]['expired'] = expired
    
    save_users(users)
    
    action_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("👥 LIHAT USERS")],
        [KeyboardButton("➕ TAMBAH USER"), KeyboardButton("✏️ EDIT USER")],
        [KeyboardButton("🎁 BUAT REDEEM"), KeyboardButton("📊 STATISTIK")],
        [KeyboardButton("🔙 KEMBALI")]
    ], resize_keyboard=True)
    
    text = f"""```
✅ USER BERHASIL DIUPDATE
───────────────────────────────────────

User ID  : {user_id}
Role     : {role}
Expired  : {expired.strftime("%d-%m-%Y") if expired else "Permanent"}

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=action_keyboard)
    return ASK_ACTION

async def menu_owner_redeem_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    mode = update.message.text
    context.user_data['redeem_mode'] = mode
    
    if mode == "🎲 RANDOM":
        # Generate random code
        code = generate_random_code()
        context.user_data['redeem_code'] = code
        context.user_data['redeem_role'] = "VIP"
        
        text = f"""```
🎲 RANDOM CODE GENERATED
───────────────────────────────────────

Kode Generated:
{code}

Role: VIP (hanya untuk VIP)
PREMIUM hanya bisa dibeli!

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown")
        
        # Continue to duration
        cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
        
        text = """```
⏰ DURASI VIP
───────────────────────────────────────

Masukkan durasi dalam hari
(berapa lama user mendapat akses VIP)

Contoh: 7
(untuk 7 hari VIP)

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
        return ASK_REDEEM_DURATION
    
    else:  # CUSTOM
        cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
        
        text = """```
✍️ BUAT KODE CUSTOM
───────────────────────────────────────

Masukkan kode redeem yang ingin dibuat
(huruf kapital & angka)

Contoh: VIP2024

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
        return ASK_REDEEM_CODE

async def menu_owner_redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    code = update.message.text.strip().upper()
    context.user_data['redeem_code'] = code
    context.user_data['redeem_role'] = "VIP"
    
    cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
    
    text = """```
⏰ DURASI VIP
───────────────────────────────────────

Masukkan durasi dalam hari
(berapa lama user mendapat akses VIP)

Contoh: 7
(untuk 7 hari VIP)

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
    return ASK_REDEEM_DURATION

async def menu_owner_redeem_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    try:
        duration = int(update.message.text.strip())
    except:
        await update.message.reply_text("```\n❌ Durasi harus angka!\n```", parse_mode="Markdown")
        return ASK_REDEEM_DURATION
    
    context.user_data['redeem_user_duration'] = duration
    
    cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
    
    text = """```
⏰ EXPIRED KODE REDEEM
───────────────────────────────────────

Berapa hari kode ini berlaku?

Contoh: 30
(kode berlaku 30 hari dari sekarang)

Ketik 0 untuk permanent (tidak expires)

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
    return ASK_CODE_EXPIRY

async def menu_owner_code_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    try:
        code_expiry_days = int(update.message.text.strip())
    except:
        await update.message.reply_text("```\n❌ Nilai harus angka!\n```", parse_mode="Markdown")
        return ASK_CODE_EXPIRY
    
    code = context.user_data.get('redeem_code')
    role = context.user_data.get('redeem_role')
    user_duration = context.user_data.get('redeem_user_duration')
    
    try:
        with open("redeem.json", "r") as f:
            redeem_codes = json.load(f)
    except FileNotFoundError:
        redeem_codes = {}
    
    code_expired = code_expiry_days if code_expiry_days > 0 else 0
    
    redeem_codes[code] = {
        "role": role,
        "duration_days": user_duration,
        "code_expired": code_expired,
        "used": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("redeem.json", "w") as f:
        json.dump(redeem_codes, f, indent=2)
    
    action_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("👥 LIHAT USERS")],
        [KeyboardButton("➕ TAMBAH USER"), KeyboardButton("✏️ EDIT USER")],
        [KeyboardButton("🎁 BUAT REDEEM"), KeyboardButton("📊 STATISTIK")],
        [KeyboardButton("🔙 KEMBALI")]
    ], resize_keyboard=True)
    
    duration_readable = format_duration_readable(user_duration)
    code_expiry_readable = format_code_expiry_readable(code_expiry_days)
    
    active_until = (datetime.now() + timedelta(days=user_duration)).strftime("%d-%m-%Y %H:%M:%S")
    
    text = f"""```
✅ REDEEM CODE DIBUAT
───────────────────────────────────────

Kode Redeem  : {code}
───────────────────────────────────────

Role         : VIP (GRATIS)
Durasi Akses : {duration_readable}
Aktif s.d.   : {active_until}

Kode Berlaku : {code_expiry_readable}
Setelah expired, kode tidak bisa digunakan

Note: PREMIUM hanya bisa dibeli, bukan redeem!
───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=action_keyboard)
    return ASK_ACTION
