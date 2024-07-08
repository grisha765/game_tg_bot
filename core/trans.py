import json

def load_translations():
    translations = {
        "ru": json.load(open("config/lang/ru.json", encoding="utf-8")),
        "en": json.load(open("config/lang/en.json", encoding="utf-8"))
    }
    return translations

def get_translation(lang_code, key):
    return load_translations().get(lang_code, load_translations()["en"]).get(key, key)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
