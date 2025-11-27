from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from commands.vip_system import get_user_role, OWNER_ID

def get_main_menu_keyboard(user_id):
    is_owner = (user_id == OWNER_ID)
    
    keyboard = [
        [InlineKeyboardButton("🜲 STATUS 🜲", callback_data="menu_status")],
        [InlineKeyboardButton("🜲 MSG TO TXT 🜲", callback_data="menu_msg_to_txt"), 
         InlineKeyboardButton("🜲 TXT TO VCF 🜲", callback_data="menu_txt_to_vcf")],
        [InlineKeyboardButton("🜲 VCF TO TXT 🜲", callback_data="menu_vcf_to_txt"),
         InlineKeyboardButton("🜲 XLS TO VCF 🜲", callback_data="menu_xls_to_vcf")],
        [InlineKeyboardButton("🜲 CREATE ADM/NAVY 🜲", callback_data="menu_create_admin")],
        [InlineKeyboardButton("🜲 RAPIKAN TXT 🜲", callback_data="menu_rapikan_txt"),
         InlineKeyboardButton("🜲 GABUNG FILE 🜲", callback_data="menu_gabung_file")],
        [InlineKeyboardButton("🜲 HITUNG KONTAK 🜲", callback_data="menu_hitung_kontak"),
         InlineKeyboardButton("🜲 CEK NAMA 🜲", callback_data="menu_cek_nama")],
        [InlineKeyboardButton("🜲 SPLIT FILE 🜲", callback_data="menu_split_file"),
         InlineKeyboardButton("🎁 REDEEM CODE 🎁", callback_data="menu_redeem")],
    ]
    
    if is_owner:
        keyboard.append([InlineKeyboardButton("🜲 MENU OWNER 🜲", callback_data="menu_owner")])
    
    return InlineKeyboardMarkup(keyboard)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = get_main_menu_keyboard(user_id)
    
    text = """```
🎌  KIFZL DEV BOT  
(BY @KIFZLDEV)
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
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
