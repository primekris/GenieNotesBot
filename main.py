

import os
import random
import requests
import telebot
from urllib.parse import quote, unquote
from threading import Thread
from flask import Flask
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           WebAppInfo)

# ── ENV / CONSTANTS ───────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ← Set these
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # ← Optional
ADMIN_ID = 7924807866  # ← Your TG ID

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')
user_ids = set()  # store chat IDs to broadcast/poll later
submitted = {}  # file_id → user_id  (for /reply)

# ── RESOURCES  (updated callback handler supports nested/folder structure) ────────────────────────────────────
resources = {
    "Programming": {
        "Python Basics": "BQACAgUAAxkBAAMEaG_R8NjqW_XmYhOItX0uEJCQYUAAAgMSAAKDJrlUZ202A4cEnKo2BA",
        "Javascript NOTES": "BQACAgUAAxkBAAMRaG_TBQ6S1yKlWN44-9aAxV8Sg1wAAvYWAAKcMkFUyBBP41Smquo2BA",
        "HTML Notes": "BQACAgUAAxkBAAMQaG_TBeLrJyCeaT88vgwMEQpS4UUAAg4OAAJ5gmlVdpqrLMuMzKw2BA",
        "Java Handwritten Concepts": "BQACAgUAAxkBAAMPaG_TBTuxO7GLEoqskuzFQCAmsR4AAiQNAALwrOFVzGa-Irijrs42BA",
        "Operating Systems": "BQACAgUAAxkBAAMOaG_TBbK3xcreEJ_hcglckCsPVrwAAsEMAAKTxthWj1_TdfOsre82BA",
    },
    "Data Structures": {
        "1. Getting Started": "BQACAgEAAxkBAAMWaG_UfK3TuOiLNBTzfR_TYdC_otoAAkYCAALEh7BGYLmX52OonCI2BA",
        "2. Basics": "BQACAgEAAxkBAAMXaG_UfEliC4SyktOB7ryPKm32lK0AAkcCAALEh7BGdlFZ2tTz2rU2BA",
        "3. Operators": "BQACAgEAAxkBAAMYaG_UfBWqdEn1jjjWBrjxa5sSF7YAAkgCAALEh7BGaiZs8nKb_wABNgQ",
        "4. Control Flow": "BQACAgEAAxkBAAMZaG_UfDXUKDCrHhaE42dI9KtJ6XkAAkkCAALEh7BGzWzChXXi5Wc2BA",
        "5. Objects": "BQACAgEAAxkBAAMaaG_UfE7l48lsL9MlYhnNSZ23a1YAAkoCAALEh7BGgbuIutnluRE2BA",
    },
    "Web Development": {
        "CSS Notes": "BQACAgUAAxkBAAMmaG_VjlULYMXj2MhGGRCV908MxuwAAscUAALiQIlWf6N1sPpwDrQ2BA",
        "JavaScript Advanced": "BQACAgUAAxkBAAMRaG_TBQ6S1yKlWN44-9aAxV8Sg1wAAvYWAAKcMkFUyBBP41Smquo2BA",
        "React JS": "BQACAgQAAxkBAAMlaG_VjgFlhUS_0ixl7VSa8COyk8gAAkYaAAJpmFFRJjwh19rV4gk2BA",
        "Mini Project": "BQACAgUAAxkBAAMkaG_Vjk5UMPsXM1d_Ptw62hYG9e4AAukOAAJdJ1lVJ29X769X2vo2BA"
    }
}

# ── DAILY TIPS ────────────────────────────────────────────────
tips = [
    "📌 Study smarter, not harder!",
    "🧠 Review before bed—memory lock 🔐",
    "⏰ Pomodoro: 25 min work + 5 min rest",
    "📚 Consistency ≫ Intensity—practice daily.",
    "🚫 Don’t chase perfect; chase progress.",
    "🔥 If it scares you, it’s worth doing!",
    "💧 Hydrate your brain—drink water!",
    "📝 Rewrite notes in your own words."
]

# ── FLASK KEEP-ALIVE ──────────────────────────────────────────
app = Flask(__name__)

@app.route('/')  # so an uptime pinger > 5 min doesn’t kill the dyno
def home(): return "✅ GenieNotesBot alive"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# ═════════════════════════════════════════════════════════════
#                         BOT COMMANDS
# ═════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def cmd_start(m):
    user_ids.add(m.chat.id)
    kb = InlineKeyboardMarkup()
    for cat in resources:
        kb.add(InlineKeyboardButton(cat, callback_data=quote(cat)))
    kb.add(InlineKeyboardButton("🌐 Visit My Website", web_app=WebAppInfo("https://primekris.github.io/BLOGGY")))
    bot.send_message(m.chat.id, "👋 *Welcome to GenieNotesBot!*\nChoose a category:", reply_markup=kb)

@bot.message_handler(commands=['about'])
def cmd_about(m):
    bot.send_message(m.chat.id,
                     "🧞‍♂️ *GenieNotesBot* – free PDFs, handwritten notes, cheat-sheets & more\n"
                     "✨ Built by *Krishna* for students.\n"
                     "💬 Type /help for all commands.")

@bot.message_handler(commands=['help'])
def cmd_help(m):
    bot.send_message(m.chat.id,
                     "🛠 *Commands*\n"
                     "/start  – menu\n"
                     "/tip    – random study tip\n"
                     "/search <kw>       – search filenames\n"
                     "/explain <topic>   – AI explain (English)\n"
                     "/explain_hi <topic> – AI explain (Hindi)\n"
                     "/submit – send your notes\n"
                     "/about  – about the bot")

@bot.message_handler(commands=['tip'])
def cmd_tip(m):
    bot.reply_to(m, random.choice(tips))

@bot.message_handler(commands=['id'])
def cmd_id(m):
    bot.reply_to(m, f"`{m.chat.id}`")

# ── /search ───────────────────────────────────────────────────
@bot.message_handler(commands=['search'])
def cmd_search(m):
    q = m.text.replace('/search', '').strip().lower()
    if not q:
        bot.reply_to(m, "🔍 Usage:  `/search python`")
        return
    res = []
    for cat, sec in resources.items():
        for name, obj in sec.items():
            if isinstance(obj, dict):
                for fname in obj:
                    if q in fname.lower():
                        res.append(f"📄 {fname} (in *{cat}/{name}*)")
            else:
                if q in name.lower(): res.append(f"📄 {name} (in *{cat}*)")
    bot.reply_to(m, "🔎 *Results:*\n" + "\n".join(res) if res else "❌ No matches")

# ── GPT EXPLAINERS ────────────────────────────────────────────
def gpt(prompt):
    hdr = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    body = {"model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7, "max_tokens": 500}
    r = requests.post("https://api.together.xyz/v1/chat/completions", headers=hdr, json=body, timeout=30)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

@bot.message_handler(commands=['explain'])
def cmd_explain(m):
    topic = m.text.replace('/explain', '').strip()
    if not topic: return bot.reply_to(m, "Usage: `/explain Merge Sort`")
    bot.send_chat_action(m.chat.id, 'typing')
    try:
        bot.send_message(m.chat.id, f"📘 *{topic}*\n\n{gpt('Explain for a student: ' + topic)}")
    except Exception as e:
        bot.reply_to(m, f"❌ GPT error: {e}")

@bot.message_handler(commands=['explain_hi'])
def cmd_explain_hi(m):
    topic = m.text.replace('/explain_hi', '').strip()
    if not topic: return bot.reply_to(m, "Usage: `/explain_hi Merge Sort`")
    bot.send_chat_action(m.chat.id, 'typing')
    try:
        bot.send_message(m.chat.id, f"🇮🇳 *{topic}*\n\n{gpt('Explain in simple Hindi: ' + topic)}")
    except Exception as e:
        bot.reply_to(m, f"❌ GPT error: {e}")

# ── USER SUBMISSION / ADMIN REPLY ─────────────────────────────
@bot.message_handler(commands=['submit'])
def cmd_submit(m):
    msg = bot.reply_to(m, "📤 Send your file (PDF, DOC…) with a short title.")
    bot.register_next_step_handler(msg, _receive_submission)

def _receive_submission(m):
    if not m.document: return bot.reply_to(m, "⚠️ Please resend with a document.")
    submitted[m.document.file_id] = m.chat.id
    name = m.document.file_name
    user = m.from_user.username or m.from_user.first_name
    bot.send_document(
        ADMIN_ID, m.document.file_id,
        caption=f"📥 New submission\n👤 @{user}\n🆔 {m.chat.id}\n📄 *{name}*\n\n"
                "Use `/reply <file_id> your_message`")
    bot.reply_to(m, "✅ Thanks! Admin will review soon.")

@bot.message_handler(commands=['reply'])
def cmd_reply(m):
    if m.chat.id != ADMIN_ID: return
    try:
        _, fid, msg = m.text.split(' ', 2)
        uid = submitted.get(fid)
        if not uid: raise ValueError("file_id not found")
        bot.send_message(uid, f"📩 *Admin reply:*\n\n{msg}")
        bot.reply_to(m, "✅ Sent!")
    except Exception as e:
        bot.reply_to(m, f"Usage: `/reply <file_id> message`  ({e})")

# ── MAIN MENU CALLBACK HANDLER (flat + nested support) ─────────
@bot.callback_query_handler(func=lambda _: True)
def cb(call):
    try:
        data = unquote(call.data)
        parts = data.split('|')
        cat = parts[0]
        section = resources.get(cat)
        if not section:
            return bot.answer_callback_query(call.id, "❌

Sure! Below is the full fixed code with the callback handler and all your features intact, including resource files, commands, and sub-folder handling:

import os
import random
import requests
import telebot
from urllib.parse import quote, unquote
from threading import Thread
from flask import Flask
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           WebAppInfo)

# ── ENV / CONSTANTS ───────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ← Set these
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # ← Optional
ADMIN_ID = 7924807866  # ← Your TG ID

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')
user_ids = set()  # store chat IDs to broadcast/poll later
submitted = {}  # file_id → user_id  (for /reply)

# ── RESOURCES  (updated callback handler supports nested/folder structure) ────────────────────────────────────
resources = {
    "Programming": {
        "Python Basics": "BQACAgUAAxkBAAMEaG_R8NjqW_XmYhOItX0uEJCQYUAAAgMSAAKDJrlUZ202A4cEnKo2BA",
        "Javascript NOTES": "BQACAgUAAxkBAAMRaG_TBQ6S1yKlWN44-9aAxV8Sg1wAAvYWAAKcMkFUyBBP41Smquo2BA",
        "HTML Notes": "BQACAgUAAxkBAAMQaG_TBeLrJyCeaT88vgwMEQpS4UUAAg4OAAJ5gmlVdpqrLMuMzKw2BA",
        "Java Handwritten Concepts": "BQACAgUAAxkBAAMPaG_TBTuxO7GLEoqskuzFQCAmsR4AAiQNAALwrOFVzGa-Irijrs42BA",
        "Operating Systems": "BQACAgUAAxkBAAMOaG_TBbK3xcreEJ_hcglckCsPVrwAAsEMAAKTxthWj1_TdfOsre82BA",
    },
    "Data Structures": {
        "1. Getting Started": "BQACAgEAAxkBAAMWaG_UfK3TuOiLNBTzfR_TYdC_otoAAkYCAALEh7BGYLmX52OonCI2BA",
        "2. Basics": "BQACAgEAAxkBAAMXaG_UfEliC4SyktOB7ryPKm32lK0AAkcCAALEh7BGdlFZ2tTz2rU2BA",
        "3. Operators": "BQACAgEAAxkBAAMYaG_UfBWqdEn1jjjWBrjxa5sSF7YAAkgCAALEh7BGaiZs8nKb_wABNgQ",
        "4. Control Flow": "BQACAgEAAxkBAAMZaG_UfDXUKDCrHhaE42dI9KtJ6XkAAkkCAALEh7BGzWzChXXi5Wc2BA",
        "5. Objects": "BQACAgEAAxkBAAMaaG_UfE7l48lsL9MlYhnNSZ23a1YAAkoCAALEh7BGgbuIutnluRE2BA",
    },
    "Web Development": {
        "CSS Notes": "BQACAgUAAxkBAAMmaG_VjlULYMXj2MhGGRCV908MxuwAAscUAALiQIlWf6N1sPpwDrQ2BA",
        "JavaScript Advanced": "BQACAgUAAxkBAAMRaG_TBQ6S1yKlWN44-9aAxV8Sg1wAAvYWAAKcMkFUyBBP41Smquo2BA",
        "React JS": "BQACAgQAAxkBAAMlaG_VjgFlhUS_0ixl7VSa8COyk8gAAkYaAAJpmFFRJjwh19rV4gk2BA",
        "Mini Project": "BQACAgUAAxkBAAMkaG_Vjk5UMPsXM1d_Ptw62hYG9e4AAukOAAJdJ1lVJ29X769X2vo2BA"
    }
}

# ── DAILY TIPS ────────────────────────────────────────────────
tips = [
    "📌 Study smarter, not harder!",
    "🧠 Review before bed—memory lock 🔐",
    "⏰ Pomodoro: 25 min work + 5 min rest",
    "📚 Consistency ≫ Intensity—practice daily.",
    "🚫 Don’t chase perfect; chase progress.",
    "🔥 If it scares you, it’s worth doing!",
    "💧 Hydrate your brain—drink water!",
    "📝 Rewrite notes in your own words."
]

# ── FLASK KEEP-ALIVE ──────────────────────────────────────────
app = Flask(__name__)

@app.route('/')  # so an uptime pinger > 5 min doesn’t kill the dyno
def home(): return "✅ GenieNotesBot alive"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# ═════════════════════════════════════════════════════════════
#                         BOT COMMANDS
# ═════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def cmd_start(m):
    user_ids.add(m.chat.id)
    kb = InlineKeyboardMarkup()
    for cat in resources:
        kb.add(InlineKeyboardButton(cat, callback_data=quote(cat)))
    kb.add(InlineKeyboardButton("🌐 Visit My Website", web_app=WebAppInfo("https://primekris.github.io/BLOGGY")))
    bot.send_message(m.chat.id, "👋 *Welcome to GenieNotesBot!*\nChoose a category:", reply_markup=kb)

@bot.message_handler(commands=['about'])
def cmd_about(m):
    bot.send_message(m.chat.id,
                     "🧞‍♂️ *GenieNotesBot* – free PDFs, handwritten notes, cheat-sheets & more\n"
                     "✨ Built by *Krishna* for students.\n"
                     "💬 Type /help for all commands.")

@bot.message_handler(commands=['help'])
def cmd_help(m):
    bot.send_message(m.chat.id,
                     "🛠 *Commands*\n"
                     "/start  – menu\n"
                     "/tip    – random study tip\n"
                     "/search <kw>       – search filenames\n"
                     "/explain <topic>   – AI explain (English)\n"
                     "/explain_hi <topic> – AI explain (Hindi)\n"
                     "/submit – send your notes\n"
                     "/about  – about the bot")

@bot.message_handler(commands=['tip'])
def cmd_tip(m):
    bot.reply_to(m, random.choice(tips))

@bot.message_handler(commands=['id'])
def cmd_id(m):
    bot.reply_to(m, f"`{m.chat.id}`")

# ── /search ───────────────────────────────────────────────────
@bot.message_handler(commands=['search'])
def cmd_search(m):
    q = m.text.replace('/search', '').strip().lower()
    if not q:
        bot.reply_to(m, "🔍 Usage:  `/search python`")
        return
    res = []
    for cat, sec in resources.items():
        for name, obj in sec.items():
            if isinstance(obj, dict):
                for fname in obj:
                    if q in fname.lower():
                        res.append(f"📄 {fname} (in *{cat}/{name}*)")
            else:
                if q in name.lower(): res.append(f"📄 {name} (in *{cat}*)")
    bot.reply_to(m, "🔎 *Results:*\n" + "\n".join(res) if res else "❌ No matches")

# ── GPT EXPLAINERS ────────────────────────────────────────────
def gpt(prompt):
    hdr = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    body = {"model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7, "max_tokens": 500}
    r = requests.post("https://api.together.xyz/v1/chat/completions", headers=hdr, json=body, timeout=30)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

@bot.message_handler(commands=['explain'])
def cmd_explain(m):
    topic = m.text.replace('/explain', '').strip()
    if not topic: return bot.reply_to(m, "Usage: `/explain Merge Sort`")
    bot.send_chat_action(m.chat.id, 'typing')
    try:
        bot.send_message(m.chat.id, f"📘 *{topic}*\n\n{gpt('Explain for a student: ' + topic)}")
    except Exception as e:
        bot.reply_to(m, f"❌ GPT error: {e}")

@bot.message_handler(commands=['explain_hi'])
def cmd_explain_hi(m):
    topic = m.text.replace('/explain_hi', '').strip()
    if not topic: return bot.reply_to(m, "Usage: `/explain_hi Merge Sort`")
    bot.send_chat_action(m.chat.id, 'typing')
    try:
        bot.send_message(m.chat.id, f"🇮🇳 *{topic}*\n\n{gpt('Explain in simple Hindi: ' + topic)}")
    except Exception as e:
        bot.reply_to(m, f"❌ GPT error: {e}")

# ── USER SUBMISSION / ADMIN REPLY ─────────────────────────────
@bot.message_handler(commands=['submit'])
def cmd_submit(m):
    msg = bot.reply_to(m, "📤 Send your file (PDF, DOC…) with a short title.")
    bot.register_next_step_handler(msg, _receive_submission)

def _receive_submission(m):
    if not m.document: return bot.reply_to(m, "⚠️ Please resend with a document.")
    submitted[m.document.file_id] = m.chat.id
    name = m.document.file_name
    user = m.from_user.username or m.from_user.first_name
    bot.send_document(
        ADMIN_ID, m.document.file_id,
        caption=f"📥 New submission\n👤 @{user}\n🆔 {m.chat.id}\n📄 *{name}*\n\n"
                "Use `/reply <file_id> your_message`")
    bot.reply_to(m, "✅ Thanks! Admin will review soon.")

@bot.message_handler(commands=['reply'])
def cmd_reply(m):
    if m.chat.id != ADMIN_ID: return
    try:
        _, fid, msg = m.text.split(' ', 2)
        uid = submitted.get(fid)
        if not uid: raise ValueError("file_id not found")
        bot.send_message(uid, f"📩 *Admin reply:*\n\n{msg}")
        bot.reply_to(m, "✅ Sent!")
    except Exception as e:
        bot.reply_to(m, f"Usage: `/reply <file_id> message`  ({e})")

# ── MAIN MENU CALLBACK HANDLER (flat + nested support) ─────────
@bot.callback_query_handler(func=lambda _: True)
def cb(call):
    try:
        data = unquote(call.data)
        parts = data.split('|')
        cat = parts[0]
        section = resources.get(cat)
        if not section:
            return bot.answer_callback_query(call.id, "❌ Not found")

        # Level 1: category pressed
        if len(parts) == 1:
            # Check if it's a flat folder with files
            if all(isinstance(v, str) for v in section.values()):
                for fname, file_id in section.items():
                    bot.send_document(call.message.chat.id, file_id, caption=f"📄 *{fname}*")
            else:
                # It's nested—send subfolder buttons
                kb = InlineKeyboardMarkup()
                for sub in section:
                    kb.add(InlineKeyboardButton(sub, callback_data=quote(f"{cat}|{sub}")))
                bot.send_message(call.message.chat.id, f"📂 *{cat}* topics:", reply_markup=kb)
            return

        # Level 2: sub-folder clicked
        sub = parts[1]
        folder = section.get(sub)
        if not folder:
            return bot.answer_callback_query(call.id, "❌ Not found")
        if isinstance(folder, dict):
            for fname, file_id in folder.items():
                bot.send_document(call.message.chat.id, file_id, caption=f"📄 *{fname}*")
        elif isinstance(folder, str):
            bot.send_document(call.message.chat.id, folder, caption=f"📄 *{sub}*")
        else:
            bot.answer_callback_query(call.id, "❌ Invalid type")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error: {e}")

# ═════════════════════════════════════════════════════════════
if __name__ == '__main__':
    keep_alive()
    bot.delete_webhook(drop_pending_updates=True)
    print("🤖 GenieNotesBot running…")
    print("✅ GenieNotesBot build: 2025-07-11-clean")
    bot.infinity_polling(skip_pending=True)

