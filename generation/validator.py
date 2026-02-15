def validate_vk_post(text: str, structure: dict):
    soft_errors = []
    hard_errors = []

    squad = structure["squad_name"]

    if len(text) < 500:
        soft_errors.append("Текст короче 500 символов")

    if squad in text[:-200]:
        hard_errors.append("Название отряда упоминается не только в конце")

    if "Ключевые действия" in text:
        hard_errors.append("Лишний служебный блок")

    if not any(word in text.lower() for word in ["мы", "наш", "наши"]):
        soft_errors.append("Нет повествования от первого лица")

    return soft_errors, hard_errors
