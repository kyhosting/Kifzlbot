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

def format_expired_date(days):
    """Format expiry date dengan jam:menit"""
    expired = datetime.now() + timedelta(days=days)
    return expired.strftime("%Y-%m-%d %H:%M:%S")

def format_duration_readable(days):
    """Convert days to readable format (hari/bulan/tahun)"""
    if days <= 0:
        return "Permanent"
    
    months = days // 30
    remaining_days = days % 30
    years = months // 12
    remaining_months = months % 12
    
    parts = []
    if years > 0:
        parts.append(f"{years} tahun")
    if remaining_months > 0:
        parts.append(f"{remaining_months} bulan")
    if remaining_days > 0:
        parts.append(f"{remaining_days} hari")
    
    if not parts:
        return f"{days} hari"
    
    return ", ".join(parts)

def calculate_expiry_date(days):
    """Calculate exact expiry date"""
    if days <= 0:
        return "Permanent (tidak ada tanggal kadaluarsa)"
    
    expired = datetime.now() + timedelta(days=days)
    return expired.strftime("%d-%m-%Y %H:%M:%S")
