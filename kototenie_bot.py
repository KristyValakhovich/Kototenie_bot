import telebot
from telebot.types import Message, CallbackQuery
import config
import database as db
import keyboards as kb

bot = telebot.TeleBot(config.BOT_TOKEN)
db.init_db()

user_states = {}

def is_allowed(user_id: int) -> bool:
    return user_id in config.ALLOWED_USERS

def check_access(func):
    def wrapper(message_or_call, *args, **kwargs):
        user_id = message_or_call.from_user.id
        if not is_allowed(user_id):
            if isinstance(message_or_call, Message):
                bot.send_message(message_or_call.chat.id, "🔒 Доступ ограничен. Это приватный бот.")
            elif isinstance(message_or_call, CallbackQuery):
                bot.answer_callback_query(message_or_call.id, "🔒 Доступ ограничен.")
            return
        return func(message_or_call, *args, **kwargs)
    return wrapper

def send_idea_content(chat_id: int, idea, reply_markup, edit_message_id=None):
    c_type = idea['content_type']
    text = idea['text_content'] or ""
    media_id = idea['media_file_id']
    category_tag = f"\n\n🏷 Категория: #{idea['category']}"

    if c_type == 'text':
        full_text = text + category_tag
        if edit_message_id:
            try:
                bot.edit_message_text(full_text, chat_id, edit_message_id, reply_markup=reply_markup)
            except Exception:
                bot.send_message(chat_id, full_text, reply_markup=reply_markup)
        else:
            bot.send_message(chat_id, full_text, reply_markup=reply_markup)

    elif c_type == 'photo':
        caption = (text + category_tag) if text else f"🏷 Категория: #{idea['category']}"
        if edit_message_id:
            bot.delete_message(chat_id, edit_message_id)
        bot.send_photo(chat_id, media_id, caption=caption, reply_markup=reply_markup)

    elif c_type == 'voice':
        caption = (text + category_tag) if text else f"🏷 Категория: #{idea['category']}"
        if edit_message_id:
            bot.delete_message(chat_id, edit_message_id)
        bot.send_voice(chat_id, media_id, caption=caption, reply_markup=reply_markup)

    elif c_type == 'document':
        caption = (text + category_tag) if text else f"🏷 Категория: #{idea['category']}"
        if edit_message_id:
            bot.delete_message(chat_id, edit_message_id)
        bot.send_document(chat_id, media_id, caption=caption, reply_markup=reply_markup)

@bot.message_handler(commands=['start'])
@check_access
def send_welcome(message: Message):
    bot.send_message(
        message.chat.id,
        "Привет! Добро пожаловать в ваш общий конверт с идеями для свиданий. ❤️",
        reply_markup=kb.remove_keyboard()
    )
    send_main_menu(message.chat.id)

def send_main_menu(chat_id: int):
    bot.send_message(
        chat_id,
        "💫 **Что замутим?** Выберите действие из меню:",
        parse_mode="Markdown",
        reply_markup=kb.main_menu_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
@check_access
def handle_callbacks(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data == "main_menu":
        bot.edit_message_text("💫 **Что замутим?** Выберите действие из меню:", chat_id, message_id, parse_mode="Markdown", reply_markup=kb.main_menu_keyboard())

    elif data == "random_any":
        idea = db.get_random_idea()
        if idea:
            send_idea_content(chat_id, idea, kb.idea_action_keyboard(idea['id']), edit_message_id=message_id)
        else:
            bot.edit_message_text("💌 В конверте пока нет новых идей. Добавьте новую!", chat_id, message_id, reply_markup=kb.back_to_main_keyboard())

    elif data == "choose_category":
        categories = db.get_categories()
        if categories:
            bot.edit_message_text("🔥 Выберите категорию:", chat_id, message_id, reply_markup=kb.categories_keyboard(categories))
        else:
            bot.edit_message_text("💌 Категорий пока нет.", chat_id, message_id, reply_markup=kb.back_to_main_keyboard())

    elif data.startswith("random_cat_"):
        cat = data.replace("random_cat_", "")
        idea = db.get_random_idea(category=cat)
        if idea:
            send_idea_content(chat_id, idea, kb.idea_action_keyboard(idea['id']), edit_message_id=message_id)
        else:
            bot.edit_message_text(f"💌 В категории #{cat} нет новых идей.", chat_id, message_id, reply_markup=kb.back_to_main_keyboard())

    elif data.startswith("complete_"):
        idea_id = int(data.split("_")[1])
        db.update_idea_status(idea_id, "done")
        bot.delete_message(chat_id, message_id)
        idea = db.get_random_idea()
        if idea:
            send_idea_content(chat_id, idea, kb.idea_action_keyboard(idea['id']))
        else:
            bot.send_message(chat_id, "✨ Идея сохранена в «Наши моменты». В конверте больше нет новых идей!", reply_markup=kb.back_to_main_keyboard())

    elif data.startswith("view_idea_"):
        idea_id = int(data.split("_")[1])
        idea = db.get_idea_by_id(idea_id)
        if idea:
            send_idea_content(chat_id, idea, kb.idea_action_keyboard(idea['id']), edit_message_id=message_id)

    elif data.startswith("settings_"):
        idea_id = int(data.split("_")[1])
        bot.edit_message_text("⚙️ **Настройки идеи:** Выберите действие", chat_id, message_id, parse_mode="Markdown", reply_markup=kb.idea_settings_keyboard(idea_id))

    elif data.startswith("confirm_delete_"):
        idea_id = int(data.split("_")[1])
        bot.edit_message_text("❓ Вы уверены, что хотите удалить эту идею?", chat_id, message_id, reply_markup=kb.confirm_delete_keyboard(idea_id))

    elif data.startswith("delete_"):
        idea_id = int(data.split("_")[1])
        db.delete_idea(idea_id)
        bot.edit_message_text("🗑 Идея успешно удалена.", chat_id, message_id, reply_markup=kb.back_to_main_keyboard())

    elif data == "add_idea":
        user_states[chat_id] = {"step": "wait_content"}
        bot.edit_message_text("✏️ Отправьте идею (текст, фото или голосовое сообщение):", chat_id, message_id)

    elif data.startswith("edit_title_"):
        idea_id = int(data.split("_")[2])
        user_states[chat_id] = {"step": "edit_content", "idea_id": idea_id}
        bot.edit_message_text("✏️ Отправьте новый контент для идеи (текст, фото или голос):", chat_id, message_id)

    elif data.startswith("edit_cat_"):
        idea_id = int(data.split("_")[2])
        user_states[chat_id] = {"step": "edit_cat", "idea_id": idea_id}
        bot.edit_message_text("🏷 Введите новую категорию:", chat_id, message_id)

    elif data == "collection_menu":
        bot.edit_message_text("📚 **Наша коллекция**\nВыберите список:", chat_id, message_id, parse_mode="Markdown", reply_markup=kb.collection_menu_keyboard())

    elif data == "list_new":
        ideas = db.get_ideas_by_status("new")
        text = "✨ **Идеи, которые ждут своего часа:**\n\n"
        if not ideas:
            text += "Список пуст."
        else:
            for idx, item in enumerate(ideas, 1):
                preview = item['text_content'] or f"[{item['content_type']}]"
                if len(preview) > 30:
                    preview = preview[:30] + "..."
                text += f"{idx}. {preview} (`#{item['category']}`)\n"
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=kb.back_to_main_keyboard())

    elif data == "list_done":
        ideas = db.get_ideas_by_status("done")
        text = "❤️ **Наши моменты:**\n\n"
        if not ideas:
            text += "Пока нет реализованных идей."
        else:
            for idx, item in enumerate(ideas, 1):
                preview = item['text_content'] or f"[{item['content_type']}]"
                if len(preview) > 30:
                    preview = preview[:30] + "..."
                text += f"{idx}. {preview} (`#{item['category']}`)\n"
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=kb.back_to_main_keyboard())

    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['text', 'photo', 'voice', 'document'])
@check_access
def handle_incoming_content(message: Message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if not state:
        send_main_menu(chat_id)
        return

    step = state.get("step")

    content_type = 'text'
    text_content = message.text or message.caption
    media_file_id = None

    if message.photo:
        content_type = 'photo'
        media_file_id = message.photo[-1].file_id
    elif message.voice:
        content_type = 'voice'
        media_file_id = message.voice.file_id
    elif message.document:
        content_type = 'document'
        media_file_id = message.document.file_id

    if step == "wait_content":
        user_states[chat_id]["content_type"] = content_type
        user_states[chat_id]["text_content"] = text_content
        user_states[chat_id]["media_file_id"] = media_file_id
        user_states[chat_id]["step"] = "wait_category"
        bot.send_message(chat_id, "🏷 Теперь отправьте название категории для этой идеи (например: *Дома*, *Прогулка*):", parse_mode="Markdown")

    elif step == "wait_category":
        category = message.text
        c_type = user_states[chat_id]["content_type"]
        t_content = user_states[chat_id]["text_content"]
        m_id = user_states[chat_id]["media_file_id"]

        db.add_idea(c_type, category, t_content, m_id)
        del user_states[chat_id]
        bot.send_message(chat_id, "🎉 **Идея успешно добавлена в конверт!**", parse_mode="Markdown", reply_markup=kb.back_to_main_keyboard())

    elif step == "edit_content":
        idea_id = state["idea_id"]
        db.update_idea_content(idea_id, content_type, text_content, media_file_id)
        del user_states[chat_id]
        bot.send_message(chat_id, "✅ Содержимое идеи обновлено!", reply_markup=kb.back_to_main_keyboard())

    elif step == "edit_cat":
        idea_id = state["idea_id"]
        db.update_idea_category(idea_id, message.text)
        del user_states[chat_id]
        bot.send_message(chat_id, "✅ Категория идеи обновлена!", reply_markup=kb.back_to_main_keyboard())

if __name__ == "__main__":
    print("Бот успешно запущен...")
    bot.infinity_polling(skip_pending=True)