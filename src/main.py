import json
import random
import telebot
from data import messages
import threading
import time

TOKEN = '*Нужно узазать токен*'
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'data/user_data.json'

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.message_handler(commands=['start'])
def handle_start(message):
    data = load_data()
    user_id = str(message.from_user.id)
    username = message.from_user.username
    display_name = f"{message.from_user.first_name} (@{username})" if username else message.from_user.first_name

    if username:
        data["usernames"][user_id] = username
    if display_name not in data["recent_users"]:
        data["recent_users"].append(display_name)
    if int(user_id) not in data["subscribers"]:
        data["subscribers"].append(int(user_id))

    save_data(data)
    bot.reply_to(message, "✨ Добро пожаловать в мир доброты и мотивации! Напиши /help, если потерялся 🌈")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "🧭 Команды бота:\n"
        "/start - ✨ Запустить добро и мотивацию\n"
        "/now - 💡 Получить мотивацию прямо сейчас\n"
        "/subscribe - 💌 Подписаться на редкие мотивации\n"
        "/unsubscribe - 🚫 Отписаться от мотивации\n"
        "/friend @username - 🤝 Отправить мотивацию другу\n"
        "/hug @username - 🫂 Обнять друга\n"
        "/flip - 🎲 Подбросить монетку (пчёлка или божья коровка)\n"
        "/story - 📖 Получить добрую сказку\n"
        "/inspire - 🎨 Идея для творчества\n"
        "/donate - ☕️ Поддержать автора\n"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['now'])
def handle_now(message):
    quote = random.choice(messages.quotes)
    bot.send_message(message.chat.id, f"💡 {quote}")

@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    data = load_data()
    user_id = int(message.from_user.id)
    if user_id not in data["subscribers"]:
        data["subscribers"].append(user_id)
        save_data(data)
        bot.reply_to(message, "💌 Подписка оформлена. Мотивация будет приходить время от времени 💛")
    else:
        bot.reply_to(message, "Ты уже подписан 😊")

@bot.message_handler(commands=['unsubscribe'])
def handle_unsubscribe(message):
    data = load_data()
    user_id = int(message.from_user.id)
    if user_id in data["subscribers"]:
        data["subscribers"].remove(user_id)
        save_data(data)
        bot.reply_to(message, "🚫 Подписка отменена. Мы всё равно тебя любим 💛")
    else:
        bot.reply_to(message, "Ты и так не подписан 🐢")

@bot.message_handler(commands=['friend'])
def friend_message(message):
    try:
        data = load_data()
        usernames = data["usernames"]
        quotes = messages.quotes

        parts = message.text.split()
        if len(parts) != 2 or not parts[1].startswith('@'):
            raise ValueError
        friend_username = parts[1][1:]
        friend_chat_id = next((int(cid) for cid, uname in usernames.items() if uname == friend_username), None)

        if friend_chat_id:
            bot.send_message(friend_chat_id, f"{message.from_user.first_name} (@{message.from_user.username}) послал(а) тебе мотивашку:\n\n{random.choice(quotes)}")
            bot.send_message(message.chat.id, f"Сообщение отправлено @{friend_username} 💌")
        else:
            bot.send_message(message.chat.id, f"@{friend_username} ещё не запускал(а) бота... 😔")
    except:
        bot.send_message(message.chat.id, "Используй команду так: /friend @username")

@bot.message_handler(commands=['hug'])
def hug_message(message):
    try:
        data = load_data()
        usernames = data["usernames"]
        hug_messages = messages.hug_messages

        parts = message.text.split()
        if len(parts) != 2 or not parts[1].startswith('@'):
            raise ValueError
        friend_username = parts[1][1:]
        friend_chat_id = next((int(cid) for cid, uname in usernames.items() if uname == friend_username), None)

        if friend_chat_id:
            msg = random.choice(hug_messages)
            bot.send_message(friend_chat_id, f"{message.from_user.first_name} (@{message.from_user.username}) {msg}")
            bot.send_message(message.chat.id, f"Обнимашка отправлена @{friend_username} 🫂")
        else:
            bot.send_message(message.chat.id, f"@{friend_username} ещё не запускал(а) бота. Пусть напишет /start!")
    except:
        bot.send_message(message.chat.id, "Используй команду так: /hug @username")

@bot.message_handler(commands=['flip'])
def handle_flip(message):
    result = random.choice(["🐝 Пчёлка", "🐞 Божья коровка"])
    bot.reply_to(message, f"🎲 {result}!")

@bot.message_handler(commands=['story'])
def handle_story(message):
    story = random.choice(messages.stories)
    bot.send_message(message.chat.id, f"📖 {story}")

@bot.message_handler(commands=['inspire'])
def handle_inspire(message):
    idea = random.choice(messages.creative_prompts)
    bot.send_message(message.chat.id, f"🎨 {idea}")

@bot.message_handler(commands=['donate'])
def handle_donate(message):
    bot.reply_to(message, "☕️ Поддержать автора: https://www.tbank.ru/cf/nAOIjJI6s4")

@bot.message_handler(commands=['users'])
def show_users(message):
    data = load_data()
    admin_usernames = messages.admin_usernames  # или admin_username, в зависимости от того, как ты это назвал
    recent_users = data.get("recent_users", [])

    if message.from_user.username not in admin_usernames:
        return

    if not recent_users:
        bot.send_message(message.chat.id, "Пока никто не запускал бота.")
    else:
        user_list = "\n".join([f"{i+1}. {user}" for i, user in enumerate(recent_users)])
        bot.send_message(message.chat.id, f"👥 Последние пользователи:\n\n{user_list}")


def send_motivation_to_subscribers():
    while True:
        data = load_data()
        subscribers = data.get("subscribers", [])
        total = len(subscribers)

        if total == 0:
            time.sleep(3600)
            continue

        # Адаптивные параметры
        if total <= 20:
            hourly_chance = 0.2
            send_percent = 0.25
        elif total <= 50:
            hourly_chance = 0.15
            send_percent = 0.20
        else:
            hourly_chance = 0.10
            send_percent = 0.15

        # Рандом: будет ли рассылка в этом часу
        if random.random() < hourly_chance:
            send_count = max(1, int(total * send_percent))
            selected_users = random.sample(subscribers, send_count)
            for user_id in selected_users:
                try:
                    bot.send_message(user_id, f"💌 {random.choice(messages.quotes)}")
                    print(f"Мотивация отправлена пользователю {user_id}")
                except Exception as e:
                    print(f"Ошибка при отправке пользователю {user_id}: {e}")
        else:
            print("Час пропущен — рассылка не сработала.")

        time.sleep(3600)

threading.Thread(target=send_motivation_to_subscribers, daemon=True).start()
bot.polling(none_stop=True)
