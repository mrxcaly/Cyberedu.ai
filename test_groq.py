import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
print(f"Ключ прочитан: {key[:10] if key else 'НЕТ КЛЮЧА'}...")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {
    "model": "openai/gpt-oss-20b",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 10
}

try:
    print("Отправляем запрос в Groq...")
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Статус ответа: {r.status_code}")
    print(f"Ответ: {r.text}")
except Exception as e:
    print(f"Ошибка подключения: {e}")