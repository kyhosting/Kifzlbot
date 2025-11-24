import os
import re
import sys
import subprocess
import vobject
import json
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyrogram import Client, filters, idle
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyrogram.errors import FloodWait
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
import platform
import time

#====================
#Initiator Install dbs
#====================

bot = Client(
    name="OKTOCV",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

START_TIME = time.time()
#====================
#Function Converting!
#====================

def get_runtime():
    seconds = int(time.time() - START_TIME)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def remove_numbers(name):
    return re.sub(r'\d+', '', name).strip()

def read_vcf(file_path):
    with open(file_path, 'r') as file:
        vcard_data = file.read()
    return vobject.readComponents(vcard_data)

def write_vcf(contacts, file_path):
    with open(file_path, 'w') as file:
        for contact in contacts:
            file.write(contact.serialize())

#TOTAL CTC
def count_contacts_in_vcf(file_path):
    contacts = list(read_vcf(file_path))
    return len(contacts)

def count_contacts_in_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        numbers = re.findall(r'\d+', content)
        return len(numbers)

def remove_emojis(text):
    # Regular expression pattern to match emojis
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def rename_contacts(contacts, start_index=1):
    renamed_contacts = []
    for index, contact in enumerate(contacts, start=start_index):
        if hasattr(contact, 'fn'):
            clean_name = remove_numbers(contact.fn.value)
            clean_name = remove_emojis(clean_name)
            contact.fn.value = f'{clean_name} {str(index).zfill(4)}'
        renamed_contacts.append(contact)
    return renamed_contacts
    
def split_vcf(input_file, newna, contacts_per_file=100):
    contacts = list(read_vcf(input_file))
    total_contacts = len(contacts)
    file_count = (total_contacts + contacts_per_file - 1) // contacts_per_file  # jumlah file
    dump_ = []
    global_index = 1  # counter penomoran lintas file

    for i in range(file_count):
        start = i * contacts_per_file
        end = min(start + contacts_per_file, total_contacts)
        contacts_chunk = rename_contacts(contacts[start:end], start_index=global_index)
        output_file = f'{newna}-{i+1}.vcf'
        write_vcf(contacts_chunk, output_file)
        dump_.append(output_file)
        global_index += len(contacts_chunk)  # lanjutkan penomoran

    return dump_
    
def split_vcf_session(input_file, newna, contacts_per_file=100, start_index=1):
    contacts = list(read_vcf(input_file))
    total_contacts = len(contacts)
    file_count = (total_contacts + contacts_per_file - 1) // contacts_per_file
    dump_ = []
    global_index = start_index

    for i in range(file_count):
        start = i * contacts_per_file
        end = min(start + contacts_per_file, total_contacts)
        chunk = rename_contacts(contacts[start:end], start_index=global_index)
        filename = f"{newna}-{i+1}.vcf"
        write_vcf(chunk, filename)
        dump_.append(filename)
        global_index += len(chunk)

    return {
        "files": dump_,
        "next_index": global_index
    }

def split_cut_vcf(input_file, namectc, dibagi_menjadi_bagian=1):
    contacts = list(read_vcf(input_file))
    total_contacts = len(contacts)
    contacts_per_file = (total_contacts + dibagi_menjadi_bagian - 1) // dibagi_menjadi_bagian

    dump_ = []
    file_index = 1
    current_contacts = []
    global_index = 1

    for i, contact in enumerate(contacts, start=1):
        current_contacts.append(contact)
        if len(current_contacts) == contacts_per_file and file_index < dibagi_menjadi_bagian:
            output_file = f'{namectc.replace(".vcf", "")}-{file_index}.vcf'
            renamed_chunk = rename_contacts(current_contacts, global_index)
            write_vcf(renamed_chunk, output_file)
            dump_.append(output_file)
            global_index += len(current_contacts)
            current_contacts = []
            file_index += 1

    if current_contacts:
        output_file = f'{namectc.replace(".vcf", "")}-{file_index}.vcf'
        renamed_chunk = rename_contacts(current_contacts, global_index)
        write_vcf(renamed_chunk, output_file)
        dump_.append(output_file)

    return dump_

def merge_vcf_files(file_paths, output_file_path):
    merged_contacts = []
    for file_path in file_paths:
        contacts = read_vcf(file_path)
        merged_contacts.extend(contacts)
    write_vcf(merged_contacts, f"{output_file_path}.vcf")

def create_vcf_entry(phone_number, contact_name):
    vcf_entry = f"""BEGIN:VCARD
VERSION:3.0
FN:{contact_name}
TEL;TYPE=CELL:{"+" if not str(phone_number).startswith("0") else ""}{phone_number}
END:VCARD
"""
    return vcf_entry

def create_vcf_file(phone_numbers, ctcname, file_name, start_index=1):
    with open(file_name, "w") as file:
        for i, phone_number in enumerate(phone_numbers, start=start_index):
            vcf_entry = create_vcf_entry(phone_number, f"{ctcname}-{str(i).zfill(4)}")
            file.write(vcf_entry + "\n")
    return file_name

def create_vcf_nvy_file(admin_numbers, navy_numbers, file_name):
    with open(file_name, "w") as file:
        index = 1
        for phone_number in admin_numbers:
            vcf_entry = create_vcf_entry(phone_number, f"ADMIN-{str(index).zfill(4)}")
            file.write(vcf_entry + "\n")
            index += 1
        for phone_number in navy_numbers:
            vcf_entry = create_vcf_entry(phone_number, f"NAVY-{index}")
            file.write(vcf_entry + "\n")
            index += 1
    return file_name

def extract_numbers_from_file(file_path):
    numbers = []
    with open(file_path, 'r') as file:
        content = file.read()
        numbers = re.findall(r'\d+', content)
    return numbers

def process_filesgbg(file_paths, output_file):
    all_numbers = []
    for file_path in file_paths:
        if os.path.isfile(file_path):
            numbers = extract_numbers_from_file(file_path)
            all_numbers.extend(numbers)
        else:
            print(f"File {file_path} tidak ditemukan.")
    with open(output_file, 'w') as file:
        for number in all_numbers:
            file.write(number + '\n')

def extract_phone_numbers(vcf_file_path, output_txt_file_path):
    with open(vcf_file_path, 'r') as vcf_file:
        vcf_content = vcf_file.read()
    vcard_list = vobject.readComponents(vcf_content)
    with open(output_txt_file_path, 'w') as txt_file:
        for vcard in vcard_list:
            if hasattr(vcard, 'tel'):
                for tel in vcard.tel_list:
                    txt_file.write(tel.value + '\n')

def hapus_spasi_antar_nomor(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    modified_lines = [''.join(line.split()) + '\n' for line in lines]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)
    modified_lines = [line.replace('-', '') for line in modified_lines]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)
    modified_lines = [line.replace('(', '') for line in modified_lines]
    modified_lines = [line.replace(')', '') for line in modified_lines]
    modified_lines = [line.replace('/', '') for line in modified_lines]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)

#====================
#Database and Coin
#====================

class dbs:
    _buyer = {}

class session:
    split_counter = 1
    file_counter = 1
    
def load_data():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
            cleaned_data = {}
            for uid, value in data.items():
                if not isinstance(value, dict):
                    continue
                expired = value.get("expired")
                if expired:
                    try:
                        expired = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        expired = datetime.now()
                    value["expired"] = expired
                cleaned_data[int(uid)] = value
            return cleaned_data
    except FileNotFoundError:
        return {}
    
def save_data():
    def serializer(obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return obj

    with open('data.json', 'w') as file:
        json.dump(dbs._buyer, file, indent=2, default=serializer)

def parse_timedelta(time_str):
    pattern = r'(\d+)([hmb])'
    time_dict = {'h': 'days', 'm': 'weeks', 'b': 'months'}
    matches = re.findall(pattern, time_str)
    if not matches:
        return None
    kwargs = {'days': 0, 'weeks': 0, 'months': 0}
    for value, unit in matches:
        kwargs[time_dict[unit]] += int(value)
    return kwargs

def add_time_delta(current_time, time_str):
    delta_dict = parse_timedelta(time_str)
    if not delta_dict:
        return None
    new_time = current_time + timedelta(days=delta_dict['days'], weeks=delta_dict['weeks'])
    new_time = new_time + relativedelta(months=delta_dict['months'])
    return new_time
    
session_lanjutan = {
    "split_counter": 1,   # untuk penomoran kontak
    "file_counter": 1     # untuk nama file
}

def split_vcf_custom_start_session(input_file, newna, contacts_per_file=100, start_number=1, start_file=1):
    contacts = list(read_vcf(input_file))
    total_contacts = len(contacts)
    file_count = (total_contacts + contacts_per_file - 1) // contacts_per_file
    dump_ = []
    global_index = start_number
    file_index = start_file

    for _ in range(file_count):
        start = (file_index - start_file) * contacts_per_file
        end = min(start + contacts_per_file, total_contacts)
        chunk = rename_contacts(contacts[start:end], start_index=global_index)
        filename = f"{newna}-{file_index}.vcf"
        write_vcf(chunk, filename)
        dump_.append(filename)
        global_index += len(chunk)
        file_index += 1

    return dump_, global_index, file_index

#====================
#Filters User And More
#====================

home_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💎 Status 💎")],
    [KeyboardButton("📨 ADMIN 📨"), KeyboardButton("🚧 RAPIKAN TXT 🚧")],
    [KeyboardButton("📊 POTONG VCF 📊"), KeyboardButton("📊 POTONG LANJUTAN 📊")],
    [KeyboardButton("🪓 BAGI VCF 🪓"), KeyboardButton("🪓 BAGI LANJUTAN 🪓")],
    [KeyboardButton("️📨 MSG to TXT 📨")],
    [KeyboardButton("🏷️ TXT to VCF 🏷️"), KeyboardButton("🚀 XLS to VCF 🚀")],
    [KeyboardButton("♻️ VCF to TXT ♻️"), KeyboardButton("🗄️ Gabung TXT 🗄️")],
    [KeyboardButton("🗄️ Gabung VCF 🗄️"), KeyboardButton("🔢 Hitung Kontak 🔢")],
    [KeyboardButton("🔍 Cek Nama Kontak 🔍")]
], resize_keyboard=True)

def on_msg(pilter=None):
    def wrapper(func):
        @bot.on_message(pilter)
        async def wrapped_func(client, message):
            try:
                await func(client, message)
            except Exception as err:
                await message.reply(f"Errors:\n{err}")
        return wrapped_func
    return wrapper

def on_txt(message):
    if message.document:
        if message.document.file_name.endswith(".txt"):
            return True
    return False

def on_vcf(message):
    if message.document:
        if message.document.file_name.endswith(".vcf"):
            return True
    return False

def on_xls(message):
    if message.document:
        if message.document.file_name.endswith(".xls") or message.document.file_name.endswith(".xlsx"):
            return True
    return False

def ngecek_(user_id):
    if user_id not in dbs._buyer:
        return False
    data = dbs._buyer[user_id]
    if not data.get("expired"):
        return False
    return data["expired"] > datetime.now()

def batals(text):
    if text == "❌ Batal ❌":
        return True
    return False

def load_all_users():
    try:
        with open("users_all.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_all_users(data):
    with open("users_all.json", "w") as f:
        json.dump(data, f, indent=2)
        
#====================
#Core Modules initiator
#====================
@on_msg(filters.command("start") & filters.private)
async def start_(client, message):
    user_id = str(message.from_user.id)
    name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    username = f"@{message.from_user.username}" if message.from_user.username else "-"

    # Simpan semua user yang pernah start
    all_users = load_all_users()
    if user_id not in all_users:
        all_users[user_id] = {
            "name": name,
            "username": username,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_all_users(all_users)

    # Salam singkat + info
    await message.reply(
        f"👋 Hai <b>{name}</b>!\n\n"
        f"Selamat datang di <b>Bot Konversi Kontak</b>.\n"
        f"Ketik <code>/help</code> untuk melihat daftar fitur.",
        reply_markup=home_keyboard
    )

#===========[RAPIHKAN TXT]

@on_msg(filters.command("🚧 Rapikan TXT 🚧", "") & filters.private)
async def ngecremotate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @@Soyydev😋</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang mau lu convert! (wajib .txt)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_txt(ask1) or batals(ask1.text):
        return await message.reply("<b><i>Itu bukan .txt tolol\n\nProses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    hapus_spasi_antar_nomor(file)
    try:
        await message.reply_document(file)
        await message.reply(f"<b><i> Selesai merapihkan txt</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(file)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    os.remove(file)

#===========[STATUS]
@on_msg(filters.command("💎 Status 💎", "") & filters.private)
async def status_user(client, message):
    user_id = message.from_user.id

    # Pastikan user terdaftar
    if user_id not in dbs._buyer:
        return await message.reply(
            "<b><i>Anda belum memiliki akses.\n\nHubungi @@Deckro08 untuk mendapatkannya.</i></b>"
        )

    data = dbs._buyer[user_id]
    nama = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    username = f"@{message.from_user.username}" if message.from_user.username else data.get("username", "-")
    saldo = data.get("saldo", 0)

    expired = data.get("expired")
    if isinstance(expired, str):
        try:
            expired = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S.%f")
        except:
            try:
                expired = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
            except:
                expired = None
    expired_str = expired.strftime("%Y-%m-%d %H:%M:%S") if expired else "-"

    txt = (
        f"<b>💎 STATUS AKSES 💎</b>\n\n"
        f"<b>ID:</b> <code>{user_id}</code>\n"
        f"<b>Nama:</b> <code>{nama}</code>\n"
        f"<b>Username:</b> <code>{username}</code>\n"
        f"<b>Saldo:</b> <code>{saldo}</code>\n"
        f"<b>Expired:</b> <code>{expired_str}</code>"
    )

    await message.reply(txt, reply_markup=home_keyboard)

#===========[MSG TO TXT]

@on_msg(filters.command("️📨 MSG to TXT 📨", "") & filters.private)
async def ngecreate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    ask1 = await client.ask(text="<b><i>Masukkan nomor yang ingin anda ubah jadi file!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    newname = ask2.text
    with open(f"{newname}.txt", 'w') as file:
        file.write(ask1.text)
    try:
        await message.reply_document(f"{newname}.txt")
        await message.reply(f"<b><i> Selesai merubah massage to txt</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(f"{newname}.txt")
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    return os.remove(f"{newname}.txt")

#===========[ADM DAN NAVY]

@on_msg(filters.command("📨 ADMIN 📨", "") & filters.private)
async def ngecreateadmin(client, message):
    user_id = message.from_user.id
    if not ngecek_(user_id):
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")

    # Minta nomor admin saja
    ask1 = await client.ask(
        text="<b><i>Masukkan nomor admin!</b></i>",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )

    if batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)

    dmp_adm = ask1.text.split()

    # Buat file VCF admin
    file_name = 'ADMIN.vcf'
    with open(file_name, "w") as file:
        for index, phone_number in enumerate(dmp_adm, start=1):
            vcf_entry = create_vcf_entry(phone_number, f"ADMIN-{str(index).zfill(4)}")
            file.write(vcf_entry + "\n")

    try:
        await message.reply_document(file_name)
        await message.reply(
            f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nFile ADMIN berhasil dibuat.</b></i>",
            reply_markup=home_keyboard
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(file_name)
    except:
        pass
    os.remove(file_name)

#===========[XLS TO VCF]

@on_msg(filters.command("🚀 XLS to VCF 🚀", "") & filters.private)
async def ngexlseate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .xls)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_xls(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i></b>Proses dibatalkan</i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".txt", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan nama contact baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or batals(ask3.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask3.text == "⭕️ Skip ⭕️":
        newnamk = ask2.text
    else:
        newnamk = ask3.text
    cont_all = []
    df = pd.read_excel(file)
    ls_cont = df.values.flatten().tolist()
    for isi in ls_cont:
        isi_ = str(isi).replace("+", "")
        if isi_.isnumeric():
            cont_all.append(isi_)
    if not cont_all:
        return await message.reply("<b><i>Contact tidak ditemukan!</b></i>")
    dump_ = create_vcf_file(cont_all, newnamk, f'{newname}.vcf', start_index=1)
    try:
        await message.reply_document(dump_)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(dump_)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    os.remove(dump_)
    os.remove(file)

#===========[TXT TO VCF]

@on_msg(filters.command("🏷️ TXT to VCF 🏷️", "") & filters.private)
async def ngecreate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .txt)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_txt(ask1) or batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".txt", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan nama contact baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or batals(ask3.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask3.text == "⭕️ Skip ⭕️":
        newnamk = ask2.text
    else:
        newnamk = ask3.text
    cont_all = []
    with open(file, 'r') as f:
        ls_cont = f.read().split()
        for isi in ls_cont:
            isi_ = isi.replace("+", "")
            if isi_.isnumeric():
                cont_all.append(isi_)
    if not cont_all:
        return await message.reply("<b><i>Contact tidak ditemukan!</b></i>")
    dump_ = create_vcf_file(cont_all, newnamk, f'{newname}.vcf')
    try:
        await message.reply_document(dump_)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(dump_)
    except:
        pass
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    os.remove(dump_)
    os.remove(file)

#===========[BAGI VCF]

@on_msg(filters.command("🪓 BAGI VCF 🪓", "") & filters.private)
async def ngevcfkan(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .vcf)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_vcf(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".cvf", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan berapa jumlah file barunya!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or not ask3.text.isnumeric() or ask3.text == "0":
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    hsl = split_cut_vcf(file, newname, int(ask3.text))
    for isi in hsl:
        try:
            await message.reply_document(isi)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_document(isi)
        except:
            pass
        os.remove(isi)
    os.remove(file)
    try:
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass

#===========[POTONG VCF]
@on_msg(filters.command("📊 POTONG VCF 📊", "") & filters.private)
async def potong_vcf_berlanjut(client, message):
    user_id = message.from_user.id
    if not ngecek_(user_id):
        return await message.reply("<b><i>Anda tidak memiliki akses.\n\nMau akses? hubungi @Deckro08</b></i>", reply_markup=home_keyboard)

    # Reset counter saat memulai proses baru
    session.split_counter = 1
    session.file_counter = 1

    await lanjutkan_potong(client, message, user_id)
    
async def lanjutkan_potong(client, message, user_id):
    ask1 = await client.ask(
        text="📤 Kirim file VCF yang ingin dipotong:",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if not on_vcf(ask1) or batals(ask1.text):
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)

    file = await ask1.download()

    ask2 = await client.ask(
        text="📎 Masukkan nama file output (tanpa .vcf):",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️"), KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if batals(ask2.text):
        os.remove(file)
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)

    if ask2.text == "⭕️ Skip ⭕️":
        newname = os.path.splitext(ask1.document.file_name)[0]
    else:
        newname = ask2.text

    ask3 = await client.ask(
        text="🔢 Masukkan jumlah kontak per file:",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if batals(ask3.text) or not ask3.text.isnumeric() or int(ask3.text) <= 0:
        os.remove(file)
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)

    kontak_per_file = int(ask3.text)

    hasil = split_vcf_session(
    file, newname, kontak_per_file,
    start_index=session.split_counter,
    start_file=session.file_counter
)

    for f in hasil["files"]:
        try:
            await message.reply_document(f)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_document(f)
        except:
            pass
        os.remove(f)

    session.split_counter = hasil["next_index"]
    session.file_counter = hasil["next_file_index"]
    os.remove(file)

    lanjut = await client.ask(
        text=f"✅ Selesai memotong hingga {session.split_counter - 1:04d}.\n\nIngin lanjut potong file berikutnya?",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("➕ Lanjut"), KeyboardButton("✅ Selesai")]
        ], resize_keyboard=True)
    )

    if lanjut.text == "➕ Lanjut":
        return await lanjutkan_potong(client, message, user_id)

    return await message.reply("✅ Semua proses selesai.", reply_markup=home_keyboard)


def split_vcf_session(input_file, newna, contacts_per_file=100, start_index=1, start_file=1):
    contacts = list(read_vcf(input_file))
    total_contacts = len(contacts)
    file_count = (total_contacts + contacts_per_file - 1) // contacts_per_file
    dump_ = []
    global_index = start_index
    file_index = start_file

    for i in range(file_count):
        start = i * contacts_per_file
        end = min(start + contacts_per_file, total_contacts)
        chunk = rename_contacts(contacts[start:end], start_index=global_index)
        filename = f"{newna}-{file_index}.vcf"
        write_vcf(chunk, filename)
        dump_.append(filename)
        global_index += len(chunk)
        file_index += 1

    return {
        "files": dump_,
        "next_index": global_index,
        "next_file_index": file_index
    }

#===========[GABUNG VCF]

@on_msg(filters.command("🗄️ Gabung VCF 🗄️", "") & filters.private)
async def ngecreategabung(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    allfile = []
    while True:
        asking = await client.ask(text="<b><i>Kirim file yang ingin anda gabung! (wajib .vcf)\n\nNote: Jika sudah memasukkan 2 file / lebih anda dapan menekan tombol done</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Done ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
        if asking.text:
            if batals(asking.text):
                return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
            elif asking.text == "⭕️ Done ⭕️":
                if len(allfile) < 2:
                    return await message.reply("<b><i>Proses gagal, mohon masukkan 2 file atau lebih!!</b></i>", reply_markup=home_keyboard)
                break
        elif not on_vcf(asking):
            return await message.reply("<b><i>File invalid, proses dibatalkan!!</b></i>", reply_markup=home_keyboard)
        file = await asking.download()
        allfile.append(file)
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    merge_vcf_files(allfile, ask2.text)
    await message.reply_document(f"{ask2.text}.vcf")
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    allfile.append(f"{ask2.text}.vcf")
    for isine in allfile:
        os.remove(isine)

#===========[GABUNG TXT]

@on_msg(filters.command("🗄️ Gabung TXT 🗄️", "") & filters.private)
async def ngecreatetxtgbg(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    allfile = []
    while True:
        asking = await client.ask(text="<b><i>Kirim file yang ingin anda gabung! (wajib .txt)\n\nNote: Jika sudah memasukkan 2 file / lebih anda dapan menekan tombol done</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Done ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
        if asking.text:
            if batals(asking.text):
                return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
            elif asking.text == "⭕️ Done ⭕️":
                if len(allfile) < 2:
                    return await message.reply("<b><i>Proses gagal, mohon masukkan 2 file atau lebih!!</b></i>", reply_markup=home_keyboard)
                break
        elif not on_txt(asking):
            return await message.reply("<b><i>File invalid, proses dibatalkan!!</b></i>", reply_markup=home_keyboard)
        file = await asking.download()
        allfile.append(file)
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    process_filesgbg(allfile, f"{ask2.text}.txt")
    await message.reply_document(f"{ask2.text}.txt")
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    allfile.append(f"{ask2.text}.txt")
    for isine in allfile:
        os.remove(isine)

#===========[VCF TO TXT]

@on_msg(filters.command("♻️ VCF to TXT ♻️", "") & filters.private)
async def ngetxtkanvcf(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .vcf)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_vcf(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".vcf", ".txt")
    else:
        newname = f"{ask2.text}.txt"
    extract_phone_numbers(file, newname)
    await message.reply_document(newname)
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    os.remove(file)
    os.remove(newname)
    
#===========[HITUNG CTC]

@on_msg(filters.command("🔢 Hitung Kontak 🔢", "") & filters.private)
async def count_contacts_handler(client, message):
    user_id = message.from_user.id
    if not ngecek_(user_id):
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>", reply_markup=home_keyboard)

    ask = await client.ask(
        text="<b><i>Kirim file .vcf atau .txt yang ingin dihitung jumlah kontaknya!</b></i>",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )

    if batals(ask.text) or not ask.document:
        return await message.reply("<b><i>Proses dibatalkan.</b></i>", reply_markup=home_keyboard)

    file = await ask.download()
    try:
        if on_vcf(ask):
            total = count_contacts_in_vcf(file)
            jenis = "VCF"
        elif on_txt(ask):
            total = count_contacts_in_txt(file)
            jenis = "TXT"
        else:
            return await message.reply("<b><i>File tidak valid. Wajib .vcf atau .txt</b></i>", reply_markup=home_keyboard)

        await message.reply(
            f"<b><i>Total kontak dalam file {jenis}:</i></b> <code>{total}</code>",
            reply_markup=home_keyboard
        )
    except Exception as e:
        await message.reply(f"<b><i>Terjadi kesalahan:</i></b>\n<code>{e}</code>", reply_markup=home_keyboard)
    finally:
        os.remove(file)

#===========[ADDUSR]

@on_msg(filters.command("add") & filters.private)
async def add_(client, message):
    user_id = message.from_user.id
    if user_id not in OWNER_ID:
        return await message.reply("Fitur ini hanya bisa digunakan oleh owner.")

    try:
        _, target_id, timeny = message.text.split(maxsplit=2)
        target_id = int(target_id)
    except:
        return await message.reply(
            "Format salah!\n\nContoh: <code>/add 12345678 1b</code>\n\n"
            "Note:\n- b = bulan\n- m = minggu\n- h = hari"
        )

    # Ambil data user dari database, default ke dict kosong jika belum terdaftar
    user_data = dbs._buyer.get(target_id, {})
    
    # Ambil expired saat ini, fallback ke waktu sekarang jika belum ada
    current_expired = user_data.get("expired")
    if isinstance(current_expired, dict) or current_expired is None:
      current_expired = datetime.now()

    # Tambahkan waktu sesuai input
    new_expired = add_time_delta(current_expired, timeny.lower())
    if not new_expired:
        return await message.reply("Format waktu tidak valid. Gunakan akhiran h/m/b.")

    # Update database user
    dbs._buyer[target_id] = {
        "expired": new_expired,
        "name": user_data.get("name", "-"),
        "username": user_data.get("username", "-"),
        "saldo": user_data.get("saldo", 0),
        "log": user_data.get("log", [])
    }

    save_data()
    await message.reply(
        f"<b><i>Berhasil menambahkan user <code>{target_id}</code> selama {timeny}</i></b>"
    )

#===========[REMOVE]

@on_msg(filters.command("remove") & filters.private)
async def remove_(client, message):
    user_id = message.from_user.id
    if user_id not in OWNER_ID:
        return await message.reply("fitur ini hanya bisa digunakan oleh owner")

    if len(message.text.split()) != 2 or not message.text.split()[1].isnumeric():
        return await message.reply("<b>Masukkan input yang valid!</b>\n\nContoh: <code>/remove 91838299</code>")

    _, target_id = message.text.split()
    removed = dbs._buyer.pop(int(target_id), None)
    save_data()

    if removed:
        await message.reply(f"<b><i>Pengguna {target_id} telah dihapus dari akses!</b></i>")
    else:
        await message.reply(f"<b><i>Pengguna {target_id} tidak ditemukan dalam database.</b></i>")

#===========[UPDATE]

@on_msg(filters.command("update") & filters.user(OWNER_ID[0]))
async def update_bot(client, message):
    x = await message.reply("Updating...", quote=True)
    #subprocess.run(['git', 'pull', '-q'])
    await x.edit("Successfully updating, restart!")
    os.execl(sys.executable, sys.executable, "main.py")
    
async def check_exp_loop():
    while True:
        waktu_sekarang = datetime.now()
        expired_users = []

        for buyer in list(dbs._buyer):
            data = dbs._buyer[buyer]
            expired = data.get("expired")

            if not expired:
                continue

            selisih = waktu_sekarang - expired
            if selisih.total_seconds() > 0:
                expired_users.append(buyer)

        for user_id in expired_users:
            del dbs._buyer[user_id]

        save_data()
        await asyncio.sleep(600)

#===========[CHECK]

@on_msg(filters.command("check") & filters.user(OWNER_ID))
async def check_exp_command(client, message):
    await message.reply("Fungsi cek berjalan otomatis di background setiap 10 menit.")
    
#===========[BACKUP]
    
@on_msg(filters.command("backup") & filters.private)
async def backup_data(client, message):
    user_id = message.from_user.id
    if user_id not in OWNER_ID:
        return await message.reply("fitur ini hanya bisa digunakan oleh owner")

    try:
        await message.reply_document("data.json", caption="<b><i>Berikut adalah file backup data akses user.</b></i>")
    except Exception as e:
        await message.reply(f"Gagal mengirim backup: {e}")
        
#===========[USERALL]
 
@on_msg(filters.command("listalluser") & filters.user(OWNER_ID))
async def list_all_user(client, message):
    all_users = load_all_users()

    if not all_users:
        return await message.reply("<b><i>Tidak ada user yang pernah start bot ini.</i></b>")

    teks = f"<b>📋 Daftar Semua User (Total: {len(all_users)})</b>\n\n"

    for uid, data in all_users.items():
        name = data.get("name", "-")
        username = data.get("username", "-")
        teks += f"• <code>{uid}</code> — {name} ({username})\n"

    # Batasan panjang pesan Telegram (4096 char)
    if len(teks) > 4000:
        # Simpan ke file jika terlalu panjang
        with open("list_all_users.txt", "w", encoding="utf-8") as f:
            f.write(teks)
        await message.reply_document("list_all_users.txt")
        os.remove("list_all_users.txt")
    else:
        await message.reply(teks)
 
#===========[LISTUSER]
        
@on_msg(filters.command("listuser") & filters.private)
async def list_user(client, message):
    user_id = message.from_user.id
    if user_id not in OWNER_ID:
        return await message.reply("Fitur ini hanya bisa digunakan oleh owner.")

    aktif_users = {
        uid: data for uid, data in dbs._buyer.items()
        if isinstance(data, dict) and data.get("expired")
    }

    if not aktif_users:
        return await message.reply("<b><i>Tidak ada user yang memiliki akses saat ini.</b></i>")

    teks = "<b><i>Daftar Pengguna yang Memiliki Akses:</i></b>\n\n"

    for uid, data in aktif_users.items():
        expired = data.get("expired")
        try:
            user_info = await client.get_users(uid)
            nama = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip()
            username = f"@{user_info.username}" if user_info.username else "-"
        except:
            nama = data.get("name", "Tidak diketahui")
            username = data.get("username", "-")

        teks += (
            f"• ID: <code>{uid}</code>\n"
            f"  Nama: <code>{nama}</code>\n"
            f"  Username: <code>{username}</code>\n"
            f"  Expired: <code>{expired.strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
        )

    await message.reply(teks)

#===========[CEK ID]

@on_msg(filters.command("id") & filters.private)
async def cek_id(client, message):
    user = message.from_user
    nama = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
    await message.reply(
        f"<b>ID Telegram Anda:</b> <code>{user.id}</code>\n<b>Nama:</b> <code>{nama}</code>",
        reply_markup=home_keyboard
    )

#===========[BROADCAST]
    
def load_all_users():
    try:
        with open("users_all.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@on_msg(filters.command("broadcast") & filters.private)
async def broadcast_(client, message):
    user_id = message.from_user.id
    if user_id not in OWNER_ID:
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>", reply_markup=home_keyboard)

    ask = await client.ask(
        text="<b><i>Ketik isi pesan broadcast yang ingin dikirim ke semua user yang pernah start bot:</b></i>",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )

    if batals(ask.text):
        return await message.reply("<b><i>Broadcast dibatalkan.</b></i>", reply_markup=home_keyboard)

    isi = ask.text
    all_users = load_all_users()
    aktif_users = [int(uid) for uid in all_users.keys()]

    total, sukses, gagal = 0, 0, 0
    for uid in aktif_users:
        total += 1
        try:
            await client.send_message(uid, isi)
            sukses += 1
            await asyncio.sleep(0.2)
        except:
            gagal += 1

    hasil = f"<b>Broadcast selesai!</b>\n\nTotal: {total}\nSukses: {sukses}\nGagal: {gagal}"
    await message.reply(hasil, reply_markup=home_keyboard)
    
#===========[CEK NAMA KONTAK]
@on_msg(filters.command("🔍 Cek Nama Kontak 🔍", "") & filters.private)
async def cek_nama_kontak(client, message):
    user_id = message.from_user.id
    if not ngecek_(user_id):
        return await message.reply("<b><i>lu gada akses kocak\n\nmau punya akses? pm @Soyydev😋</b></i>", reply_markup=home_keyboard)

    ask = await client.ask(
        text="<b><i>Kirim file .vcf yang ingin dicek nama kontaknya!</b></i>",
        user_id=user_id,
        chat_id=user_id,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )

    if batals(ask.text) or not ask.document or not on_vcf(ask):
        return await message.reply("<b><i>Proses dibatalkan atau file tidak valid.</b></i>", reply_markup=home_keyboard)

    file = await ask.download()

    try:
        kontak = list(read_vcf(file))
        daftar_nama = []

        for c in kontak:
            if hasattr(c, 'fn'):
                daftar_nama.append(c.fn.value.strip())

        if not daftar_nama:
            return await message.reply("<b><i>Nama kontak tidak ditemukan dalam file ini.</b></i>", reply_markup=home_keyboard)

        hasil = "<b><i>Nama-nama kontak:</i></b>\n\n"
        hasil += '\n'.join(f"{i+1}. {nama}" for i, nama in enumerate(daftar_nama[:100]))  # Batas 100 agar tidak overload

        await message.reply(hasil, reply_markup=home_keyboard)

    except Exception as e:
        await message.reply(f"<b><i>Gagal membaca file: {e}</b></i>", reply_markup=home_keyboard)
    finally:
        os.remove(file)
        
 #===========[STATISTIK]
@on_msg(filters.command("statistik") & filters.user(OWNER_ID))
async def statistik_bot(client, message):
    total_users = len(dbs._buyer)
    now = datetime.now()
    aktif = 0
    expired = 0
    total_saldo = 0
    online_today = 0

    for uid, data in dbs._buyer.items():
        exp = data.get("expired")
        saldo = data.get("saldo", 0)
        total_saldo += saldo

        if isinstance(exp, datetime):
            if exp > now:
                aktif += 1
                if (now - exp).days <= 0:
                    online_today += 1
            else:
                expired += 1

    teks = (
        f"<b>📊 Statistik Bot:</b>\n\n"
        f"👥 Total User: <code>{total_users}</code>\n"
        f"✅ User Aktif: <code>{aktif}</code>\n"
        f"❌ User Expired: <code>{expired}</code>\n"
        f"💰 Total Saldo Semua User: <code>{total_saldo}</code>\n"
        f"📅 User Aktif Hari Ini: <code>{online_today}</code>"
    )

    await message.reply(teks)
    
#===========[POTONG LANJUTAN]
@on_msg(filters.private & filters.regex("📊 POTONG LANJUTAN 📊"))
async def potong_lanjutan_inline(client, message):
    user_id = message.from_user.id
    if not ngecek_(user_id):
        return await message.reply("❌ Anda tidak memiliki akses.", reply_markup=home_keyboard)

    session_lanjutan["split_counter"] = 1
    session_lanjutan["file_counter"] = 1

    await lanjut_potong_lanjutan(client, message, user_id)


async def lanjut_potong_lanjutan(client, message, user_id):
    # 1. Kirim file VCF
    ask1 = await client.ask(
        chat_id=user_id,
        text="📤 Kirim file VCF:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if not on_vcf(ask1) or batals(ask1.text):
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
    file = await ask1.download()

    # 2. Masukkan nama file output
    ask2 = await client.ask(
        chat_id=user_id,
        text="📎 Masukkan nama file output:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("⭕️ Skip ⭕️"), KeyboardButton("❌ Batal ❌")]],
            resize_keyboard=True
        )
    )
    if batals(ask2.text):
        os.remove(file)
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
    newname = os.path.splitext(ask1.document.file_name)[0] if ask2.text == "⭕️ Skip ⭕️" else ask2.text

    # 3. Jika pertama kali, minta angka awal penomoran & nama file
    if session_lanjutan["split_counter"] == 1:
        ask3 = await client.ask(
            chat_id=user_id,
            text="🔢 Masukkan angka awal penomoran kontak:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
        )
        if batals(ask3.text) or not ask3.text.isnumeric():
            os.remove(file)
            return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
        session_lanjutan["split_counter"] = int(ask3.text)

        ask_file = await client.ask(
            chat_id=user_id,
            text="🔢 Masukkan angka awal nama file:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
        )
        if batals(ask_file.text) or not ask_file.text.isnumeric():
            os.remove(file)
            return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
        session_lanjutan["file_counter"] = int(ask_file.text)

    # 4. Jumlah kontak per file
    ask4 = await client.ask(
        chat_id=user_id,
        text="📄 Masukkan jumlah kontak per file:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if batals(ask4.text) or not ask4.text.isnumeric():
        os.remove(file)
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
    kontak_per_file = int(ask4.text)

    # 5. Proses pemotongan
    hasil, next_index, next_file = split_vcf_custom_start_session(
        file, newname, kontak_per_file,
        session_lanjutan["split_counter"],
        session_lanjutan["file_counter"]
    )

    for f in hasil:
        try:
            await message.reply_document(f)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_document(f)
        os.remove(f)

    session_lanjutan["split_counter"] = next_index
    session_lanjutan["file_counter"] = next_file
    os.remove(file)

    # 6. Tanya lanjut atau selesai
    lanjut = await client.ask(
        chat_id=user_id,
        text="✅ Selesai memotong. Mau lanjut file berikutnya?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("➕ Lanjut"), KeyboardButton("✅ Selesai")]],
            resize_keyboard=True
        )
    )
    if lanjut.text == "➕ Lanjut":
        return await lanjut_potong_lanjutan(client, message, user_id)

    await message.reply("✅ Semua proses selesai.", reply_markup=home_keyboard)

#===========[BAGI LANJUTAN]
@on_msg(filters.private & filters.regex("🪓 BAGI LANJUTAN 🪓"))
async def bagi_lanjutan_inline(client, message):
    user_id = message.from_user.id
    if not ngecek_(user_id):
        return await message.reply("❌ Anda tidak memiliki akses.", reply_markup=home_keyboard)

    session_lanjutan["split_counter"] = 1
    session_lanjutan["file_counter"] = 1

    await lanjut_bagi_lanjutan(client, message, user_id)


async def lanjut_bagi_lanjutan(client, message, user_id):
    # 1. Kirim file VCF
    ask1 = await client.ask(
        chat_id=user_id,
        text="📤 Kirim file VCF yang ingin dibagi:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if not on_vcf(ask1) or batals(ask1.text):
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
    file = await ask1.download()

    # 2. Nama file output
    ask2 = await client.ask(
        chat_id=user_id,
        text="📎 Masukkan nama file output:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("⭕️ Skip ⭕️"), KeyboardButton("❌ Batal ❌")]],
            resize_keyboard=True
        )
    )
    if batals(ask2.text):
        os.remove(file)
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
    newname = os.path.splitext(ask1.document.file_name)[0] if ask2.text == "⭕️ Skip ⭕️" else ask2.text

    # 3. Jika pertama kali, minta angka awal penomoran & nama file
    if session_lanjutan["split_counter"] == 1:
        ask3 = await client.ask(
            chat_id=user_id,
            text="🔢 Masukkan angka awal penomoran kontak:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
        )
        if batals(ask3.text) or not ask3.text.isnumeric():
            os.remove(file)
            return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
        session_lanjutan["split_counter"] = int(ask3.text)

        ask_file = await client.ask(
            chat_id=user_id,
            text="🔢 Masukkan angka awal nama file:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
        )
        if batals(ask_file.text) or not ask_file.text.isnumeric():
            os.remove(file)
            return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
        session_lanjutan["file_counter"] = int(ask_file.text)

    # 4. Jumlah bagian yang diinginkan
    ask4 = await client.ask(
        chat_id=user_id,
        text="🪓 Masukkan jumlah file (bagian) yang ingin dibuat:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True)
    )
    if batals(ask4.text) or not ask4.text.isnumeric() or int(ask4.text) <= 0:
        os.remove(file)
        return await message.reply("❌ Proses dibatalkan.", reply_markup=home_keyboard)
    bagian = int(ask4.text)

    # 5. Proses pembagian dengan rename dan lanjutan
    contacts = list(read_vcf(file))
    total_contacts = len(contacts)
    contacts_per_file = (total_contacts + bagian - 1) // bagian

    dump_ = []
    global_index = session_lanjutan["split_counter"]
    file_index = session_lanjutan["file_counter"]

    for i in range(bagian):
        start = i * contacts_per_file
        end = min(start + contacts_per_file, total_contacts)
        chunk = rename_contacts(contacts[start:end], start_index=global_index)
        filename = f"{newname}-{file_index}.vcf"
        write_vcf(chunk, filename)
        dump_.append(filename)
        global_index += len(chunk)
        file_index += 1

    for f in dump_:
        try:
            await message.reply_document(f)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_document(f)
        os.remove(f)

    session_lanjutan["split_counter"] = global_index
    session_lanjutan["file_counter"] = file_index
    os.remove(file)

    lanjut = await client.ask(
        chat_id=user_id,
        text="✅ Selesai membagi. Mau lanjut file berikutnya?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("➕ Lanjut"), KeyboardButton("✅ Selesai")]],
            resize_keyboard=True
        )
    )
    if lanjut.text == "➕ Lanjut":
        return await lanjut_bagi_lanjutan(client, message, user_id)

    await message.reply("✅ Semua proses selesai.", reply_markup=home_keyboard)

 #===========[HELP]
 
@on_msg(filters.command("help") & filters.private)
async def help_cmd(client, message):
    text = """
<b>📌 Daftar Fitur Bot</b>

🔹 <b>📊 POTONG VCF</b>  
Memecah file VCF besar menjadi beberapa bagian, dengan penomoran kontak dan file yang berurutan.

🔹 <b>📊 BAGI VCF</b>  
Membagi VCF menjadi beberapa bagian berdasarkan jumlah bagian yang diinginkan.

🔹 <b>♻️ VCF to TXT</b>  
Mengubah semua nomor dalam VCF menjadi file .txt.

🔹 <b>🏷️ TXT to VCF</b>  
Mengubah file .txt berisi nomor menjadi file kontak .vcf.

🔹 <b>🚀 XLS to VCF</b>  
Mengubah file Excel menjadi file kontak VCF.

🔹 <b>📨 MSG to TXT</b>  
Mengubah pesan teks menjadi file .txt.

🔹 <b>🚧 RAPIKAN TXT</b>  
Membersihkan spasi/simbol agar file txt berisi nomor yang bersih.

🔹 <b>🗄️ Gabung TXT / VCF</b>  
Menggabungkan beberapa file menjadi satu.

🔹 <b>🔢 Hitung Kontak</b>  
Menghitung jumlah nomor dari file VCF/TXT.

🔹 <b>🔍 Cek Nama Kontak</b>  
Melihat daftar nama yang tersimpan dalam VCF.

🔹 <b>📨 ADMIN</b>  
Membuat file VCF berisi nomor-nomor admin dengan format nama ADMIN-xxxx.

🔹 <b>💎 Status</b>  
Cek status dan masa berlaku akses kamu.

—

<b>❗️ Butuh akses atau ingin menyewa bot ini?</b>  
Silakan hubungi saya langsung melalui:

👉 <b>@Soyydev</b>

Harga sewa murah dan support penuh!
"""
    await message.reply(text, reply_markup=home_keyboard)
 
 #===========[RUNTIME]
@on_msg(filters.command("runtime") & filters.user(OWNER_ID))
async def runtime_handler(client, message):
    os_info = platform.system() + " " + platform.release()
    uptime = get_runtime()
    await message.reply(
        f"🖥️ <b>OS:</b> <code>{os_info}</code>\n"
        f"⏱️ <b>Bot Online:</b> <code>{uptime}</code>"
    )
async def main():
    data_ = load_data()
    dbs._buyer = data_
    await bot.start()
    await check_exp_loop()

if __name__ == "__main__":
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(main())
