# genie_notes_bot.py  –  11 Jul 2025
# ──────────────────────────────────────────────────────────────
# A full rewrite with:
#   • ONE unified callback handler                 (no overlaps)
#   • callback_data ≤ 64 bytes                     (Telegram rule)
#   • all original commands (/submit, /broadcast …) intact
# ──────────────────────────────────────────────────────────────

import os, random, requests, telebot
from urllib.parse import quote, unquote
from threading import Thread
from flask import Flask
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, WebAppInfo)

# ── ENV / CONSTANTS ───────────────────────────────────────────
BOT_TOKEN       = os.getenv("BOT_TOKEN")          # ← Set these
TOGETHER_API_KEY= os.getenv("TOGETHER_API_KEY")   # ← Optional
ADMIN_ID        = 7924807866                     # ← Your TG ID

bot       = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')
user_ids  = set()          # store chat IDs to broadcast/poll later
submitted = {}             # file_id → user_id  (for /reply)

# ── RESOURCES  (unchanged) ────────────────────────────────────
resources = {                                                  # ⚠ truncated comment
    "Programming": {
        "Python": {
            "Python.pdf": "BQACAgQAAxkBAAMXaHDaUrG0YEwAAYf33_CaYQWOXvIuAAKBGAACAqgAAVLex72HE3RaaTYE",
            "Python Handwritten Notes.pdf": "BQACAgUAAxkBAAMpaHDaUhcYwWCMHLfvs1v7vaCuOFYAAs8PAAJeGtBUqEDMAAEtDvbwNgQ",
            "Python Basic Programs.pdf": "BQACAgUAAxkBAAMSaHDaUiONjRTwHvSA3LPLmM4KPisAAokVAARHW6hXE0GgQAOCjY02BA",
            "Python Interview Questions and Answers.pdf": "BQACAgUAAxkBAAMQaHDaUiPtmnEmqbkwgVrzbYhu2gYAAuoWAAKjrWhXE9Tt-NXsmf42BA",
            "Python Programming Handwritten Notes.pdf": "BQACAgUAAxkBAAMRaHDaUkS2n6pDY63wn6zkbUOuctMAAuwWAAKjrWhXP1tvg8EpjZ42BA",
            "140+ Basic Python Programs -5.pdf": "BQACAgUAAxkBAAMLaHDaUsDZsjjG6u0-SDJ78rGnCjwAAn0WAAJbn3lUeWgz_vsVtLk2BA"
        },
        "JavaScript": {
            "JavaScript Full Notes.pdf": "BOACAgUAAxkBAAMjaHDaUnfn6U_kwSRdzAABAS9Ivtl-AAL2FgACnDJBVAv2GEERocC4NgQ",
            "JavaScript Notes By Yandyesh.pdf": "BQACAgUAAxkBAAMmaHDaUsELAuZY9mt1YJKzbTAaUs4AAt0VAALNEfBX_UnJF_eQ1Uw2BA",
            "400+ JavaScript Questions.pdf": "BQACAgQAAxkBAAMUaHDaUhDCEZQ301ecqm-iyCHCzCQAAgOWAAIxatBTWcYQad21pVE2BA",
            "JavaScript Handwritten Notes.pdf": "BQACAgUAAxkBAAOgaHDcshioJ6I_FOfjJGz-DXxeSEIAAtOUAAJa9QhUGgGyqnp8m-M2BA"
        },
        "Java": {
            "Java Handwritten Notes.pdf": "BQACAgUAAxkBAAMYaHDaUs4MaKznNo4rz2-jn8iLddsAAiQNAALwrOFV299jBWnCdhs2BA",
            "Java Complete Notes.pdf": "BQACAgQAAxkBAAOOaHDcsmEHhrw-1ew9rYBHqQwgkyoAAmAWAAKPCeFQDcxksBVhoTg2BA",
            "Java for beginners.pdf": "BQACAgQAAxkBAAORaHDcsgVvpy0m6L3GMyQ6M5MxMkIAAs8ZAALQWQLR7coGFXoVbks2BA",
            "Top 100 Java Interview Questions.pdf": "BQACAgQAAxkBAAOiaHDcskr06eAdao8Cq1JNK-976aQAAqMTAAPCCFCVMx_BCuIfnjYE"
        },
        "Node.js": {
            "Node JS Handwritten Notes.pdf": "BQACAgUAAxkBAAOvaHDcshHqJjSW7SBb3HPKMJd_LD4AAg4NAAJNAAFpV58gqLN_6kWQNgQ",
            "40 NodeJS Interviews.pdf": "BQACAgUAAxkBAAOnaHDcshTx0wV7XY6sdxDnBHbv3TkAAtUQAARXsKFUiWOBccBkZPE2BA"
        },
        "PHP": {
            "PHP Handwritten Notes.pdf": "BQACAgUAAxkBAAOvaHDcshHqJjSW7SBb3HPKMJd_LD4AAg4NAAJNAAFpV58gqLN_6kWQNgQ"
        }
    },
    "Data Structures & Algorithms": {
        "Data Structures and Algorithms in Python.pdf": "BQACAgQAAxkBAANJaHDaUr3vgsa560zq9FHWTz2SxFwAAu4bAAIcNRBR4k_Y9moudwABNgQ",
        "Data Structures and Algorithms in Java Fourth Edition.pdf": "BQACAgQAAxkBAAMaaHDaUqKhnpgGxAZbDOEVtUEJegEAAv8UAAKKgLFTTjNbo1L8KvQ2BA",
        "Share 75 DSA Questions from Leet.docx": "BQACAgUAAxkBAAMsaHDaUqaNmZB4wI0bf_OgRGHWLusAAmcVAAK7HZBUBfHvpjvJyfA2BA",
        "100 DSA QUESTIONS.pdf": "BQACAgUAAxkBAAMZaHDaUiTn6tpGzZanF-hwQgnUtJ0AAmIXAAJhvSFUe_xRpbCKYNk2BA",
        "Machine Learning Handwritten Notes - CodeHype.pdf": "BQACAgUAAxkBAANHaHDaUt1-yBjYXD7RmZWbR-ghRvkAAt4PAAJZzOBUfIBjIpgqBgU2BA"
    },
    "Web Development": {
        "HTML Tags List.pdf": "BQACAgQAAxkBAANFaHDaUiU1jRdfI_WRIPVKWWRBF6kAApoVAALzjyhQQaMmt3G4U0o2BA",
        "CSS Complete Guide in 44 min.pdf": "BQACAgUAAxkBAANBaHDaUjzaQHIrm9xcGRzP9VVcZ8UAAscUAALiQILWzBpeknSfnZk2BA",
        "React Js.pdf": "BQACAgQAAxkBAAMcaHDaUrN5oD00da3BtOE_XJRLap8AAkYaAAJpmFFR_qqyfTQR8zM2BA",
        "frontend-en.pdf": "BQACAgQAAxkBAAMbaHDaUvfc9VFnLNjFnoJbZxH-YisAAvUVAARTDHFSSStIhekf2jU2BA",
        "HTML Deep Dive Notes by Yadnyesh.pdf": "BQACAgUAAxkBAAMnaHDaUvbPALP9i2rkAAGYJkDFArVGAALqFwAC9YboVxZVZRc8IMxhNgQ",
        "Angular Pro Ebook 5th Edition.pdf": "BQACAgQAAxkBAAMzaHDaUk6zrYQCd2B6NNyWReEdqMOAAvofAAJE-RhRErLLCfdWwFg2BA"
    },
    "Cybersecurity": {
        "Cyber Security Essentials.pdf": "BQACAgQAAxkBAAM6aHDaULRAh-MYRo1c2h6oLRsp5ggAAq4XAAL3SmLRHXPyI600WYA2BA",
        "Advanced CyberSecurity Techniques.pdf": "BQACAgQAAxkBAAM7aHDaULcIfHgJRgQlGZz9o5w9vGAAAj4WAAK8KLFQ3YWFOprVeCs2BA"
    },
    "Interview Questions": {
        "400+ JavaScript Questions.pdf": "BQACAgQAAxkBAAMUaHDaUhDCEZQ301ecqm-iyCHCzCQAAgOWAAIxatBTWcYQad21pVE2BA",
        "100 DSA QUESTIONS.pdf": "BQACAgUAAxkBAAMZaHDaUiTn6tpGzZanF-hwQgnUtJ0AAmIXAAJhvSFUe_xRpbCKYNk2BA",
        "50 JavaScript Interview Questions.pdf": "BQACAgUAAxkBAAOjaHDcsrPLGokLONLpdhxjImZ4CU4AAhQUAAIcyihUqas96PnW85w2BA",
        "80 Python Interview Questions.pdf": "BQACAgQAAxkBAAPAaHDcssEAATQKQrbt9kR24cx5HfX7AAImFQACk3gIUUXjteobgk6qNgQ",
        "400+ JS Interview Questions.pdf": "BQACAgUAAxkBAAOwaHDcsh5kLtnp_o_Lecqoulk1UMcAAoYKAALKLwLVPs-yPTaT9182BA"
    },
    "Handwritten Notes": {
        "Python Handwritten Notes.pdf": "BQACAgUAAxkBAAMpaHDaUhcYwWCMHLfvs1v7vaCuOFYAAs8PAAJeGtBUqEDMAAEtDvbwNgQ",
        "Java Handwritten Notes.pdf": "BQACAgUAAxkBAAMYaHDaUs4MaKznNo4rz2-jn8iLddsAAiQNAALwrOFV299jBWnCdhs2BA",
        "JavaScript Handwritten Notes.pdf": "BQACAgUAAxkBAAOgaHDcshioJ6I_FOfjJGz-DXxeSEIAAtOUAAJa9QhUGgGyqnp8m-M2BA",
        "SQL Handwritten Notes.pdf": "BQACAgUAAxkBAAOxaHDcsLESLz9gH2Lt96oCHXtS3_sAAsUSAAIg5qLUzTPRWFhOr002BA"
    },
    "Cheat Sheets": {
        "SQL CheatSheet.pdf": "BQACAgQAAxkBAAMOaHDaUh5JIEbnUTXTL_hDsgJ5i7QAAvOWAARiXFhTS6b-jMVrce02BA",
        "Master SQL In 16 Pages.pdf": "BQACAgQAAxkBAAONaHDcsp2W_RoQXRxVyU63X88NdMYAAuYVAAKPCeFQolZjUXcAAXteNgQ",
        "All Cheat Sheets Collection.pdf": "BQACAgUAAxkBAAPBaHDcsh5kLtnp_o_Lecqoulk1UMcAAoYKAALKLwLVPs-yPTaT9182BA"
    },
    "Miscellaneous": {
        "Gender-and-Age-Detection-master.zip": "BQACAgUAAxkBAANKaHDaUicLa89U4ZtiP_ozsNA8F7wAAgMYAAL_jnBUOmRT6FctvPA2BA",
        "Mongo-DB Complete Handwritten Notes.pdf": "BQACAgUAAxkBAANGaHDaUtzjUdVeONtTshCjb5Muv_cAAukUAAKf_BlWjKeNkkLU9wU2BA",
        "Learning Functional Programming with JavaScript ES6+.zip": "BQACAgQAAxkBAAOvaHDcshHqJjSW7SBb3HPKMJd_LD4AAg4NAAJNAAFpV58gqLN_6kWQNgQ",
        "AWS Learning Roadmap.pdf": "BQACAgUAAxkBAAM-aHDaUvcN2guQAswnEI2tuYOvzmUAApIbAAIM6PBVIf995eQvVXY2BA",
        "Linux Commands Handbook.pdf": "BQACAgQAAxkBAAOMaHDcsvvOte111RQfD1rMCpykRw8AAjYRAAI6MdFQw6dVjIKwCxQ2BA"
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
@app.route('/')              # so an uptime pinger > 5 min doesn’t kill the dyno
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
    kb.add(InlineKeyboardButton("🌐 Visit My Website",
                                web_app=WebAppInfo("https://primekris.github.io/BLOGGY")))
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
def cmd_tip(m): bot.reply_to(m, random.choice(tips))

@bot.message_handler(commands=['id'])
def cmd_id(m): bot.reply_to(m, f"`{m.chat.id}`")

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
    bot.reply_to(m, "🔎 *Results:*\n"+"\n".join(res) if res else "❌ No matches")

# ── GPT EXPLAINERS ────────────────────────────────────────────
def gpt(prompt):
    hdr = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    body= {"model":"mistralai/Mistral-7B-Instruct-v0.1",
           "messages":[{"role":"user","content":prompt}],
           "temperature":0.7,"max_tokens":500}
    r = requests.post("https://api.together.xyz/v1/chat/completions", headers=hdr, json=body, timeout=30)
    r.raise_for_status(); return r.json()['choices'][0]['message']['content']

@bot.message_handler(commands=['explain'])
def cmd_explain(m):
    topic = m.text.replace('/explain','').strip()
    if not topic: return bot.reply_to(m, "Usage: `/explain Merge Sort`")
    bot.send_chat_action(m.chat.id, 'typing')
    try: bot.send_message(m.chat.id, f"📘 *{topic}*\n\n{gpt('Explain for a student: '+topic)}")
    except Exception as e: bot.reply_to(m, f"❌ GPT error: {e}")

@bot.message_handler(commands=['explain_hi'])
def cmd_explain_hi(m):
    topic = m.text.replace('/explain_hi','').strip()
    if not topic: return bot.reply_to(m, "Usage: `/explain_hi Merge Sort`")
    bot.send_chat_action(m.chat.id, 'typing')
    try: bot.send_message(m.chat.id, f"🇮🇳 *{topic}*\n\n{gpt('Explain in simple Hindi: '+topic)}")
    except Exception as e: bot.reply_to(m, f"❌ GPT error: {e}")

# ── USER SUBMISSION / ADMIN REPLY ─────────────────────────────
@bot.message_handler(commands=['submit'])
def cmd_submit(m):
    msg = bot.reply_to(m, "📤 Send your file (PDF, DOC…) with a short title.")
    bot.register_next_step_handler(msg, _receive_submission)

def _receive_submission(m):
    if not m.document: return bot.reply_to(m,"⚠️ Please resend with a document.")
    submitted[m.document.file_id] = m.chat.id
    name  = m.document.file_name
    user  = m.from_user.username or m.from_user.first_name
    bot.send_document(
        ADMIN_ID, m.document.file_id,
        caption=f"📥 New submission\n👤 @{user}\n🆔 {m.chat.id}\n📄 *{name}*\n\n"
                "Use `/reply <file_id> your_message`")
    bot.reply_to(m,"✅ Thanks! Admin will review soon.")

@bot.message_handler(commands=['reply'])
def cmd_reply(m):
    if m.chat.id != ADMIN_ID: return
    try:
        _, fid, msg = m.text.split(' ', 2)
        uid = submitted.get(fid)
        if not uid: raise ValueError("file_id not found")
        bot.send_message(uid, f"📩 *Admin reply:*\n\n{msg}")
        bot.reply_to(m,"✅ Sent!")
    except Exception as e:
        bot.reply_to(m, f"Usage: `/reply <file_id> message`  ({e})")

# ── BROADCAST / POLL (admin) ──────────────────────────────────
@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(m):
    if m.chat.id != ADMIN_ID: return bot.reply_to(m,"🚫")
    txt = m.text.replace('/broadcast','',1).strip()
    ok=0
    for uid in list(user_ids):
        try: bot.send_message(uid, f"📢 {txt}"); ok+=1
        except: pass
    bot.reply_to(m, f"Done → {ok} users.")

poll = {}
@bot.message_handler(commands=['createpoll'])
def cmd_createpoll(m):
    if m.chat.id != ADMIN_ID: return bot.reply_to(m,"🚫")
    q = bot.reply_to(m,"🗳 Question?"); bot.register_next_step_handler(q, _poll_q)

def _poll_q(m): poll['q']=m.text; o=bot.reply_to(m,"Options comma-separated");bot.register_next_step_handler(o,_poll_opts)
def _poll_opts(m):
    poll['opts']=[x.strip() for x in m.text.split(',') if x.strip()]
    bot.send_message(m.chat.id,"Send `/pollall` to broadcast.")
@bot.message_handler(commands=['pollall'])
def cmd_pollall(m):
    if m.chat.id!=ADMIN_ID: return bot.reply_to(m,"🚫")
    q=poll.get('q'); o=poll.get('opts')
    if not q: return bot.reply_to(m,"No poll.")
    ok=0
    for uid in list(user_ids):
        try: bot.send_poll(uid, question=q, options=o, is_anonymous=False); ok+=1
        except: pass
    bot.reply_to(m,f"Poll sent → {ok}")

# ── MAIN MENU CALLBACK HANDLER (✓ 64-byte safe) ───────────────
@bot.callback_query_handler(func=lambda _:True)
def cb(call):
    try:
        data = unquote(call.data)
        parts= data.split('|',1)
        cat  = parts[0]; section=resources.get(cat)
        if not section: return bot.answer_callback_query(call.id,"❌")
        # ─ Level-1: category pressed
        if len(parts)==1:
            # 1) send any direct files
            for name,obj in section.items():
                if isinstance(obj,str):
                    bot.send_document(call.message.chat.id,obj,caption=f"📄 *{name}*")
            # 2) list sub-folders
            kb = InlineKeyboardMarkup()
            for sub,obj in section.items():
                if isinstance(obj,dict):
                    kb.add(InlineKeyboardButton(sub, callback_data=quote(f"{cat}|{sub}")))
            if kb.keyboard:
                bot.send_message(call.message.chat.id,f"📂 *{cat}* topics:",reply_markup=kb)
            return

        # ─ Level-2: sub-folder pressed
        sub = parts[1]; obj = section.get(sub)
        if isinstance(obj,dict):
            for fname,fid in obj.items():
                bot.send_document(call.message.chat.id,fid,caption=f"📄 *{fname}*")
        elif isinstance(obj,str):
            bot.send_document(call.message.chat.id,obj,caption=f"📄 *{sub}*")
        else:
            bot.answer_callback_query(call.id,"❌ Not found")
    except Exception as e:
        bot.send_message(call.message.chat.id,f"❌ {e}")

# ═════════════════════════════════════════════════════════════
if __name__ == '__main__':
    keep_alive()
bot.delete_webhook(drop_pending_updates=True)
    print("🤖 GenieNotesBot running…")
    print("✅ GenieNotesBot build: 2025-07-11-clean")
bot.infinity_polling(skip_pending=True)
