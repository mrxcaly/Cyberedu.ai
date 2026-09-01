import json
import os
import re
import random
import sys
import time
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# ANSI-коды оформления Kali Linux
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


class CyberGameEngine:
    def __init__(self, quest_filepath: str = None, use_ai: bool = True):
        # Метаданные квеста для отображения в баннере
        self.quest = {
            "title": "WPA2 Handshake & Hashcat Brute-Force",
            "description": "WPA2 tarmog'ini buzish: tarmoq kartasini monitoring rejimiga o'tkazish, handshake ushlash va Hashcat orqali parolni topish."
        }

        if quest_filepath and os.path.exists(quest_filepath):
            try:
                with open(quest_filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.quest["title"] = data.get("title", self.quest["title"])
                    self.quest["description"] = data.get("description", self.quest["description"])
            except Exception:
                pass

        # Состояние игровой системы
        self.state = {
            "monitor_mode": False,
            "handshake_captured": False,
            "cracked": False
        }

        self.use_ai = use_ai
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def get_current_instruction(self) -> str:
        """Динамическое вычисление текущей цели."""
        if self.state["cracked"]:
            return "Kvest muvaffaqiyatli yakunlandi! WPA2 paroli topildi."
        elif not self.state["monitor_mode"]:
            return "wlan0 tarmoq kartasida monitor rejimini yoqing (airmon-ng)."
        elif not self.state["handshake_captured"]:
            return "Atrofdagi tarmoqlarni skanerlang va WPA2 handshake ushlang (airodump-ng)."
        else:
            return "Ushlangan handshake faylini Hashcat yordamida brutforz qiling."

    def is_completed(self) -> bool:
        return self.state["cracked"]

    def _clean_ai_response(self, text: str) -> str:
        """Очистка ответа ИИ без обрезания незавершённых мыслей."""
        if not text:
            return ""

        # Удаляем размышления <think>
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        forbidden_keywords = [
            "we need to", "the user", "instruction", "so we should",
            "meaning", "first, let's", "let's explain", "correct usage",
            "don't give", "tayyor javobni", "expected_cmd"
        ]

        clean_lines = []
        for line in text.split("\n"):
            line_str = line.strip()
            if not line_str or any(key in line_str.lower() for key in forbidden_keywords):
                continue
            clean_lines.append(line_str)

        result = " ".join(clean_lines)
        result = re.sub(r'^(💡\s*)?(AI|ИИ|AI-Maslahat):\s*', '', result, flags=re.IGNORECASE)
        result = re.sub(r'^💡\s*', '', result).strip('"`\' ')

        return result.strip()

    def _simulate_hashcat(self, delay_sec: int = 4):
        """Симуляция подбора пароля в Hashcat."""
        print(f"\n{COLOR_BOLD}hashcat (v6.2.6) starting in autodetected background mode...{COLOR_RESET}\n")
        time.sleep(0.4)
        print("OpenCL API (OpenCL 3.0 PoCL) on CyberEdu Engine")
        print("* Device #1: NVIDIA GeForce RTX 3060, 12012/12287 MB, 28MCU")
        print("Hashes: 1 digest; 1 unique digest")
        print("Target: handshake.hc22000 (WPA-PBKDF2-PMKID/EAPOL)")
        print("Dictionary: rockyou.txt (14,344,384 words)\n")
        print("[+] Initializing speed test and memory allocations...")
        time.sleep(0.6)
        print("[+] Hash-Mode 22000: WPA-PBKDF2-PMKID/EAPOL\n")

        candidates = [
            "12345678", "password", "qwerty123", "admin2024",
            "iloveyou", "dragon123", "sunshine", "supersecret123"
        ]

        steps = 30
        sleep_time = delay_sec / steps

        for i in range(1, steps + 1):
            percent = int((i / steps) * 100)
            filled = int((percent / 100) * 20)
            bar = "=" * filled + ">" + " " * (20 - filled)

            speed = round(138.5 + random.uniform(-4.0, 7.5), 1)
            temp = 58 + int((i / steps) * 12)
            cand = candidates[(i // 5) % len(candidates)]

            status_line = (
                f"\r{COLOR_CYAN}[{bar}] {percent}%{COLOR_RESET} | "
                f"Speed: {speed} kH/s | Temp: {temp}°C | Candidate: {cand:<14}"
            )
            sys.stdout.write(status_line)
            sys.stdout.flush()
            time.sleep(sleep_time)

        print(f"\n\n{COLOR_GREEN}[+] Status: Cracked!{COLOR_RESET}")
        print(f"{COLOR_GREEN}[+] Key.Mode: 001122334455:HomeWiFi:supersecret123{COLOR_RESET}\n")

    def _simulate_generic_scan(self, delay_sec: int = 3):
        """Анимация сканирования сети."""
        print(f"\n[*] Tarmoq paketi va Handshake ushlanmoqda... ({delay_sec} soniya)")
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        steps = 25
        sleep_time = delay_sec / steps

        for i in range(1, steps + 1):
            percent = int((i / steps) * 100)
            filled = int((percent / 100) * 20)
            bar = "=" * filled + ">" + " " * (20 - filled)
            spin = spinners[i % len(spinners)]

            status_line = f"\r{COLOR_CYAN}{spin} [{bar}] {percent}% [Capturing EAPOL/WPA Handshake...]{COLOR_RESET}"
            sys.stdout.write(status_line)
            sys.stdout.flush()
            time.sleep(sleep_time)

        print("\n")

    def _get_groq_ai_hint(self, user_cmd: str) -> str:
        """Запрос к Groq API для генерации полнотекстовой подсказки."""
        if not self.api_key:
            return "Buyruq sintaksisini va joriy bosqichni tekshiring."

        state_desc = (
            f"Monitor mode: {'Yoqilgan (wlan0mon)' if self.state['monitor_mode'] else 'Yoqilmagan'}. "
            f"Handshake fayli: {'Mavjud (handshake.hc22000)' if self.state['handshake_captured'] else 'Ushlanmagan/Mavjud emas'}."
        )

        system_instruction = (
            "Siz CyberEdu.ai платформасининг киберхавфсизлик бўйича ИИ-устозисиз.\n"
            "ҚОИДАЛАР:\n"
            "1. Ўзбек тилида ТОЛИҚ, ТУГАЛЛАНГАН ва тушунарли 1-3 жумладан иборат маслаҳат беринг.\n"
            "2. ЖУМЛАНИ ЯРИМ ЙЎЛДА ТЎХТАТИБ ҚЎЙМАНГ! Фикрингизни охиригача етказинг.\n"
            "3. Фойдаланувчи киритган буйруқ нега ҳозирги тизим ҳолатига тўғри келмаслигини айтинг.\n"
            "4. ТЎҒРИ БУЙРУҚНИ ТЎЛИҚ ЁЗМАНГ, фақат кейинги логик қадамга ишора қилинг.\n"
            "5. 'AI:', '💡' каби префикслар ишлатманг."
        )

        user_content = (
            f"Тизим ҳолати: {state_desc}\n"
            f"Фойдаланувчи киритган буйруқ: {user_cmd}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.2,
            "max_tokens": 300
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=6)
            if response.status_code == 200:
                data = response.json()
                msg = data["choices"][0]["message"]
                raw_content = msg.get("content") or msg.get("reasoning") or ""
                cleaned = self._clean_ai_response(raw_content)
                if cleaned:
                    return cleaned
        except Exception:
            pass

        return "Ushbu buyruq joriy bosqichga mos kelmaydi. Buyruq nomini va parametrlarni tekshiring."

    def process_command(self, user_command: str) -> dict:
        clean_cmd = user_command.strip()

        if self.is_completed():
            return {"status": "completed", "output": "Kvest allaqachon muvaffaqiyatli yakunlangan!"}

        # 1. ls
        if clean_cmd == "ls" or clean_cmd.startswith("ls "):
            if self.state["handshake_captured"]:
                output = f"{COLOR_CYAN}handshake.hc22000{COLOR_RESET}  wordlist.txt"
                hint = "Fayllar mavjud. Endi Hashcat yordamida parolni buzishingiz mumkin."
            else:
                output = "wordlist.txt"
                hint = (
                    "Hozircha katalogda xesh fayli yo'q. Avval airmon-ng orqali monitor rejimini yoqing "
                    "va airodump-ng yordamida handshake ushlang."
                )

            return {
                "status": "info",
                "output": output,
                "hint": f"{COLOR_GREEN}{hint}{COLOR_RESET}",
                "next_instruction": self.get_current_instruction()
            }

        # 2. pwd, whoami, clear
        if clean_cmd == "pwd":
            return {"status": "info", "output": "/root/Desktop/Cyberedu.ai", "next_instruction": self.get_current_instruction()}
        if clean_cmd == "whoami":
            return {"status": "info", "output": "root", "next_instruction": self.get_current_instruction()}
        if clean_cmd == "clear":
            os.system("clear")
            return {"status": "info", "output": "", "next_instruction": self.get_current_instruction()}

        # 3. airmon-ng
        if "airmon-ng" in clean_cmd:
            if "start" in clean_cmd and ("wlan0" in clean_cmd or "wlan0mon" in clean_cmd):
                self.state["monitor_mode"] = True
                out = (
                    "PHY\tInterface\tDriver\t\tChipset\n"
                    "phy0\twlan0\t\tath9k\t\tQualcomm Atheros\n\n"
                    "(mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)\n"
                    "(mac80211 station mode vif disabled for [phy0]wlan0)"
                )
                return {
                    "status": "success",
                    "output": out,
                    "completed": False,
                    "next_instruction": self.get_current_instruction()
                }

        # 4. airodump-ng
        if "airodump-ng" in clean_cmd:
            if not self.state["monitor_mode"]:
                hint = "Tarmoq kartasi monitor rejimida emas! Avval airmon-ng yordamida monitor rejimini yoqing."
                return {
                    "status": "error",
                    "output": "bash: airodump-ng: ERROR: Interface wlan0 is not in monitor mode.",
                    "hint": f"{COLOR_GREEN}{hint}{COLOR_RESET}"
                }
            else:
                self._simulate_generic_scan(delay_sec=3)
                self.state["handshake_captured"] = True
                out = (
                    "[+] WPA Handshake ushlandi!\n"
                    "[+] Fayl saqlandi: handshake.hc22000"
                )
                return {
                    "status": "success",
                    "output": out,
                    "completed": False,
                    "next_instruction": self.get_current_instruction()
                }

        # 5. hashcat
        if "hashcat" in clean_cmd:
            if not self.state["handshake_captured"]:
                hint = "Katalogda 'handshake.hc22000' fayli topilmadi! Avval airodump-ng orqali trafikni ushlang."
                return {
                    "status": "error",
                    "output": "hashcat: No hash file found.",
                    "hint": f"{COLOR_GREEN}{hint}{COLOR_RESET}"
                }
            else:
                self._simulate_hashcat(delay_sec=4)
                self.state["cracked"] = True
                return {
                    "status": "success",
                    "output": "Kvest muvaffaqiyatli yakunlandi!",
                    "completed": True,
                    "next_instruction": None
                }

        # 6. Произвольная команда -> Запрос к ИИ
        ai_hint = self._get_groq_ai_hint(clean_cmd) if self.use_ai else "Buyruqni tekshiring."
        return {
            "status": "error",
            "output": f"bash: buyruq topilmadi yoki mantiqiy xato: '{clean_cmd}'",
            "hint": f"{COLOR_GREEN}{ai_hint}{COLOR_RESET}"
        }