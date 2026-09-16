from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

GENDER_LABELS = {"male": "Мужской", "female": "Женский"}
LOOKING_FOR_LABELS = {"male": "Парней", "female": "Девушек", "any": "Всех"}


def remove():
    return ReplyKeyboardRemove()


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🔍 Смотреть анкеты")],
        [KeyboardButton(text="👤 Моя анкета"), KeyboardButton(text="✏️ Изменить анкету")],
        [KeyboardButton(text="❤️ Кто меня лайкнул"), KeyboardButton(text="⚙️ Настройки поиска")],
        [KeyboardButton(text="❓ Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def gender_kb(prefix: str = "gender") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨 Мужской", callback_data=f"{prefix}:male"),
            InlineKeyboardButton(text="👩 Женский", callback_data=f"{prefix}:female"),
        ]
    ])


def looking_for_kb(prefix: str = "lf") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨 Парня", callback_data=f"{prefix}:male"),
            InlineKeyboardButton(text="👩 Девушку", callback_data=f"{prefix}:female"),
        ],
        [InlineKeyboardButton(text="🌈 Не важно", callback_data=f"{prefix}:any")],
    ])


def browse_kb(target_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👎", callback_data=f"dislike:{target_id}"),
            InlineKeyboardButton(text="❤️", callback_data=f"like:{target_id}"),
        ],
        [InlineKeyboardButton(text="⚠️ Пожаловаться", callback_data=f"complain:{target_id}")],
    ])


def my_profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать анкету", callback_data="goto_edit")]
    ])


def edit_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя", callback_data="edit:name"),
            InlineKeyboardButton(text="🎂 Возраст", callback_data="edit:age"),
        ],
        [
            InlineKeyboardButton(text="📍 Город", callback_data="edit:city"),
            InlineKeyboardButton(text="💬 О себе", callback_data="edit:about"),
        ],
        [InlineKeyboardButton(text="📸 Фото", callback_data="edit:photo")],
        [
            InlineKeyboardButton(text="🚻 Мой пол", callback_data="edit:gender"),
            InlineKeyboardButton(text="🔎 Кого ищу", callback_data="edit:looking_for"),
        ],
    ])


def settings_kb(current_mode: str) -> InlineKeyboardMarkup:
    city_label = ("✅ " if current_mode == "city" else "") + "🏙 Мой город"
    all_label = ("✅ " if current_mode == "all" else "") + "🌍 Все города"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=city_label, callback_data="setmode:city"),
            InlineKeyboardButton(text=all_label, callback_data="setmode:all"),
        ],
        [InlineKeyboardButton(text="🎂 Возрастной диапазон партнёра", callback_data="setage")],
    ])


def profile_caption(p: dict) -> str:
    return (
        f"<b>{p['name']}, {p['age']}</b>\n"
        f"📍 {p['city']}\n\n"
        f"{p['about']}"
    )
