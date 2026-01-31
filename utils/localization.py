import json
import logging
import os

import discord

import config


class Translator:
    def __init__(self, locales_path='./locales/'):
        self.translations = {}
        self._load_translations(locales_path)

    def _load_translations(self, locales_path):
        loaded_count = 0
        for filename in os.listdir(locales_path):
            if filename.endswith(".json"):
                lang_code = filename[:-5]
                file_path = os.path.join(locales_path, filename)

                try:
                    with open(file_path, 'r') as file:
                        self.translations[lang_code] = json.load(file)
                        loaded_count += 1
                except Exception as e:
                    logging.error(f'Unable to load translation file: {file_path}')
        if loaded_count == 0:
            logging.error('Unable to load any locales. Please check the locales path or clone the repo again.')
            exit(1)

    def _get_nested_value(self, data: dict, key_path: str):
        keys = key_path.split('.')
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None

    def get(self, key: str, locale: discord.Locale, **kwargs):
        lang_code = str(locale)[:2]

        # Fall back to english if language is not localized or if localization is disabled
        if lang_code not in self.translations or not config.enable_localization:
            lang_code = 'en'

        language_dict = self.translations.get(lang_code)
        text = self._get_nested_value(language_dict, key)

        # If string doesn't exist in one language pick its english equivalent
        if text is None:
            default_dict = self.translations.get('en')
            text = self._get_nested_value(default_dict, key)

        return text.format(**kwargs)

translator = Translator()

