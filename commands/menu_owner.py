import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from commands.vip_system import OWNER_ID, load_users, save_users
from commands.menu import get_main_menu_keyboard
from commands.banner_helper import send_with_banner

ASK_ACTION, ASK_USER_ID, ASK_ROLE, ASK_DURATION, ASK_REDEEM_CODE, ASK_REDEEM_ROLE, ASK_REDEEM_DURATION = range(7)

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
        await send_with_banner(update, context, "```\n🔙 Kembali ke menu utama\n```", parse_mode="Markdown", reply_markup=keyboard)
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
        cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
        
        text = """```
🎁 BUAT REDEEM CODE
───────────────────────────────────────

Masukkan kode redeem yang ingin dibuat
(huruf kapital & angka)

Contoh: VIP2024

───────────────────────────────────────
```"""
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
        return ASK_REDEEM_CODE
    
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

async def menu_owner_redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    code = update.message.text.strip().upper()
    context.user_data['redeem_code'] = code
    
    role_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("VIP"), KeyboardButton("PREMIUM")],
        [KeyboardButton("❌ BATAL ❌")]
    ], resize_keyboard=True)
    
    text = """```
🎭 ROLE REDEEM
───────────────────────────────────────

Pilih role untuk redeem code:

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=role_keyboard)
    return ASK_REDEEM_ROLE

async def menu_owner_redeem_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        return await menu_owner_start(update, context)
    
    role = update.message.text
    if role not in ["VIP", "PREMIUM"]:
        await update.message.reply_text("```\n❌ Role tidak valid!\n```", parse_mode="Markdown")
        return ASK_REDEEM_ROLE
    
    context.user_data['redeem_role'] = role
    
    cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
    
    text = """```
⏰ DURASI REDEEM
───────────────────────────────────────

Masukkan durasi dalam hari

Contoh: 7
(untuk 7 hari)

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
    
    code = context.user_data.get('redeem_code')
    role = context.user_data.get('redeem_role')
    
    try:
        with open("redeem.json", "r") as f:
            redeem_codes = json.load(f)
    except FileNotFoundError:
        redeem_codes = {}
    
    redeem_codes[code] = {
        "role": role,
        "duration_days": duration,
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
    
    text = f"""```
✅ REDEEM CODE DIBUAT
───────────────────────────────────────

Kode     : {code}
Role     : {role}
Durasi   : {duration} hari

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=action_keyboard)
    return ASK_ACTION
