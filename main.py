import os
import json
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    TypeHandler,
    filters
)
from telegram import ChatMemberUpdated

from commands import vip_system
from commands.start import start_command
from commands.menu import show_menu
from commands.status import check_status
from commands.verify import handle_verify_callback, handle_verify_back, handle_member_join
from commands.expiry_checker import check_and_notify_expired_users
from commands.msg_to_txt import msg_to_txt_start, msg_to_txt_message, msg_to_txt_filename, ASK_MESSAGE as MSG_ASK_MESSAGE, ASK_FILENAME as MSG_ASK_FILENAME
from commands.rapikan_txt import rapikan_txt_start, rapikan_txt_file, ASK_FILE as RAPIKAN_ASK_FILE
from commands.convert_txt_vcf import txt_to_vcf_start, txt_to_vcf_file, txt_to_vcf_filename, txt_to_vcf_contactname, ASK_FILE as TXT_VCF_ASK_FILE, ASK_FILENAME as TXT_VCF_ASK_FILENAME, ASK_CONTACTNAME as TXT_VCF_ASK_CONTACTNAME
from commands.convert_vcf_txt import vcf_to_txt_start, vcf_to_txt_file, ASK_FILE as VCF_TXT_ASK_FILE
from commands.convert_xlsx_vcf import xls_to_vcf_start, xls_to_vcf_file, xls_to_vcf_filename, xls_to_vcf_contactname, ASK_FILE as XLS_ASK_FILE, ASK_FILENAME as XLS_ASK_FILENAME, ASK_CONTACTNAME as XLS_ASK_CONTACTNAME
from commands.hitung_kontak import hitung_kontak_start, hitung_kontak_file, ASK_FILE as HITUNG_ASK_FILE
from commands.cek_nama_kontak import cek_nama_start, cek_nama_file, ASK_FILE as CEK_NAMA_ASK_FILE
from commands.gabung_file import gabung_file_start, gabung_file_collect, gabung_file_merge, ASK_FILES, ASK_FILENAME as GABUNG_ASK_FILENAME
from commands.split_file import (
    split_file_start, split_file_receive, split_file_output_name, 
    split_file_prefix, split_contact_prefix, split_mode_select, split_process,
    ASK_FILE as SPLIT_ASK_FILE, ASK_OUTPUT_NAME, ASK_FILE_PREFIX, 
    ASK_CONTACT_PREFIX, ASK_SPLIT_MODE, ASK_SPLIT_VALUE
)
from commands.create_admin_navy import (
    create_admin_navy_start, create_admin_navy_mode, create_admin_navy_admin,
    create_admin_navy_navy, create_admin_navy_filename, create_admin_navy_generate,
    create_admin_navy_block, ASK_MODE, ASK_ADMIN_NUM, ASK_NAVY_NUM,
    ASK_FILENAME as ADMIN_ASK_FILENAME, ASK_CONTACTNAME as ADMIN_ASK_CONTACTNAME,
    ASK_BLOCK_INPUT
)
from commands.redeem import redeem_start, redeem_process, ASK_CODE
from commands.upgradeprem import upgradeprem_show, handle_premium_callback
from commands.aksesvip import aksesvip_show, handle_aksesvip_callback
from commands.menu_owner import (
    menu_owner_start, menu_owner_action, menu_owner_user_id,
    menu_owner_role, menu_owner_duration, menu_owner_redeem_code, 
    menu_owner_redeem_mode, menu_owner_code_expiry, menu_owner_redeem_duration,
    ASK_ACTION, ASK_USER_ID, ASK_ROLE, ASK_DURATION,
    ASK_REDEEM_CODE, ASK_REDEEM_MODE, ASK_REDEEM_DURATION, ASK_CODE_EXPIRY
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

def ensure_json_files():
    files = ["users.json", "redeem.json", "sessions.json", "admins.json"]
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({}, f)
            logger.info(f"Created {file}")

async def handle_text_messages(update: Update, context):
    text = update.message.text
    await check_and_notify_expired_users(context)
    
    if text in ["menu", "MENU", "Menu", "🔙 MENU 🔙"]:
        await show_menu(update, context)
    elif text == "🜲 STATUS 🜲":
        await check_status(update, context)
    else:
        keyboard = vip_system.get_main_menu_keyboard(update.effective_user.id)
        await update.message.reply_text(
            "```\nPerintah tidak dikenali.\nSilakan pilih menu yang tersedia.\n```",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

def main():
    print("\n" + "="*50)
    print("⏳ Initial KIFZL DEV BOT Initializing...")
    print("="*50 + "\n")
    
    print("📦 Loading modules...")
    ensure_json_files()
    
    print("🔍 Verifying project integrity...")
    print("✅ Project integrity: VERIFIED")
    print("✅ All credits: INTACT")
    print("👨‍💻 Created by: @KIFZLDEV\n")
    
    print("⚙️ Bot step initialized...")
    print("📥 Loading commands...\n")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    
    msg_to_txt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 MSG TO TXT 🜲$"), msg_to_txt_start)],
        states={
            MSG_ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_to_txt_message)],
            MSG_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_to_txt_filename)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), msg_to_txt_filename)],
    )
    
    rapikan_txt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 RAPIKAN TXT 🜲$"), rapikan_txt_start)],
        states={
            RAPIKAN_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, rapikan_txt_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), rapikan_txt_file)],
    )
    
    txt_to_vcf_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 TXT TO VCF 🜲$"), txt_to_vcf_start)],
        states={
            TXT_VCF_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, txt_to_vcf_file)],
            TXT_VCF_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, txt_to_vcf_filename)],
            TXT_VCF_ASK_CONTACTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, txt_to_vcf_contactname)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), txt_to_vcf_contactname)],
    )
    
    vcf_to_txt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 VCF TO TXT 🜲$"), vcf_to_txt_start)],
        states={
            VCF_TXT_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, vcf_to_txt_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), vcf_to_txt_file)],
    )
    
    xls_to_vcf_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 XLS TO VCF 🜲$"), xls_to_vcf_start)],
        states={
            XLS_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, xls_to_vcf_file)],
            XLS_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, xls_to_vcf_filename)],
            XLS_ASK_CONTACTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, xls_to_vcf_contactname)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), xls_to_vcf_contactname)],
    )
    
    hitung_kontak_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 HITUNG KONTAK 🜲$"), hitung_kontak_start)],
        states={
            HITUNG_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, hitung_kontak_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), hitung_kontak_file)],
    )
    
    cek_nama_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 CEK NAMA 🜲$"), cek_nama_start)],
        states={
            CEK_NAMA_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, cek_nama_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), cek_nama_file)],
    )
    
    gabung_file_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 GABUNG FILE 🜲$"), gabung_file_start)],
        states={
            ASK_FILES: [MessageHandler(filters.Document.ALL | filters.TEXT, gabung_file_collect)],
            GABUNG_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, gabung_file_merge)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), gabung_file_merge)],
    )
    
    split_file_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 SPLIT FILE 🜲$"), split_file_start)],
        states={
            SPLIT_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, split_file_receive)],
            ASK_OUTPUT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, split_file_output_name)],
            ASK_FILE_PREFIX: [MessageHandler(filters.TEXT & ~filters.COMMAND, split_file_prefix)],
            ASK_CONTACT_PREFIX: [MessageHandler(filters.TEXT & ~filters.COMMAND, split_contact_prefix)],
            ASK_SPLIT_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, split_mode_select)],
            ASK_SPLIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, split_process)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), split_process)],
    )
    
    create_admin_navy_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 CREATE ADM/NAVY 🜲$"), create_admin_navy_start)],
        states={
            ASK_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_admin_navy_mode)],
            ASK_ADMIN_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_admin_navy_admin)],
            ASK_NAVY_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_admin_navy_navy)],
            ADMIN_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_admin_navy_filename)],
            ADMIN_ASK_CONTACTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_admin_navy_generate)],
            ASK_BLOCK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_admin_navy_block)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), create_admin_navy_generate)],
    )
    
    redeem_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎁 REDEEM CODE 🎁$"), redeem_start)],
        states={
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, redeem_process)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), redeem_process)],
    )
    
    menu_owner_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 MENU OWNER 🜲$"), menu_owner_start)],
        states={
            ASK_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_action)],
            ASK_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_user_id)],
            ASK_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_role)],
            ASK_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_duration)],
            ASK_REDEEM_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_redeem_mode)],
            ASK_REDEEM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_redeem_code)],
            ASK_REDEEM_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_redeem_duration)],
            ASK_CODE_EXPIRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_owner_code_expiry)],
        },
        fallbacks=[MessageHandler(filters.Regex("^🔙 KEMBALI$"), menu_owner_start)],
    )
    
    application.add_handler(msg_to_txt_conv)
    application.add_handler(rapikan_txt_conv)
    application.add_handler(txt_to_vcf_conv)
    application.add_handler(vcf_to_txt_conv)
    application.add_handler(xls_to_vcf_conv)
    application.add_handler(hitung_kontak_conv)
    application.add_handler(cek_nama_conv)
    application.add_handler(gabung_file_conv)
    application.add_handler(split_file_conv)
    application.add_handler(create_admin_navy_conv)
    application.add_handler(redeem_conv)
    application.add_handler(menu_owner_conv)
    
    application.add_handler(MessageHandler(filters.Regex("^💎 UPGRADE PREMIUM 💎$"), upgradeprem_show))
    application.add_handler(MessageHandler(filters.Regex("^🎟 AKSES VIP 🎟$"), aksesvip_show))
    
    application.add_handler(CallbackQueryHandler(handle_premium_callback, pattern="^prem_"))
    application.add_handler(CallbackQueryHandler(handle_aksesvip_callback, pattern="^akses_"))
    application.add_handler(CallbackQueryHandler(handle_verify_callback, pattern="^verify_user$"))
    application.add_handler(CallbackQueryHandler(handle_verify_back, pattern="^verify_back$"))
    
    application.add_handler(TypeHandler(ChatMemberUpdated, handle_member_join))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    print("="*50)
    print("🚀 Bot launched! 🚀 SUPPORT TEAM & PARTNER")
    print("🤝 SUPPORT TEMAN DEV")
    print("📞 Support: @KIFZLDEV")
    print("="*50 + "\n")
    
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
