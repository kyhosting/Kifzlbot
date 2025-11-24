# KIFZL DEV BOT

## Overview
Bot Telegram lengkap dengan sistem role (FREE/VIP/PREMIUM/OWNER), redeem code, converter tools (TXT/VCF/XLSX), split system, dan fitur Create Admin & Navy.

## Owner Configuration
- Owner ID: 8317563450
- Owner Username: @KIFZLDEV
- VIP Groups (auto-grant VIP 1 minggu):
  - https://t.me/agentviber12
  - https://t.me/channelviber

## Project Structure
```
/KIFZL_DEV_BOT
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── users.json                 # Auto-created: User database
├── redeem.json               # Auto-created: Redeem codes
├── sessions.json             # Auto-created: Session tracking
├── admins.json               # Auto-created: Admin data
└── commands/                 # Modular command handlers
    ├── vip_system.py         # Role authorization system
    ├── start.py              # Start command with user status
    ├── menu.py               # Main menu keyboard
    ├── msg_to_txt.py         # MSG to TXT converter
    ├── rapikan_txt.py        # Clean TXT files
    ├── convert_txt_vcf.py    # TXT to VCF converter
    ├── convert_vcf_txt.py    # VCF to TXT extractor
    ├── convert_xlsx_vcf.py   # Excel to VCF converter
    ├── hitung_kontak.py      # Count contacts
    ├── cek_nama_kontak.py    # Check contact names
    ├── gabung_file.py        # Merge files (TXT/VCF)
    ├── split_file.py         # Split files (per kontak/bagian)
    ├── create_admin_navy.py  # Create Admin & Navy (3 modes)
    ├── redeem.py             # Redeem code system
    ├── upgradeprem.py        # Premium upgrade with inline buttons
    ├── aksesvip.py           # VIP access information
    └── menu_owner.py         # Owner management panel
```

## Features
### Role System
- **FREE**: Limited access
- **VIP**: Partial features (7 days default)
- **PREMIUM**: All features (1/7/30 days packages)
- **OWNER**: Unlimited access + management

### Converter Tools
- MSG → TXT
- TXT → VCF (with custom naming)
- VCF → TXT (extract phone numbers)
- XLSX → VCF (Excel to contacts)

### File Management
- Rapikan TXT (clean formatting)
- Gabung File (merge multiple files)
- Split File (per kontak atau per bagian)
- Hitung Kontak (count contacts)
- Cek Nama Kontak (check contact names)

### Admin & Navy Creator (3 Modes)
- **Mode A - Guided**: Step-by-step input
- **Mode B - Auto Parse**: Block text parsing
- **Mode C - Minimal**: Single number input

### Premium System
- Inline quantity controller [-] [+]
- Paket: 1 Day, 7 Days, 30 Days
- Checkout with owner confirmation

### Redeem System
- Owner creates redeem codes
- Auto-update role and expiry
- Track usage and history

### Owner Panel
- View all users
- Add/Edit user roles
- Create redeem codes
- View statistics

## Recent Changes
- 2024-11-24: Initial project setup
- All features implemented with keyboard button navigation
- Modular architecture for easy maintenance
- Auto-create JSON files on first run
- Session tracking functions implemented (load_sessions, save_session, get_session, clear_session)
- Note: ConversationHandler uses in-memory context.user_data for session state management
- sessions.json available for logging/auditing, full persistence requires custom handler

## Environment Variables
- `TELEGRAM_BOT_TOKEN`: Telegram bot API token (required)

## User Preferences
- All interactions via keyboard buttons (no `/` commands)
- Markdown formatting for all bot messages
- Auto-cleanup temporary files
- Session tracking for multi-step processes
