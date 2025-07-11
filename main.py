import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import random
from urllib.parse import quote, unquote
import time
from datetime import datetime, time as dtime
from threading import Thread


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 7924807866  # Your Telegram ID
user_ids = set()  # To store user chat IDs

# === YOUR RESOURCES DATABASE ===
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


# === START COMMAND ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.chat.id)

    markup = InlineKeyboardMarkup()
# okk2
    @bot.callback_query_handler(func=lambda call: True)
    def handle_buttons(call):
        try:
            data = unquote(call.data)
            parts = data.split('|')

            if len(parts) == 1:
                # Category selected → show sub-topics
                category = parts[0].strip()
                if category in resources:
                    submarkup = InlineKeyboardMarkup()
                    for sub in resources[category]:
                        # Check if it's a subfolder (dict) or direct file (str)
                        if isinstance(resources[category][sub], dict):
                            callback = quote(f"{category}|{sub}")
                        else:
                            # Direct file – also use sub as filename
                            callback = quote(f"{category}|{sub}")
                        submarkup.add(InlineKeyboardButton(text=sub, callback_data=callback))

                    bot.send_message(call.message.chat.id,
                                     f"📂 *{category}* files:",
                                     reply_markup=submarkup,
                                     parse_mode="Markdown")

                else:
                    bot.send_message(call.message.chat.id, "❌ Invalid category.")

            elif len(parts) == 2:
                # Sub-topic selected → send files
                category, sub = parts[0].strip(), parts[1].strip()
                files_dict = resources.get(category, {}).get(sub, {})

                if not isinstance(files_dict, dict) or not files_dict:
                    # If it's not a dict, it's likely a single file_id (string)
                    file_id = resources.get(category, {}).get(sub)
                    if file_id:
                        bot.send_document(
                            call.message.chat.id,
                            file_id,
                            caption=f"📄 *{sub}*",
                            parse_mode='Markdown'
                        )
                    else:
                        bot.send_message(call.message.chat.id, "❌ No file found.")
                    return

                for file_name, file_id in files_dict.items():
                    try:
                        bot.send_document(
                            call.message.chat.id,
                            file_id,
                            caption=f"📄 *{file_name}*",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        bot.send_message(call.message.chat.id,
                                         f"❌ Failed to send `{file_name}`:\n`{e}`",
                                         parse_mode='Markdown')
            else:
                bot.send_message(call.message.chat.id, "⚠️ Unrecognized action.")

        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error: {str(e)}")

    # Add resource categories
    for category in resources:
        markup.add(InlineKeyboardButton(text=category, callback_data=quote(category)))


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
def send_subtopics(call):
    category = call.data
    markup = InlineKeyboardMarkup()
    for subtopic in resources[category]:
        markup.add(InlineKeyboardButton(
            text=subtopic,
            callback_data=f"{category}|{subtopic}"
        ))
    bot.send_message(
        call.message.chat.id,
        f"📚 Choose a topic from *{category}*:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# okk
    @bot.callback_query_handler(func=lambda call: '|' in call.data)
    def send_pdf(call):
        category, sub = map(str.strip, call.data.split('|'))

        print(f"[DEBUG] call.data = {call.data}")
        print(f"[DEBUG] category = '{category}' | sub = '{sub}'")

        section = resources.get(category)

        if not section:
            bot.send_message(call.message.chat.id, "❌ Category not found.")
            return

        # ✅ CASE 1: Entire category is a flat dict with filenames
        if sub in section and isinstance(section[sub], str):
            file_id = section[sub]
            try:
                bot.send_document(
                    call.message.chat.id,
                    document=file_id,
                    caption=f"📄 *{sub}*",
                    parse_mode='Markdown'
                )
            except Exception as e:
                bot.send_message(
                    call.message.chat.id,
                    f"❌ Failed to send `{sub}`:\n`{e}`",
                    parse_mode='Markdown'
                )
            return

        # ✅ CASE 2: Subfolder with multiple files
        elif sub in section and isinstance(section[sub], dict):
            files_dict = section[sub]
            if not files_dict:
                bot.send_message(call.message.chat.id, "❌ No files found in this topic.")
                return

            for file_name, file_id in files_dict.items():
                try:
                    bot.send_document(
                        call.message.chat.id,
                        document=file_id,
                        caption=f"📄 *{file_name}*",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    bot.send_message(
                        call.message.chat.id,
                        f"❌ Failed to send `{file_name}`:\n`{e}`",
                        parse_mode='Markdown'
                    )
            return

        # ❌ CASE 3: sub not found in category
        bot.send_message(call.message.chat.id, "❌ This file or folder does not exist.")


# === FILE SENDER ===




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

# Store user submissions temporarily for replies
submitted_users = {}

@bot.message_handler(commands=['submit'])
def handle_submit(message):
    msg = bot.reply_to(message, "📤 Please send your notes file (PDF, doc, etc.) with a short title.")
    bot.register_next_step_handler(msg, receive_user_submission)

def receive_user_submission(message):
    if message.document:
        user_id = message.chat.id
        file_name = message.document.file_name
        file_id = message.document.file_id
        user_name = message.from_user.username or message.from_user.first_name

        # Save user_id to use for reply
        submitted_users[file_id] = user_id

        # Send file + reply instructions to ADMIN
        bot.send_document(
            ADMIN_ID,
            document=file_id,  # ✅ Add "document=" here
            caption=f"📥 New Submission\n👤 @{user_name}\n🆔 {user_id}\n📄 *{file_name}*\n\n📝 To reply: /reply {file_id} Your message here",
            parse_mode='Markdown'
        )


        bot.reply_to(message, "✅ Thanks for submitting! We'll get back to you soon.")
    else:
        bot.reply_to(message, "⚠️ Please send a valid file. Try /submit again.")

@bot.message_handler(commands=['reply'])
def handle_reply(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "❌ You're not authorized to reply.")
        return

    try:
        parts = message.text.split(' ', 2)
        file_id = parts[1]
        reply_msg = parts[2]
        user_id = submitted_users.get(file_id)

        if not user_id:
            bot.reply_to(message, "❌ No user found for that file ID.")
            return

        bot.send_message(user_id, f"📩 *Reply from Admin:*\n\n{reply_msg}", parse_mode='Markdown')
        bot.reply_to(message, "✅ Reply sent.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}\nFormat: `/reply file_id Your message`", parse_mode='Markdown')


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

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ GenieNotesBot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# okkkkkk3
def check_wakeup():
    while True:
        now = datetime.now().time()
        if dtime(6, 1) <= now <= dtime(6, 2):
            print("🌅 6:01 AM — Sending wake-up message and starting bot!")
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, "🌞 Good morning! GenieNotesBot is now awake. Type /start to continue!")
                except:
                    pass
            bot.infinity_polling()  # Start polling once awake
            break  # Exit this thread — polling takes over
        time.sleep(60)
        

# 👉 START the web server first
# keep_alive()


# # === RUN THE BOT ===
# print("🤖 Bot is running!")
# bot.infinity_polling()


# 👉 Start Flask web server
keep_alive()

now = datetime.now().time()

# ⏰ Night sleep window: 1 AM to 6 AM
if dtime(1, 0) <= now <= dtime(6, 0):
    print("😴 GenieNotesBot is sleeping from 1 AM to 6 AM.")

    def sleep_message():
        while True:
            try:
                for user_id in user_ids:
                    bot.send_message(user_id, "😴 GenieNotesBot is sleeping. Come back after 6:00 AM.")
                break
            except:
                pass

    Thread(target=sleep_message).start()
    Thread(target=check_wakeup).start()

else:
    print("🤖 GenieNotesBot is running!")
    bot.infinity_polling()

