import os

import yaml

from config import BASE_DIR, LOCALE

_translations: dict | None = None


def _load_translations() -> dict:
    global _translations
    if _translations is None:
        locale_path = os.path.join(BASE_DIR, "locales", f"{LOCALE}.yaml")
        with open(locale_path, encoding="utf-8") as f:
            _translations = yaml.safe_load(f)
    return _translations


def t(key: str, **kwargs) -> str:
    translations = _load_translations()
    value = translations
    for part in key.split("."):
        value = value[part]
    if kwargs:
        return value.format(**kwargs)
    return value
