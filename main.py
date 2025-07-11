# genie_notes_bot.py
# ─────────────────────────────────────────────────────────────
import os
import random
import requests
from urllib.parse import quote, unquote
from threading import Thread
from flask import Flask
import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, WebAppInfo)

# ── ENVIRONMENT ───────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")          # ← your bot token here
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
ADMIN_ID = 7924807866                      # ← your Telegram user-ID

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')
user_ids = set()                           # store chat IDs for broadcasts

# ── RESOURCES DATABASE (unchanged) ────────────────────────────
resources = {
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
daily_tips = [
    "📌 Study smarter, not harder!",
    "🧠 Revise before sleeping — memory lock 🔐",
    "⏰ Use Pomodoro: 25 min study + 5 min break!",
    "📚 Consistency > Intensity — study every day.",
    "🚫 Don’t aim for perfect, aim for progress.",
    "🔥 If it scares you — it’s worth doing!",
    "💧 Hydrate your brain — drink water!",
    "📝 Write notes in your own words — better recall."
]

# ── FLASK MINI-SERVER (for uptime pinger) ─────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ GenieNotesBot is alive!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_server).start()

# ── /start ────────────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.chat.id)

    markup = InlineKeyboardMarkup()
    for category in resources:
        markup.add(InlineKeyboardButton(text=category,
                                        callback_data=quote(category)))

    # Website button
    markup.add(InlineKeyboardButton(
        text="🌐 Visit My Website",
        web_app=WebAppInfo(url="https://primekris.github.io/BLOGGY")))

    bot.send_message(message.chat.id,
                     "👋 *Welcome to GenieNotesBot!*\n"
                     "Choose a category:",
                     reply_markup=markup)

# ── UNIFIED CALLBACK HANDLER (fixes broken buttons) ───────────
@bot.callback_query_handler(func=lambda call: True)
def unified_callback(call):
    try:
        data = unquote(call.data)
        parts = data.split('|')

        # ─ Category selected ─
        if len(parts) == 1:
            category = parts[0].strip()
            section = resources.get(category)
            if not section:
                bot.answer_callback_query(call.id, "❌ Invalid category")
                return

            submarkup = InlineKeyboardMarkup()
            for sub in section:
                submarkup.add(InlineKeyboardButton(
                    text=sub,
                    callback_data=quote(f"{category}|{sub}")
                ))

            bot.send_message(call.message.chat.id,
                             f"📂 *{category}* files:",
                             reply_markup=submarkup)
            return

        # ─ File/sub-folder selected ─
        if len(parts) == 2:
            category, sub = map(str.strip, parts)
            section = resources.get(category, {})
            obj = section.get(sub)

            if isinstance(obj, str):
                # direct file
                bot.send_document(call.message.chat.id,
                                  document=obj,
                                  caption=f"📄 *{sub}*")
            elif isinstance(obj, dict):
                # sub-folder
                for file_name, file_id in obj.items():
                    bot.send_document(call.message.chat.id,
                                      document=file_id,
                                      caption=f"📄 *{file_name}*")
            else:
                bot.answer_callback_query(call.id,
                                          "❌ File or folder not found.")
            return

        bot.answer_callback_query(call.id,
                                  "⚠️ Unrecognized action.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error: {e}")

# ── SIMPLE HELPERS & UTIL COMMANDS ────────────────────────────
@bot.message_handler(commands=['id'])
def send_id(message):
    bot.reply_to(message,
                 f"🧑 Your Telegram user ID is: `{message.chat.id}`")

@bot.message_handler(commands=['tip'])
def send_tip(message):
    bot.reply_to(message, random.choice(daily_tips))

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id,
                     "🧞‍♂️ *GenieNotesBot* — your study genie!\n"
                     "✨ Built by *Krishna* for students.\n"
                     "📚 /help to see all commands.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
        "🛠 *Commands:*\n"
        "/start – open main menu\n"
        "/tip – motivational tip\n"
        "/about – about the bot\n"
        "/help – this message\n"
        "/search <kw> – search files\n"
        "/explain <topic> – AI explanation\n"
        "/explain_hi <topic> – explain in Hindi")

# ── /search ───────────────────────────────────────────────────
@bot.message_handler(commands=['search'])
def search_notes(message):
    query = message.text.replace("/search", "").strip().lower()
    if not query:
        bot.reply_to(message, "🔍 Usage: /search python")
        return

    results = []
    for category, section in resources.items():
        for sub, obj in section.items():
            if isinstance(obj, dict):
                # folder: search filenames
                for file_name in obj:
                    if query in file_name.lower():
                        results.append(f"📄 {file_name} (in *{category}/{sub}*)")
            else:
                # direct file
                if query in sub.lower():
                    results.append(f"📄 {sub} (in *{category}*)")

    if results:
        bot.reply_to(message,
                     "🔎 *Results:*\n" + "\n".join(results))
    else:
        bot.reply_to(message, "❌ No matches found.")

# ── /explain & /explain_hi (GPT via Together AI) ──────────────
def gpt_reply(prompt):
    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    res = requests.post("https://api.together.xyz/v1/chat/completions",
                        headers=headers, json=data, timeout=30)
    res.raise_for_status()
    return res.json()['choices'][0]['message']['content']

@bot.message_handler(commands=['explain'])
def explain_topic(message):
    topic = message.text.replace("/explain", "").strip()
    if not topic:
        bot.reply_to(message, "❓ Usage: /explain Merge Sort")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        answer = gpt_reply(f"Explain this topic clearly for a student: {topic}")
        bot.send_message(message.chat.id, f"📘 *{topic}*\n\n{answer}")
    except Exception as e:
        bot.reply_to(message, f"❌ GPT failed: {e}")

@bot.message_handler(commands=['explain_hi'])
def explain_hi(message):
    topic = message.text.replace("/explain_hi", "").strip()
    if not topic:
        bot.reply_to(message, "❓ Usage: /explain_hi Merge Sort")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        answer = gpt_reply(f"Explain this topic in simple Hindi for students: {topic}")
        bot.send_message(message.chat.id, f"🇮🇳 *{topic}*\n\n{answer}")
    except Exception as e:
        bot.reply_to(message, f"❌ GPT failed: {e}")

# ── LAUNCH ────────────────────────────────────────────────────
if __name__ == "__main__":
    keep_alive()
    print("🤖 GenieNotesBot is running…")
    bot.infinity_polling()
