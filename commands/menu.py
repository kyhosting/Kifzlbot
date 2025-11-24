from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from commands.vip_system import get_user_role, OWNER_ID
from commands.banner_helper import send_with_banner

def get_main_menu_keyboard(user_id):
    is_owner = (user_id == OWNER_ID)
    
    keyboard = [
        [KeyboardButton("🜲 STATUS 🜲")],
        [KeyboardButton("🜲 MSG TO TXT 🜲"), KeyboardButton("🜲 TXT TO VCF 🜲")],
        [KeyboardButton("🜲 VCF TO TXT 🜲"), KeyboardButton("🜲 XLS TO VCF 🜲")],
        [KeyboardButton("🜲 CREATE ADM/NAVY 🜲")],
        [KeyboardButton("🜲 RAPIKAN TXT 🜲"), KeyboardButton("🜲 GABUNG FILE 🜲")],
        [KeyboardButton("🜲 HITUNG KONTAK 🜲"), KeyboardButton("🜲 CEK NAMA 🜲")],
        [KeyboardButton("🜲 SPLIT FILE 🜲"), KeyboardButton("🎁 REDEEM CODE 🎁")],
    ]
    
    if is_owner:
        keyboard.append([KeyboardButton("🜲 MENU OWNER 🜲")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = get_main_menu_keyboard(user_id)
    
    text = """```
🎌  KIFZL DEV CV BOTS  
(BY KIFZL DEV)
───────────────────────────────────────

Pilih menu yang tersedia di bawah ini:

───────────────────────────────────────
⚡ FITUR UTAMA
───────────────────────────────────────
🜲 STATUS               — Cek akses  
🜲 MSG → TXT            — Convert  
🜲 TXT → VCF            — Convert  
🜲 VCF → TXT            — Ekstrak  
🜲 CREATE ADM & NAVY    — Buat kontak  
🜲 RAPIKAN TXT          — Bersihkan  
🜲 XLS → VCF            — Convert XLS  
🜲 GABUNG FILE          — Gabungkan  
🜲 HITUNG KONTAK        — Hitung  
🜲 CEK NAMA KONTAK      — Validasi  
🜲 SPLIT FILE           — Bagi file  
🎁 REDEEM CODE          — Aktivasi  

───────────────────────────────────────
```"""
    
    await update.message.reply_text(text,
                parse_mode="Markdown", reply_markup=keyboard)
