from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

def remove_keyboard():
    return ReplyKeyboardRemove()

def main_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎲 Случайная идея", callback_data="random_any"),
        InlineKeyboardButton("🔥 Из категории", callback_data="choose_category")
    )
    kb.add(
        InlineKeyboardButton("➕ Добавить идею", callback_data="add_idea"),
        InlineKeyboardButton("📚 Наша коллекция", callback_data="collection_menu")
    )
    return kb

def categories_keyboard(categories):
    kb = InlineKeyboardMarkup(row_width=2)
    for cat in categories:
        kb.add(InlineKeyboardButton(f"🔥 {cat}", callback_data=f"random_cat_{cat}"))
    kb.add(InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu"))
    return kb

def idea_action_keyboard(idea_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✨ Вперед!", callback_data=f"complete_{idea_id}"),
        InlineKeyboardButton("🎲 В другой раз", callback_data="random_any")
    )
    kb.add(
        InlineKeyboardButton("⚙️ Настройки идеи", callback_data=f"settings_{idea_id}")
    )
    kb.add(
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    )
    return kb

def idea_settings_keyboard(idea_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✏️ Текст/Контент", callback_data=f"edit_title_{idea_id}"),
        InlineKeyboardButton("🏷 Категорию", callback_data=f"edit_cat_{idea_id}")
    )
    kb.add(
        InlineKeyboardButton("🗑 Удалить", callback_data=f"confirm_delete_{idea_id}")
    )
    kb.add(
        InlineKeyboardButton("◀️ Назад к идее", callback_data=f"view_idea_{idea_id}")
    )
    return kb

def confirm_delete_keyboard(idea_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("❌ Да, удалить", callback_data=f"delete_{idea_id}"),
        InlineKeyboardButton("↩️ Отмена", callback_data=f"settings_{idea_id}")
    )
    return kb

def collection_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✨ Ждут своего часа", callback_data="list_new"),
        InlineKeyboardButton("❤️ Наши моменты", callback_data="list_done"),
        InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")
    )
    return kb

def back_to_main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    return kb