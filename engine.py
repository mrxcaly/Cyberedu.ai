import json
import os
import sys
import time
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# ANSI-коды для цветового оформления в терминале Kali Linux
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

class CyberGameEngine:
    def __init__(self, quest_filepath: str, use_ai: bool = True):
        if not os.path.exists(quest_filepath):
            raise FileNotFoundError(f"Kvest fayli topilmadi: {quest_filepath}")
            
        with open(quest_filepath, 'r', encoding='utf-8') as f:
            self.quest = json.load(f)
            
        self.current_step = 0
        self.total_steps = len(self.quest["steps"])
        self.use_ai = use_ai
        
        # Настройки Groq API
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def get_current_instruction(self) -> str:
        if self.is_completed():
            return "Kvest yakunlandi."
        return self.quest["steps"][self.current_step]["instruction"]

    def _simulate_progress(self, delay_sec: int, is_hashcat: bool = False):
        """Эмуляция выполнения команды с динамическим прогресс-баром в реальном времени"""
        if is_hashcat:
            print("\nhashcat (v6.2.6) starting in autodetected background mode...")
            print("OpenCL API (OpenCL 3.0 PoCL) on CyberEdu Engine")
            print("* Device #1: NVIDIA GeForce RTX 3060 (12012 MB)")
            print("Dictionary: rockyou.txt (14,344,384 words)\n")
            print("[+] Initializing attack (WPA-PBKDF2-PMKID/EAPOL)...")
            
            candidates = ["12345678", "password", "dragon123", "iloveyou", "supersecret123"]
            steps = 40
            sleep_time = delay_sec / steps
            
            for i in range(1, steps + 1):
                percent = int((i / steps) * 100)
                filled = int((percent / 100) * 20)
                bar = "=" * filled + ">" + " " * (20 - filled)
                cand = candidates[(i // 8) % len(candidates)]
                
                # Перезапись одной строки в терминале
                sys.stdout.write(f"\r{COLOR_CYAN}[{bar}] {percent}% | Speed: 142.5 kH/s | Candidate: {cand:<15}{COLOR_RESET}")
                sys.stdout.flush()
                time.sleep(sleep_time)
            print("\n")
        else:
            print(f"\n[*] Jarayon bajarilmoqda... ({delay_sec} soniya)")
            steps = 25
            sleep_time = delay_sec / steps
            for i in range(1, steps + 1):
                percent = int((i / steps) * 100)
                filled = int((percent / 100) * 20)
                bar = "=" * filled + ">" + " " * (20 - filled)
                sys.stdout.write(f"\r{COLOR_CYAN}[{bar}] {percent}% [Scanning/Processing...]{COLOR_RESET}")
                sys.stdout.flush()
                time.sleep(sleep_time)
            print("\n")

    def _get_groq_ai_hint(self, user_cmd: str, expected_cmd: str, instruction: str) -> str:
        """Запрос к модели openai/gpt-oss-20b в Groq API"""
        default_hint = self.quest["steps"][self.current_step].get("hint") or "Bayroqlarni va buyruq sintaksisini tekshiring."
        
        if not self.api_key:
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
                
                reasoning = msg.get("reasoning", "").strip()
                if reasoning:
                    return reasoning
        except Exception:
            pass
        
        return default_hint

    def process_command(self, user_command: str) -> dict:
        if self.is_completed():
            return {"status": "completed", "output": "Kvest allaqachon yakunlangan."}

        step_data = self.quest["steps"][self.current_step]
        clean_user = user_command.strip()
        clean_expected = step_data["expected_command"].strip()

        if clean_user == clean_expected:
            # Анимация задержки при совпадении команды
            if "delay" in step_data and step_data["delay"] > 0:
                is_hashcat = "hashcat" in clean_expected
                self._simulate_progress(step_data["delay"], is_hashcat=is_hashcat)

            self.current_step += 1
            completed = self.is_completed()
            return {
                "status": "success",
                "output": step_data["output"],
                "completed": completed,
                "next_instruction": self.get_current_instruction() if not completed else None
            }
        else:
            raw_hint = self._get_groq_ai_hint(clean_user, clean_expected, step_data["instruction"]) if self.use_ai else step_data.get("hint", "")
            
            # Зеленый цвет для подсказки ИИ
            green_hint = f"{COLOR_GREEN}💡 AI: {raw_hint}{COLOR_RESET}" if raw_hint else ""
            
            return {
                "status": "error",
                "output": f"bash: buyruq topilmadi yoki sintaksis xatosi: '{clean_user}'",
                "hint": green_hint
            }

    def is_completed(self) -> bool:
        return self.current_step >= self.total_steps