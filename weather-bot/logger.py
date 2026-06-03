import os
from datetime import datetime

LOGS_DIR = "logs"

def log(user_id: int, action: str, detail: str = ""):
    """
    Записывает действие пользователя в его лог-файл.
    
    user_id уникальный ID пользователя из Telegram
    action название действия (например "WEATHER", "FORECAST")
    detail дополнительная информация (город, результат и т.д.)
    """
    # Создаём папку logs если её нет
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Путь к файлу пользователя: logs/123456789.log
    log_path = os.path.join(LOGS_DIR, f"{user_id}.log")

    # Текущее время
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формируем строку лога
    if detail:
        line = f"[{timestamp}] {action}: {detail}\n"
    else:
        line = f"[{timestamp}] {action}\n"

    # Записываем в файл (дописываем в конец)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def get_history(user_id: int) -> str:
    """
    Читает и возвращает историю пользователя из его лог-файла.
    Если файла нет возвращает сообщение что истории пока нет.
    """
    log_path = os.path.join(LOGS_DIR, f"{user_id}.log")

    if not os.path.exists(log_path):
        return "📭 История запросов пуста."

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return "📭 История запросов пуста."

    # Берём последние 20 записей чтобы не перегружать сообщение
    last_lines = lines[-20:]
    history_text = "📋 Твоя история запросов:\n\n"
    history_text += "".join(last_lines)

    return history_text