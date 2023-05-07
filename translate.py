import requests
from decouple import config


API_KEY = config('YANDEX_TRANSLATE_API_KEY')
target_language = 'de'
texts = ["Hello", "World"]

body = {
    "targetLanguageCode": target_language,
    "texts": texts
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {API_KEY}"

}

response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                         json=body,
                         headers=headers
                         )

print(response.text)

# response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/languages',
#                          # json=body,
#                          headers=headers
#                          )

print(response.text)
