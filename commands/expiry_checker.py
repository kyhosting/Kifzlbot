import json
from datetime import datetime
from telegram.ext import ContextTypes

async def check_and_notify_expired_users(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        
        for user_id, user_data in users.items():
            if user_data.get("role") in ["VIP", "PREMIUM"]:
                expired = user_data.get("expired")
                
                if expired:
                    if isinstance(expired, str):
                        try:
                            expired_dt = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
                        except:
                            continue
                    else:
                        expired_dt = expired
                    
                    now = datetime.now()
                    time_diff = (expired_dt - now).total_seconds()
                    
                    notified = user_data.get("expiry_notified", False)
                    
                    if time_diff <= 0 and not notified:
                        notification = f"""```
⏰ NOTIFIKASI MASA AKTIF HABIS

Masa aktif VIP/PREMIUM Anda sudah habis!

❌ Status: TIDAK AKTIF
⌛ Tanggal Berakhir: {expired_dt.strftime('%d-%m-%Y %H:%M')}

Untuk melanjutkan akses, silakan:
💎 Beli Premium paket baru
🎟  Redeem Code gratis dari owner

Terima kasih telah menggunakan layanan kami! 🙏
```"""
                        
                        try:
                            await context.bot.send_message(
                                chat_id=int(user_id),
                                text=notification,
                                parse_mode="Markdown"
                            )
                            
                            users[user_id]["expiry_notified"] = True
                            with open("users.json", "w") as f:
                                json.dump(users, f, indent=2)
                        except Exception as e:
                            pass
    except Exception as e:
        pass
