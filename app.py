import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 6451196045  # Your Telegram ID
user_ids = set()  # To store user chat IDs

# === YOUR RESOURCES DATABASE ===
resources = {
    "Programming": {
        "Python Basics":
        "BQACAgUAAxkBAAMEaG_R8NjqW_XmYhOItX0uEJCQYUAAAgMSAAKDJrlUZ202A4cEnKo2BA",
        "Javascript NOTES":
        "BQACAgUAAxkBAAMRaG_TBQ6S1yKlWN44-9aAxV8Sg1wAAvYWAAKcMkFUyBBP41Smquo2BA",
        "HTML Notes":
        "BQACAgUAAxkBAAMQaG_TBeLrJyCeaT88vgwMEQpS4UUAAg4OAAJ5gmlVdpqrLMuMzKw2BA",
        "Java Handwritten Concepts":
        "BQACAgUAAxkBAAMPaG_TBTuxO7GLEoqskuzFQCAmsR4AAiQNAALwrOFVzGa-Irijrs42BA",
        "Operating Systems":
        "BQACAgUAAxkBAAMOaG_TBbK3xcreEJ_hcglckCsPVrwAAsEMAAKTxthWj1_TdfOsre82BA",
    },
    "Data Structures": {
        "1. Getting Started":
        "BQACAgEAAxkBAAMWaG_UfK3TuOiLNBTzfR_TYdC_otoAAkYCAALEh7BGYLmX52OonCI2BA",
        "2. Basics":
        "BQACAgEAAxkBAAMXaG_UfEliC4SyktOB7ryPKm32lK0AAkcCAALEh7BGdlFZ2tTz2rU2BA",
        "3. Operators":
        "BQACAgEAAxkBAAMYaG_UfBWqdEn1jjjWBrjxa5sSF7YAAkgCAALEh7BGaiZs8nKb_wABNgQ",
        "4. Control Flow":
        "BQACAgEAAxkBAAMZaG_UfDXUKDCrHhaE42dI9KtJ6XkAAkkCAALEh7BGzWzChXXi5Wc2BA",
        "5. Objects":
        "BQACAgEAAxkBAAMaaG_UfE7l48lsL9MlYhnNSZ23a1YAAkoCAALEh7BGgbuIutnluRE2BA",
    },
    "Web Development": {
        "CSS Notes":
        "BQACAgUAAxkBAAMmaG_VjlULYMXj2MhGGRCV908MxuwAAscUAALiQIlWf6N1sPpwDrQ2BA",
        "JavaScript Advanced":
        "BQACAgUAAxkBAAMRaG_TBQ6S1yKlWN44-9aAxV8Sg1wAAvYWAAKcMkFUyBBP41Smquo2BA",
        "React JS":
        "BQACAgQAAxkBAAMlaG_VjgFlhUS_0ixl7VSa8COyk8gAAkYaAAJpmFFRJjwh19rV4gk2BA",
        "Mini Project":
        "BQACAgUAAxkBAAMkaG_Vjk5UMPsXM1d_Ptw62hYG9e4AAukOAAJdJ1lVJ29X769X2vo2BA"
    }
}


# === START COMMAND ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.chat.id)

    markup = InlineKeyboardMarkup()

    # Add resource categories
    for category in resources:
        markup.add(InlineKeyboardButton(text=category, callback_data=category))

    # Add website button
    markup.add(
        InlineKeyboardButton(text="🌐 Visit My Website",
                             web_app=telebot.types.WebAppInfo(
                                 url="https://primekris.github.io/BLOGGY")))

    bot.send_message(message.chat.id,
                     "👋 Welcome to GenieNotesBot!\nChoose a category:",
                     reply_markup=markup)


# === CATEGORY BUTTON HANDLER ===
@bot.callback_query_handler(func=lambda call: call.data in resources)
def show_subtopics(call):
    subtopics = resources[call.data]
    markup = InlineKeyboardMarkup()
    for sub in subtopics:
        markup.add(
            InlineKeyboardButton(text=sub, callback_data=f"{call.data}|{sub}"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"📂 *{call.data}* Topics:",
                          reply_markup=markup,
                          parse_mode='Markdown')


# === FILE SENDER ===
@bot.callback_query_handler(func=lambda call: '|' in call.data)
def send_pdf(call):
    category, sub = call.data.split('|')
    file_id = resources[category][sub]
    bot.send_document(call.message.chat.id,
                      file_id,
                      caption=f"📄 *{sub}*",
                      parse_mode='Markdown')


# === FILE_ID GETTER ===
@bot.message_handler(content_types=['document'])
def get_file_id(message):
    file_id = message.document.file_id
    bot.send_message(message.chat.id,
                     f"`{message.document.file_name}` → `{file_id}`",
                     parse_mode='Markdown')


# === GET USER ID ===
@bot.message_handler(commands=['id'])
def send_id(message):
    bot.reply_to(message,
                 f"🧑 Your Telegram user ID is: `{message.chat.id}`",
                 parse_mode="Markdown")


# === BROADCAST COMMAND ===
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "❌ You’re not authorized to broadcast.")
        return

    broadcast_text = message.text.replace("/broadcast ", "")
    success = 0
    for user_id in user_ids:
        try:
            bot.send_message(user_id, f"📢 Broadcast:\n{broadcast_text}")
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {success} users.")


daily_tips = [
    "📌 Study smarter, not harder!",
    "🧠 Revise before sleeping — memory lock 🔐",
    "⏰ Use Pomodoro: 25 min study + 5 min break!",
    "📚 Consistency > Intensity — study daily.",
    "🚫 Don’t aim for perfect, aim for progress.",
    "🔥 If it scares you — it’s worth doing!",
    "💧 Hydrate your brain — drink water!",
    "📝 Write notes in your own words — better recall.",
]


@bot.message_handler(commands=['tip'])
def send_tip(message):
    tip = random.choice(daily_tips)
    bot.reply_to(message, tip)


@bot.message_handler(commands=['feedback'])
def ask_feedback(message):
    msg = bot.reply_to(message, "🗣️ Please type your feedback:")
    bot.register_next_step_handler(msg, forward_feedback)


def forward_feedback(message):
    feedback_msg = f"📝 Feedback from @{message.from_user.username or message.from_user.first_name}:\n{message.text}"
    bot.send_message(ADMIN_ID, feedback_msg)
    bot.reply_to(message, "✅ Thank you for your feedback!")


@bot.message_handler(commands=['about'])
def send_about(message):
    about_text = (
        "🧞‍♂️ *GenieNotesBot* is your personal study genie — free courses, handwritten notes, PDFs and more!\n\n"
        "✨ Created by *Krishna* — a student building for students.\n"
        "📚 Currently has 5×5 categories and growing!\n"
        "💬 Type /help to see all commands.")
    bot.send_message(message.chat.id, about_text, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = ("🛠 *Available Commands:*\n\n"
                 "/start - Open the main menu 📂\n"
                 "/tip - Get a motivational study tip 💡\n"
                 "/feedback - Send your thoughts or report issues 📝\n"
                 "/about - About this bot 🤖\n"
                 "/clear - clears the chat 🤖\n"
                 "/help - Show all commands 🧾\n"
                 "/search - Search for notes by keyword 🔍\n"
                 "/quiz - Quizzes 🔍\n"
                 "/explain - Ask anything 🧾")
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


# === /search - Search for notes by keyword ===
@bot.message_handler(commands=['search'])
def search_notes(message):
    query = message.text.replace("/search ", "").strip().lower()
    if not query:
        bot.reply_to(
            message,
            "🔍 Please type something to search. Example:\n/search python")
        return

    results = []
    for category, notes in resources.items():
        for title in notes:
            if query in title.lower():
                results.append(f"📄 {title} (in *{category}*)")

    if results:
        bot.reply_to(message,
                     "🔎 *Search Results:*\n" + "\n".join(results),
                     parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ No matches found.")


import requests

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


@bot.message_handler(commands=['explain'])
def explain_note(message):
    query = message.text.replace("/explain ", "").strip()
    if not query:
        bot.reply_to(
            message,
            "❓ Please enter a topic to explain. Example:\n/explain Merge Sort")
        return

    bot.send_chat_action(message.chat.id, 'typing')  # 🕒 Show "typing..."

    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}

    data = {
        "model":
        "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [{
            "role":
            "user",
            "content":
            f"Explain this topic clearly for a student: {query}"
        }],
        "temperature":
        0.7,
        "max_tokens":
        500
    }

    try:
        res = requests.post("https://api.together.xyz/v1/chat/completions",
                            headers=headers,
                            json=data)
        res.raise_for_status()  # 🚨 Raises error if bad response
        answer = res.json()['choices'][0]['message']['content']
        bot.send_message(message.chat.id,
                         f"📘 *{query}*\n\n{answer}",
                         parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id,
                         f"❌ GPT failed:\n`{str(e)}`",
                         parse_mode="Markdown")


# === /explain_hi - AI Explain in Hindi ===
@bot.message_handler(commands=['explain_hi'])
def explain_in_hindi(message):
    query = message.text.replace("/explain_hi ", "").strip()
    if not query:
        bot.reply_to(
            message,
            "🇮🇳 Please enter a topic to explain in Hindi. Example:\n/explain_hi Merge Sort"
        )
        return

    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    data = {
        "model":
        "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [{
            "role":
            "user",
            "content":
            f"Explain this topic in simple Hindi for students: {query}"
        }],
        "temperature":
        0.7,
        "max_tokens":
        500
    }

    try:
        res = requests.post("https://api.together.xyz/v1/chat/completions",
                            headers=headers,
                            json=data)
        res.raise_for_status()
        answer = res.json()['choices'][0]['message']['content']
        bot.send_message(message.chat.id,
                         f"🇮🇳 *{query}*\n\n{answer}",
                         parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id,
                         f"❌ GPT Hindi failed:\n`{str(e)}`",
                         parse_mode="Markdown")


# === /clear - Clears the last interaction ===
@bot.message_handler(commands=['clear'])
def clear_chat(message):
    try:
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
    except:
        pass  # Skip if message already deleted or can't be deleted
    bot.send_message(message.chat.id, "🧹 Cleared! Type /start to begin fresh.")


# === /createpoll - Admin Creates Custom Poll ===
@bot.message_handler(commands=['createpoll'])
def create_poll_start(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "❌ You’re not authorized to create polls.")
        return
    msg = bot.reply_to(message, "🗳️ What’s your poll question?")
    bot.register_next_step_handler(msg, get_poll_question)


poll_data = {}


def get_poll_question(message):
    poll_data['question'] = message.text
    msg = bot.reply_to(
        message,
        "✏️ Now enter poll options separated by commas (,)\nExample:\nPython, Java, C++"
    )
    bot.register_next_step_handler(msg, get_poll_options)


def get_poll_options(message):
    options = [opt.strip() for opt in message.text.split(',') if opt.strip()]
    if len(options) < 2:
        msg = bot.reply_to(message, "❌ Minimum 2 options required. Try again:")
        bot.register_next_step_handler(msg, get_poll_options)
        return

    poll_data['options'] = options
    question = poll_data['question']
    confirm_msg = f"📌 *Poll Preview:*\n\n*Q:* {question}\n"
    confirm_msg += "\n".join(
        [f"{i+1}. {opt}" for i, opt in enumerate(options)])
    confirm_msg += "\n\nSend /pollall to broadcast it to everyone."

    bot.send_message(message.chat.id, confirm_msg, parse_mode='Markdown')


@bot.message_handler(commands=['pollall'])
def broadcast_poll(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "❌ You're not authorized to broadcast polls.")
        return

    question = poll_data.get('question')
    options = poll_data.get('options')
    if not question or not options:
        bot.reply_to(message, "❌ No poll prepared yet. Use /createpoll first.")
        return

    success = 0
    for user_id in user_ids:
        try:
            bot.send_poll(chat_id=user_id,
                          question=question,
                          options=options,
                          is_anonymous=False,
                          allows_multiple_answers=False)
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ Poll sent to {success} users!")


from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


# === /website - Open Your Website in WebView ===
@bot.message_handler(commands=['website'])
def open_website(message):
    web_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    web_markup.add(
        KeyboardButton(
            text="🌐 Open My Website",
            web_app=WebAppInfo(url="https://primekris.github.io/BLOGGY")))
    bot.send_message(
        message.chat.id,
        "✨ Tap the button below to visit my site inside Telegram:",
        reply_markup=web_markup)


# === RUN THE BOT ===
print("🤖 Bot is running!")
bot.infinity_polling()



from flask import Flask
import threading

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!", 200

def run_web():
    app_flask.run(host="0.0.0.0", port=3000)

threading.Thread(target=run_web).start()
