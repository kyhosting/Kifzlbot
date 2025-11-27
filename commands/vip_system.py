import json
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ContextTypes

OWNER_ID = 8317563450
VIP_GROUPS = ["https://t.me/agentviber12", "https://t.me/channelviber"]
VIP_GROUP_IDS = []

def get_vip_group_ids():
    return VIP_GROUP_IDS or []

def load_users():
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            for uid in data:
                if "expired" in data[uid] and data[uid]["expired"]:
                    try:
                        data[uid]["expired"] = datetime.strptime(data[uid]["expired"], "%Y-%m-%d %H:%M:%S")
                    except:
                        data[uid]["expired"] = None
            return data
    except FileNotFoundError:
        return {}

def save_users(data):
    def serializer(obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return obj
    
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2, default=serializer)

def get_user_role(user_id):
    if user_id == OWNER_ID:
        return "OWNER"
    
    users = load_users()
    user_data = users.get(str(user_id), {})
    
    if user_data.get("role") in ["PREMIUM", "VIP"]:
        expired = user_data.get("expired")
        if expired:
            if isinstance(expired, str):
                try:
                    expired = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
                except:
                    return "FREE"
            if expired > datetime.now():
                return user_data.get("role", "FREE")
    
    return "FREE"

def check_access(user_id, required_role="VIP"):
    role_hierarchy = {"FREE": 0, "VIP": 1, "PREMIUM": 2, "OWNER": 3}
    user_role = get_user_role(user_id)
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

async def send_access_denied(update: Update, user_role: str, required_role: str):
    text = f"""```
──────────────────────────
🔒 AKSES DITOLAK
──────────────────────────
Role Anda          : {user_role}
Akses Dibutuhkan   : {required_role}

Silakan pilih opsi di bawah ini untuk
mendapatkan akses:
──────────────────────────
```"""
    
    keyboard = [
        [InlineKeyboardButton("💎 UPGRADE PREMIUM 💎", callback_data="upgrade_prem")],
        [InlineKeyboardButton("🎟 AKSES VIP 🎟", callback_data="akses_vip")],
        [InlineKeyboardButton("🔙 MENU 🔙", callback_data="back_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def send_access_revoked(update: Update):
    """Send message when VIP access is revoked"""
    text = """```
⚠️ AKSES DICABUT

Anda telah keluar dari grup VIP kami.
Akses VIP Anda telah dihapus otomatis.

Untuk mendapatkan akses kembali:
1. Join ke salah satu grup kami
2. Verifikasi akun Anda

Grup VIP:
📌 @agentviber12
📌 @channelviber
```"""
    
    keyboard = [
        [InlineKeyboardButton("👥 Join Grup 1", url="https://t.me/agentviber12")],
        [InlineKeyboardButton("👥 Join Grup 2", url="https://t.me/channelviber")],
        [InlineKeyboardButton("🔙 MENU 🔙", callback_data="back_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def check_access_with_group_verify(user_id, required_role, bot, update):
    """Check access AND verify user is still in VIP groups"""
    user_role = get_user_role(user_id)
    
    if user_role == "OWNER":
        return True
    
    if user_role != "VIP" and user_role != "PREMIUM":
        return False
    
    vip_groups = ["agentviber12", "channelviber"]
    is_in_group = False
    
    for group in vip_groups:
        try:
            member = await bot.get_chat_member(f"@{group}", user_id)
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                is_in_group = True
                break
        except:
            pass
    
    if not is_in_group:
        update_user_data(user_id, {
            "role": "FREE",
            "expired": None,
            "verified": False
        })
        await send_access_revoked(update)
        return False
    
    return True

def get_user_data(user_id):
    users = load_users()
    return users.get(str(user_id), {})

def update_user_data(user_id, data):
    users = load_users()
    user_str = str(user_id)
    
    if user_str not in users:
        users[user_str] = {}
    
    users[user_str].update(data)
    save_users(users)

def load_sessions():
    try:
        with open("sessions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_session(user_id, session_data):
    sessions = load_sessions()
    user_str = str(user_id)
    
    def serializer(obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return obj
    
    if user_str not in sessions:
        sessions[user_str] = {}
    
    sessions[user_str].update(session_data)
    sessions[user_str]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("sessions.json", "w") as f:
        json.dump(sessions, f, indent=2, default=serializer)

def get_session(user_id):
    sessions = load_sessions()
    return sessions.get(str(user_id), {})

def clear_session(user_id):
    sessions = load_sessions()
    user_str = str(user_id)
    
    if user_str in sessions:
        del sessions[user_str]
        with open("sessions.json", "w") as f:
            json.dump(sessions, f, indent=2)

async def check_user_in_groups(user_id, application):
    """Check if user is member of VIP groups and auto-grant VIP access"""
    try:
        group_ids = ["-1001234567890", "-1001987654321"]
        for group_id in group_ids:
            try:
                member = await application.bot.get_chat_member(group_id, user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                    grant_vip_7days(user_id)
                    return True
            except:
                pass
        return False
    except:
        return False

def grant_vip_7days(user_id):
    """Auto-grant VIP access for 7 days"""
    expired_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    update_user_data(user_id, {
        "role": "VIP",
        "expired": expired_date,
        "auto_verified": True
    })
