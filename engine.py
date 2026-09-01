import json
import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class CyberGameEngine:
    def __init__(self, quest_filepath: str, use_ai: bool = True):
        if not os.path.exists(quest_filepath):
            raise FileNotFoundError(f"Kvest fayli topilmadi: {quest_filepath}")
            
        with open(quest_filepath, 'r', encoding='utf-8') as f:
            self.quest = json.load(f)
            
        self.current_step = 0
        self.total_steps = len(self.quest["steps"])
        self.use_ai = use_ai
        
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def get_current_instruction(self) -> str:
        if self.is_completed():
            return "Kvest yakunlandi."
        return self.quest["steps"][self.current_step]["instruction"]

    def _get_groq_ai_hint(self, user_cmd: str, expected_cmd: str, instruction: str) -> str:
        """Запрос к модель openai/gpt-oss-20b в Groq API"""
        default_hint = self.quest["steps"][self.current_step].get("hint") or "Bayroqlarni va buyruq sintaksisini tekshiring."
        
        if not self.api_key:
            print("\n⚠️ [Groq]: GROQ_API_KEY не найден в файле .env!")
            return default_hint

        prompt = f"""
        Foydalanuvchi Kali Linux terminalida xato buyruq kiritdi.
        Topshiriq: {instruction}
        Kutilgan to'g'ri buyruq: {expected_cmd}
        Foydalanuvchi kiritgan xato buyruq: {user_cmd}

        Foydalanuvchiga o'zbek tilida 1-2 jumladan iborat qisqa maslahat ber. 
        Tayyor javobni to'g'ridan-to'g'ri aytma, faqat qaysi bayroq (flag) yoki utilitada xato qilganini tushuntir.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        
        # max_tokens увеличено до 500, чтобы модели хватало места и на reasoning, и на ответ
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=7)
            if response.status_code == 200:
                data = response.json()
                msg = data["choices"][0]["message"]
                
                content = msg.get("content") or ""
                content = content.strip()
                
                if content:
                    return content
                
                # Запасной вариант: если content пуст, забираем reasoning
                reasoning = msg.get("reasoning", "").strip()
                if reasoning:
                    return reasoning
            else:
                print(f"\n⚠️ [Groq API Error {response.status_code}]: {response.text}")
        except Exception as e:
            print(f"\n⚠️ [Groq Connection Error]: {e}")
        
        return default_hint

    def process_command(self, user_command: str) -> dict:
        if self.is_completed():
            return {"status": "completed", "output": "Kvest allaqachon yakunlangan."}

        step_data = self.quest["steps"][self.current_step]
        clean_user = user_command.strip()
        clean_expected = step_data["expected_command"].strip()

        if clean_user == clean_expected:
            self.current_step += 1
            completed = self.is_completed()
            return {
                "status": "success",
                "output": step_data["output"],
                "completed": completed,
                "next_instruction": self.get_current_instruction() if not completed else None
            }
        else:
            hint = self._get_groq_ai_hint(clean_user, clean_expected, step_data["instruction"]) if self.use_ai else step_data.get("hint", "")
            return {
                "status": "error",
                "output": f"bash: buyruq topilmadi yoki sintaksis xatosi: '{clean_user}'",
                "hint": hint
            }

    def is_completed(self) -> bool:
        return self.current_step >= self.total_steps