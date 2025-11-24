import random
import string
from datetime import datetime, timedelta

def generate_random_code(length=12):
    """Generate random redeem code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_code_expired(code_data):
    """Check if redeem code has expired"""
    if not code_data.get("code_expired"):
        return False
    
    try:
        expired_dt = datetime.strptime(code_data["code_expired"], "%Y-%m-%d %H:%M:%S")
        return datetime.now() > expired_dt
    except:
        return False

def format_duration_readable(days):
    """Convert days to readable format (hari/bulan)"""
    if days <= 0:
        return "Permanent"
    
    months = days // 30
    remaining_days = days % 30
    
    if months > 0 and remaining_days == 0:
        return f"{months} bulan" if months > 1 else "1 bulan"
    elif months > 0 and remaining_days > 0:
        return f"{months} bulan {remaining_days} hari"
    else:
        return f"{days} hari"

def format_code_expiry_readable(days):
    """Format code expiry date (hari/bulan readable)"""
    if days <= 0:
        return "Permanent"
    
    return format_duration_readable(days)
