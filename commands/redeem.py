import json
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from commands.vip_system import update_user_data, get_user_data
from commands.menu import get_main_menu_keyboard
from commands.redeem_utils import is_code_expired, format_duration_readable, format_code_expiry_readable

ASK_CODE = range(1)

def load_redeem_codes():
    try:
        with open("redeem.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_redeem_codes(data):
    with open("redeem.json", "w") as f:
        json.dump(data, f, indent=2)

async def redeem_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cancel_keyboard = ReplyKeyboardMarkup([[KeyboardButton("❌ BATAL ❌")]], resize_keyboard=True)
    
    text = """```
🎁 REDEEM CODE
───────────────────────────────────────

Masukkan kode redeem Anda
untuk mendapatkan akses VIP/PREMIUM

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard)
    return ASK_CODE

async def redeem_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ BATAL ❌":
        keyboard = get_main_menu_keyboard(update.effective_user.id)
        await update.message.reply_text("```\n❌ Proses dibatalkan\n```",
                parse_mode="Markdown", reply_markup=keyboard)
        return ConversationHandler.END
    
    code = update.message.text.strip().upper()
    redeem_codes = load_redeem_codes()
    
    keyboard = get_main_menu_keyboard(update.effective_user.id)
    
    if code not in redeem_codes:
        await update.message.reply_text("```\n❌ Kode redeem tidak valid!\n```",
                parse_mode="Markdown", reply_markup=keyboard)
        return ConversationHandler.END
    
    code_data = redeem_codes[code]
    
    # Check if code itself has expired
    if is_code_expired(code_data):
        code_expired_at = code_data.get("code_expired", "N/A")
        await update.message.reply_text(
            f"```\n❌ KODE REDEEM SUDAH EXPIRED\n\n"
            f"Kode berakhir: {code_expired_at}\n"
            f"Hubungi owner untuk kode baru\n```",
            parse_mode="Markdown", reply_markup=keyboard)
        return ConversationHandler.END
    
    if code_data.get("used", False):
        used_by = code_data.get("used_by", "Unknown")
        used_at = code_data.get("used_at", "N/A")
        await update.message.reply_text(
            f"```\n❌ KODE REDEEM SUDAH DIGUNAKAN\n\n"
            f"Digunakan oleh: {used_by}\n"
            f"Tanggal: {used_at}\n\n"
            f"Setiap kode hanya bisa digunakan 1x\n"
            f"Hubungi owner untuk kode baru\n```",
            parse_mode="Markdown", reply_markup=keyboard)
        return ConversationHandler.END
    
    role = code_data.get("role", "VIP")
    duration_days = code_data.get("duration_days", 7)
    code_expired_days = code_data.get("code_expired")
    
    expired = datetime.now() + timedelta(days=duration_days)
    duration_readable = format_duration_readable(duration_days)
    
    user_id = update.effective_user.id
    
    update_user_data(user_id, {
        "role": role,
        "expired": expired.strftime("%Y-%m-%d %H:%M:%S"),
        "redeemed_code": code
    })
    
    code_data["used"] = True
    code_data["used_by"] = user_id
    code_data["used_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    redeem_codes[code] = code_data
    save_redeem_codes(redeem_codes)
    
    text = f"""```
🎁 REDEEM BERHASIL ✅
───────────────────────────────────────

Role          : {role} (GRATIS)
Durasi Akses  : {duration_readable}

Aktif Mulai   : {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
Aktif s.d.    : {expired.strftime("%d-%m-%Y %H:%M:%S")}

Selamat menikmati akses {role}!
───────────────────────────────────────
```"""
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
    return ConversationHandler.END
