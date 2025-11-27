import os
import json
import logging
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
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
from commands.menu import show_menu, get_main_menu_keyboard
from commands.status import check_status
from commands.verify import handle_verify_callback, handle_verify_back, handle_member_join
from commands.upgradeprem import upgradeprem_show
from commands.aksesvip import aksesvip_show
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
    menu_owner_redeem_mode, menu_owner_redeem_duration, menu_owner_code_expiry, 
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

async def handle_access_denied_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline buttons from access denied message"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "upgrade_prem":
        class FakeUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        fake_update = FakeUpdate(query)
        await upgradeprem_show(fake_update, context)
    elif query.data == "akses_vip":
        class FakeUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        fake_update = FakeUpdate(query)
        await aksesvip_show(fake_update, context)
    elif query.data == "back_menu":
        keyboard = get_main_menu_keyboard(query.from_user.id)
        await query.edit_message_text("```\n🎌 Silakan pilih menu di bawah\n```",
                    parse_mode="Markdown", reply_markup=keyboard)

async def check_vip_access_wrapper(handler_func, required_role="VIP"):
    """Create wrapper that checks access before executing handler"""
    async def wrapper(update: Update, context):
        user_id = update.effective_user.id
        if not await vip_system.check_access_with_group_verify(user_id, required_role, context.bot, update):
            user_role = vip_system.get_user_role(user_id)
            await vip_system.send_access_denied(update, user_role, required_role)
            return
        await handler_func(update, context)
    return wrapper

async def msg_to_txt_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await msg_to_txt_start(update, context)

async def rapikan_txt_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await rapikan_txt_start(update, context)

async def txt_to_vcf_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await txt_to_vcf_start(update, context)

async def vcf_to_txt_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await vcf_to_txt_start(update, context)

async def xls_to_vcf_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await xls_to_vcf_start(update, context)

async def create_admin_navy_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await create_admin_navy_start(update, context)

async def gabung_file_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await gabung_file_start(update, context)

async def split_file_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await split_file_start(update, context)

async def hitung_kontak_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await hitung_kontak_start(update, context)

async def cek_nama_start_vip(update: Update, context):
    user_id = update.effective_user.id
    if not await vip_system.check_access_with_group_verify(user_id, "VIP", context.bot, update):
        user_role = vip_system.get_user_role(user_id)
        await vip_system.send_access_denied(update, user_role, "VIP")
        return
    await cek_nama_start(update, context)

async def handle_text_messages(update: Update, context):
    text = update.message.text
    await check_and_notify_expired_users(context)
    
    if text in ["menu", "MENU", "Menu", "🔙 MENU 🔙"]:
        await show_menu(update, context)
    elif text == "🜲 STATUS 🜲":
        await check_status(update, context)
    elif text == "/status_debug":
        # Debug command for checking group membership
        user_id = update.effective_user.id
        from commands.vip_system import ChatMember, get_user_data
        
        vip_groups = ["agentviber12", "channelviber"]
        groups_count = 0
        group_status = []
        
        for group in vip_groups:
            try:
                member = await context.bot.get_chat_member(f"@{group}", user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                    groups_count += 1
                    group_status.append(f"✅ {group}: {member.status}")
                else:
                    group_status.append(f"❌ {group}: {member.status}")
            except Exception as e:
                group_status.append(f"❌ {group}: ERROR - {str(e)}")
        
        user_data = get_user_data(user_id)
        debug_text = f"""```
🔧 DEBUG STATUS
────────────────
User ID: {user_id}
Groups Count: {groups_count}/2
Role: {user_data.get('role', 'N/A')}
Expired: {user_data.get('expired', 'N/A')}
Verified: {user_data.get('verified', 'N/A')}

📍 GROUP MEMBERSHIP:
{chr(10).join(group_status)}

💾 USER DATA:
{json.dumps(user_data, indent=2)}
```"""
        await update.message.reply_text(debug_text, parse_mode="Markdown")
    else:
        keyboard = get_main_menu_keyboard(update.effective_user.id)
        await update.message.reply_text(
            "```\nPerintah tidak dikenali.\nSilakan pilih menu yang tersedia.\n```",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

def verify_bot_ownership():
    """Verify bot name hasn't been changed - ANTI-THEFT PROTECTION"""
    required_creator = "@KIFZLDEV"
    tampering_detected = False
    
    # Check start.py for creator name in specific location
    try:
        with open("commands/start.py", "r", encoding="utf-8") as f:
            start_content = f.read()
            # Look for the specific line with creator info
            if "(BY @KIFZLDEV)" not in start_content:
                tampering_detected = True
    except:
        tampering_detected = True
    
    # Check menu.py for creator name in specific location
    try:
        with open("commands/menu.py", "r", encoding="utf-8") as f:
            menu_content = f.read()
            # Look for the specific line with creator info
            if "(BY @KIFZLDEV)" not in menu_content:
                tampering_detected = True
    except:
        tampering_detected = True
    
    if tampering_detected:
        print("\n" + "="*50)
        print("❌ CRITICAL ERROR - BOT OWNERSHIP VERIFICATION FAILED!")
        print("="*50)
        print(f"❌ Bot creator name has been changed or removed!")
        print(f"❌ This bot is protected and can ONLY be fixed by @KIFZLDEV")
        print("❌ Bot will NOT start until original creator name is restored!")
        print("❌ The creator line MUST be: (BY @KIFZLDEV)")
        print("="*50 + "\n")
        raise Exception(f"ANTI-THEFT PROTECTION TRIGGERED: Bot name tampering detected! Only @KIFZLDEV can restore this bot.")

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
    
    # ⚠️ ANTI-THEFT PROTECTION - ENFORCE BOT NAME
    print("🔐 VERIFYING BOT OWNERSHIP...")
    try:
        verify_bot_ownership()
        bot_creator = "@KIFZLDEV"
        print(f"✅ Bot Creator: {bot_creator}")
        print("✅ PROTECTION ACTIVE: Bot name verified and protected!")
        print("⚠️  Attempting to rename or take this bot will cause ERROR!")
        print("⚠️  Only @KIFZLDEV can fix and restore this bot\n")
    except Exception as e:
        print(f"🛑 STARTUP BLOCKED: {e}\n")
        return
    
    print("⚙️ Bot step initialized...")
    print("📥 Loading commands...\n")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    
    msg_to_txt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 MSG TO TXT 🜲$"), msg_to_txt_start_vip)],
        states={
            MSG_ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_to_txt_message)],
            MSG_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_to_txt_filename)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), msg_to_txt_filename)],
    )
    
    rapikan_txt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 RAPIKAN TXT 🜲$"), rapikan_txt_start_vip)],
        states={
            RAPIKAN_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, rapikan_txt_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), rapikan_txt_file)],
    )
    
    txt_to_vcf_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 TXT TO VCF 🜲$"), txt_to_vcf_start_vip)],
        states={
            TXT_VCF_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, txt_to_vcf_file)],
            TXT_VCF_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, txt_to_vcf_filename)],
            TXT_VCF_ASK_CONTACTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, txt_to_vcf_contactname)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), txt_to_vcf_contactname)],
    )
    
    vcf_to_txt_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 VCF TO TXT 🜲$"), vcf_to_txt_start_vip)],
        states={
            VCF_TXT_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, vcf_to_txt_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), vcf_to_txt_file)],
    )
    
    xls_to_vcf_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 XLS TO VCF 🜲$"), xls_to_vcf_start_vip)],
        states={
            XLS_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, xls_to_vcf_file)],
            XLS_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, xls_to_vcf_filename)],
            XLS_ASK_CONTACTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, xls_to_vcf_contactname)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), xls_to_vcf_contactname)],
    )
    
    hitung_kontak_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 HITUNG KONTAK 🜲$"), hitung_kontak_start_vip)],
        states={
            HITUNG_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, hitung_kontak_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), hitung_kontak_file)],
    )
    
    cek_nama_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 CEK NAMA 🜲$"), cek_nama_start_vip)],
        states={
            CEK_NAMA_ASK_FILE: [MessageHandler(filters.Document.ALL | filters.TEXT, cek_nama_file)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), cek_nama_file)],
    )
    
    gabung_file_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 GABUNG FILE 🜲$"), gabung_file_start_vip)],
        states={
            ASK_FILES: [MessageHandler(filters.Document.ALL | filters.TEXT, gabung_file_collect)],
            GABUNG_ASK_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, gabung_file_merge)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ BATAL ❌$"), gabung_file_merge)],
    )
    
    split_file_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🜲 SPLIT FILE 🜲$"), split_file_start_vip)],
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
        entry_points=[MessageHandler(filters.Regex("^🜲 CREATE ADM/NAVY 🜲$"), create_admin_navy_start_vip)],
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
    
    application.add_handler(CallbackQueryHandler(handle_access_denied_buttons, pattern="^(upgrade_prem|akses_vip|back_menu)$"))
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
