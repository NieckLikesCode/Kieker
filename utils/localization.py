import json
import logging
import os

import discord

import config


def _get_nested_value(data: dict, key_path: str):
    """
    Resolves to key_path to a subdirectory and retrieves its value
    :param data: lookup dict
    :param key_path: path to value with a dot between subdirectories
    :return: resolved value
    """
    keys = key_path.split('.')
    current = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None

    return current if isinstance(current, str) else None


class Translator:


    def __init__(self, locales_path='./locales/'):
        self.translations = {}
        self._load_translations(locales_path)

    def _load_translations(self, locales_path):
        """
        Loads all available locales from locale directory
        :param locales_path: path to locale directory
        """
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

    def get(self, key: str, locale: discord.Locale, **kwargs):
        """
        Retrieves a key from a language dict
        :param key: value to retrieve
        :param locale: locale to retrieve
        :return: retrieved value if it exists, None otherwise
        """
        lang_code = str(locale)[:2]

        # Fall back to english if language is not localized or if localization is disabled
        if lang_code not in self.translations or config.enable_localization:
            lang_code = config.default_locale

        language_dict = self.translations.get(lang_code)
        text = _get_nested_value(language_dict, key)

        # If string doesn't exist in one language pick its english equivalent
        if text is None:
            default_dict = self.translations.get('en')
            text = _get_nested_value(default_dict, key)

        return text.format(**kwargs)

translator = Translator()

