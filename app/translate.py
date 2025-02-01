import requests
from flask_babel import _


def translate(text, source_language, dest_language):
    r = requests.get(
        f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{dest_language}"
    )
    if r.status_code != 200:
        return _("Error: the translation service failed.")
    return r.json()["matches"][0]["translation"]
