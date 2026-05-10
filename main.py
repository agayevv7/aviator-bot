import telebot
import time
import threading
import json
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "⚡ Bot 7/24 Aktivdir!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- AYARLAR --- BURANI DƏYİŞ
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 2083084323
YOUTUBE_URL = "https://youtu.be/QHPnYAeUPnU?si=WlqW1xphnaLTLbz9"
REGISTER_URL = "https://1weucj.life/?open=register&p=mlg1"
AVIATOR_URL = "https://1weucj.life/?open=register&p=mlg1"

bot = telebot.TeleBot(TOKEN)
DB_FILE = "/data/database.json"

def load_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_db = load_db()

def is_banned(uid):
    return user_db.get(str(uid), {}).get('status') == 'banned'

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    if is_banned(uid):
        bot.send_message(uid, "⛔ GİRİŞ MƏHDUDLAŞDIRILDI\n\n📞 Dəstək: @Support")
        return

    if uid not in user_db:
        user_db[uid] = {'status': 'new', 'name': message.from_user.first_name, 'proofs': 0, 'test_used': False}
        save_db(user_db)

    user_status = user_db[uid].get('status')
    test_used = user_db[uid].get('test_used', False)

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    if int(uid) == ADMIN_ID:
        markup.add(telebot.types.InlineKeyboardButton("🧪 Test Siqnal", callback_data="test_req"))
        markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktiv Et", callback_data="show_rules"))
    else:
        if not test_used and user_status!= 'vip':
            markup.add(telebot.types.InlineKeyboardButton("🧪 Pulsuz Test", callback_data="test_req"))
        if user_status!= 'vip':
            markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktiv Et", callback_data="show_rules"))

    msg = (
        f"👋 Xoş gəldin, {message.from_user.first_name}\n\n"
        "✈️ <b>AVIATOR PRO SİQNAL</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🆓 <b>STANDART</b>\n"
        "• Dəqiqlik: 70%\n"
        "• Gecikmə: 5-10 san\n"
        "• Test: 1 pulsuz\n\n"
        "💎 <b>VIP PRO</b>\n"
        "• Dəqiqlik: 95%+\n"
        "• Gecikmə: 0.1 san\n"
        "• Aktivasiya: Pulsuz\n\n"
        "⚠️ <i>VIP üçün yeni 1WIN hesabı şərtdir</i>\n"
        f"🔗 Qeydiyyat: {REGISTER_URL}"
    )
    bot.send_message(uid, msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    uid = str(call.message.chat.id)
    if is_banned(uid): return

    user_data = user_db.get(uid, {})
    user_status = user_data.get('status')
    test_used = user_data.get('test_used', False)

    if call.data == "test_req":
        if int(uid) == ADMIN_ID:
            try:
                bot.send_message(ADMIN_ID,
                    f"🧪 <b>ADMİN TEST</b>\n"
                    f"━━━━━━━━━━━━\n"
                    f"Komanda: <code>/test {uid} 14:20-14:22</code>", parse_mode='HTML'
                )
                bot.answer_callback_query(call.id, "Admin test sorğusu")
            except Exception as e: print(e)
            return

        if test_used or user_status in ['test_sent', 'vip']:
            bot.answer_callback_query(call.id, "❌ Test limitin bitib", show_alert=True)
            bot.edit_message_text(
                "⚠️ <b>TEST LİMİTİ</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Hər user yalnız 1 test ala bilər.\n\n"
                "💎 VIP-ə keçmək üçün aşağıdakı düymə:",
                uid, call.message.message_id,
                reply_markup=telebot.types.InlineKeyboardMarkup().add(
                    telebot.types.InlineKeyboardButton("💎 VIP Aktiv Et", callback_data="show_rules")
                ), parse_mode='HTML'
            )
            return
        try:
            bot.send_message(ADMIN_ID,
                f"🧪 <b>YENİ TEST</b>\n"
                f"━━━━━━━━━━━━\n"
                f"👤 @{call.from_user.username}\n"
                f"🆔 <code>{uid}</code>\n"
                f"📅 {time.strftime('%d.%m.%Y %H:%M')}\n"
                f"━━━━━━━━━━━━\n"
                f"Komanda: <code>/test {uid} 14:20-14:22</code>", parse_mode='HTML'
            )
            bot.edit_message_text(
                "✅ <b>Sorğu alındı</b>\n\n"
                "👨‍💻 Admin sənə test göndərəcək\n"
                "⏳ Gözlə...",
                uid, call.message.message_id, parse_mode='HTML'
            )
        except Exception as e: print(e)

    elif call.data == "show_rules":
        if not test_used and user_status not in ['test_sent', 'vip', 'awaiting_proof'] and int(uid)!= ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Əvvəlcə test et", show_alert=True)
            bot.send_message(uid,
                "⚠️ <b>VIP ŞƏRTİ</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "VIP üçün əvvəl 1 pulsuz test etməlisən.\n\n"
                "🧪 /start yaz və 'Pulsuz Test' seç.\n\n"
                "Testdən sonra VIP açılacaq.", parse_mode='HTML'
            )
            return

        user_db[uid]['status'] = 'awaiting_proof'
        user_db[uid]['proofs'] = 0
        save_db(user_db)

        rules_text = (
            "💎 <b>VIP AKTİVASİYA</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "⚡️ <b>2 ADIM - 95%+ DƏQİQ SİQNAL:</b>\n\n"
            f"1️⃣ <b>YouTube Abunə</b>\n"
            f"👉 {YOUTUBE_URL}\n"
            f"🔔 Zınqırovu aç + Screenshot at 📸\n\n"
            f"2️⃣ <b>Yeni 1WIN Hesab</b>\n"
            f"👉 {REGISTER_URL}\n"
            f"🎁 Promo: <code>yatirimsahesi</code>\n"
            f"✅ ID Screenshot at 📸\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "⏱ <i>2 şəkil = 2 dəqiqəyə VIP</i>\n"
            "📌 <b>Vacib:</b> Hesab yeni olmalıdır\n"
            "❗️ Şəkil aydın olsun"
        )
        bot.send_message(uid, rules_text, disable_web_page_preview=True, parse_mode='HTML')

    elif call.data.startswith("approve_"):
        target_id = call.data.split("_")[1]
        if target_id in user_db:
            user_db[target_id]['status'] = 'vip'
            user_db[target_id]['proofs'] = 0
            save_db(user_db)
            bot.send_message(target_id,
                "🎉 <b>VIP AKTİVDİR</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "✅ Təbriklər, PRO status aldın!\n\n"
                "📊 <b>İmtiyazlar:</b>\n"
                "• 95%+ dəqiqlik\n"
                "• 0.1 san gecikmə\n"
                "• Prioritet siqnal\n\n"
                "🔥 Növbəti siqnalı gözlə.", parse_mode='HTML'
            )
            bot.answer_callback_query(call.id, "VIP edildi!")
            bot.edit_message_text(f"✅ <b>TƏSDİQ</b>\nİstifadəçi: <code>{target_id}</code>", ADMIN_ID, call.message.message_id, parse_mode='HTML')

    elif call.data.startswith("reject_"):
        target_id = call.data.split("_")[1]
        user_db[target_id]['status'] = 'test_sent'
        user_db[target_id]['proofs'] = 0
        save_db(user_db)
        bot.send_message(target_id,
            "❌ <b>RƏDD EDİLDİ</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Məlumatlar keçmədi.\n\n"
            "<b>Səbəb:</b>\n"
            "• Şəkil keyfiyyətsiz\n"
            "• Abunə yoxdu\n"
            "• Link bizimki deyil\n\n"
            "🔄 Yenidən /start", parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "Rədd edildi!")
        bot.edit_message_text(f"❌ <b>RƏDD</b>\nİstifadəçi: <code>{target_id}</code>", ADMIN_ID, call.message.message_id, parse_mode='HTML')

@bot.message_handler(commands=['test'])
def admin_test(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        args = message.text.split(maxsplit=2)
        target_id, vaxt = args[1], args[2]

        if int(target_id)!= ADMIN_ID:
            user_db[target_id]['status'] = 'test_sent'
            user_db[target_id]['test_used'] = True
            save_db(user_db)

        bot.send_message(target_id,
            "📡 <b>HAZIRLIQ</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "⏳ Test 10-15 saniyəyə gəlir.\n\n"
            "📲 Telefona bax.\n"
            "⚠️ <i>Bu test siqnalıdır, gecikmə var.</i>", parse_mode='HTML'
        )

        bot.send_message(ADMIN_ID, f"✅ Hazırlıq göndərildi. 10 san sonra siqnal.\nUser: <code>{target_id}</code>", parse_mode='HTML')
        time.sleep(10)

        msg = (
            "🧪 <b>TEST SİQNAL</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"⏰ Vaxt: <b>{vaxt}</b>\n"
            f"🎮 Oyun: Aviator\n"
            f"🎰 Platforma: 1WIN\n"
            f"🔗 Keçid: {AVIATOR_URL}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🐌 <i>Test: ~10 san gecikmə</i>\n"
            "💎 <b>VIP: 0.1 san gecikmə</b>\n\n"
            "👇 Daimi siqnal üçün:"
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktiv Et", callback_data="show_rules"))
        bot.send_message(target_id, msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='HTML')
        bot.reply_to(message, "✅ Test bitdi")
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {e}\nFormat: /test ID VAXT")

@bot.message_handler(content_types=['photo'])
def handle_proofs(message):
    uid = str(message.chat.id)
    if is_banned(uid): return
    if user_db.get(uid, {}).get('status') == 'awaiting_proof':
        user_db[uid]['proofs'] = user_db[uid].get('proofs', 0) + 1
        proof_count = user_db[uid]['proofs']
        save_db(user_db)

        if proof_count == 1:
            bot.send_message(uid,
                "📩 <b>1/2 QƏBUL</b> ✅\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "2-ci şəkli göndər.\n"
                "⏳ Yoxlanılır...", parse_mode='HTML'
            )
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(ADMIN_ID, f"📸 <b>SƏNƏD 1</b>\n👤 @{message.from_user.username}\n🆔 <code>{uid}</code>", parse_mode='HTML')

        elif proof_count >= 2:
            bot.send_message(uid,
                "📩 <b>2/2 QƏBUL</b> ✅\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Məlumatlar yoxlanılır.\n"
                "⏳ 1-2 dəqiqəyə nəticə.\n"
                "🔔 Bildiriş gələcək.", parse_mode='HTML'
            )
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                telebot.types.InlineKeyboardButton("✅ Təsdiq", callback_data=f"approve_{uid}"),
                telebot.types.InlineKeyboardButton("❌ Rədd", callback_data=f"reject_{uid}")
            )
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(ADMIN_ID,
                f"🔥 <b>YOXLAMA</b>\n"
                f"━━━━━━━━━━━━\n"
                f"👤 @{message.from_user.username}\n"
                f"🆔 <code>{uid}</code>\n"
                f"━━━━━━━━━━━━", reply_markup=markup, parse_mode='HTML'
            )

@bot.message_handler(commands=['aviator'])
def broadcast_signal(message):
    if message.from_user.id!= ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ <b>Format:</b> <code>/aviator VAXT</code>\nNümunə: <code>/aviator 14:20-14:25</code>", parse_mode='HTML')
            return
        vaxt = parts[1]
        vip_signal = "⚡️ <b>VIP SİQNAL</b> ⚡️\n━━━━━━━━━━━━━━━━━━\n\n✈️ <b>Aviator 1WIN</b>\n\n⏰ <b>GİRİŞ:</b> " + vaxt + "\n🎯 <b>HƏDƏF:</b> 10x+\n📊 <b>ŞANS:</b> 95%+\n⚡️ <b>PİNG:</b> 0.1s\n━━━━━━━━━━━━━━━━━━\n💰 <b>İNDİ GİR</b>"
        locked_signal = "🔒 <b>SİQNAL KİLİDLİ</b>\n━━━━━━━━━━━━━━━━━━\n\n✈️ Aviator Siqnalı\n\n⏰ Giriş: <b>KİLİDLİ</b>\n❗️ Yüksək əmsal bu aralıqda\n📊 Proqnoz: 95%\n━━━━━━━━━━━━━━━━━━\n🔓 <b>Açmaq üçün:</b>\n1️⃣ Linklə yeni hesab aç\n2️⃣ Screenshot göndər"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎁 Qeydiyyat", url=REGISTER_URL))
        sent_vip, sent_locked = 0, 0
        for u_id, data in user_db.items():
            if data.get('status') == 'banned':
                continue
            try:
                if data.get('status') == 'vip':
                    bot.send_message(u_id, vip_signal, parse_mode='HTML')
                    sent_vip += 1
                else:
                    bot.send_message(u_id, locked_signal, reply_markup=markup, parse_mode='HTML')
                    sent_locked += 1
                time.sleep(0.05)
            except:
                pass
        bot.reply_to(message, f"✅ <b>PAYLANIŞ BİTDİ</b>\n\n💎 VIP: {sent_vip}\n🔒 Standart: {sent_locked}", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {e}")

@bot.message_handler(commands=['msg'])
def admin_message(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        args = message.text.split(maxsplit=2)
        target_id, text = args[1], args[2]
        bot.send_message(target_id, f"📩 <b>ADMİN MESAJI</b>\n━━━━━━━━━━━━\n{text}", parse_mode='HTML')
        bot.reply_to(message, f"✅ Göndərildi: <code>{target_id}</code>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format: <code>/msg ID MƏTN</code>", parse_mode='HTML')

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        target_id = message.text.split()[1]
        if target_id in user_db:
            user_db[target_id]['status'] = 'banned'
            save_db(user_db)
            bot.send_message(target_id, "⛔ <b>BAN</b>\n\nHesabın bloklandı.", parse_mode='HTML')
            bot.reply_to(message, f"✅ <code>{target_id}</code> banlandı", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ User yoxdur")
    except:
        bot.reply_to(message, "❌ Format: <code>/ban ID</code>", parse_mode='HTML')

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        target_id = message.text.split()[1]
        if target_id in user_db:
            user_db[target_id]['status'] = 'new'
            user_db[target_id]['test_used'] = False
            save_db(user_db)
            bot.send_message(target_id, "✅ <b>UNBAN</b>\n\nBan açıldı. /start yaz.", parse_mode='HTML')
            bot.reply_to(message, f"✅ <code>{target_id}</code> unban", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format: <code>/unban ID</code>", parse_mode='HTML')

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.from_user.id!= ADMIN_ID: return
    text = "👥 <b>USER LİST</b>\n━━━━━━━━━━━━\n"
    for uid, data in user_db.items():
        status_emoji = {"vip":"💎", "banned":"⛔", "new":"🆕", "test_sent":"🧪", "awaiting_proof":"⏳"}.get(data.get('status'), "❓")
        name = data.get('name', 'Adsız').replace('_', ' ').replace('*', ' ')
        test_icon = "✓" if data.get('test_used') else "✗"
        text += f"{status_emoji} <code>{uid}</code> | {name} | {data.get('status')} | Test:{test_icon}\n"
    if len(text) > 4000: text = text[:4000] + "\n..."
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['stat'])
def stats(message):
    if message.from_user.id!= ADMIN_ID: return
    total = len(user_db)
    vip = len([u for u in user_db.values() if u.get('status') == 'vip'])
    test = len([u for u in user_db.values() if u.get('test_used') == True])
    new = len([u for u in user_db.values() if u.get('status') == 'new'])
    banned = len([u for u in user_db.values() if u.get('status') == 'banned'])
    bot.reply_to(message,
        f"📊 <b>STATİSTİKA</b>\n"
        f"━━━━━━━━━━━━\n"
        f"👥 Ümumi: <b>{total}</b>\n"
        f"💎 VIP: <b>{vip}</b>\n"
        f"🧪 Test: <b>{test}</b>\n"
        f"🆕 Yeni: <b>{new}</b>\n"
        f"⛔ Ban: <b>{banned}</b>\n"
        f"━━━━━━━━━━━━", parse_mode='HTML'
    )

if __name__ == '__main__':
    keep_alive()
    print("⚡ Bot PRO - Admin Limitsiz Versiya işə salındı...")
    bot.infinity_polling(skip_pending=True)
