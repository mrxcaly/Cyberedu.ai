import json
import os
import re
import random
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ANSI-цвета Kali Linux
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


class CyberGameEngine:
    def __init__(self, mode: str = "attack", lang: str = "uz", quest_filepath: str = None, use_ai: bool = True):
        self.mode = mode.lower()
        self.lang = lang.lower() if lang.lower() in ["uz", "ru", "en"] else "uz"
        self.use_ai = use_ai
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # Состояние игровой системы
        if self.mode == "attack":
            self.state = {
                "monitor_mode": False,
                "handshake_captured": False,
                "cracked": False
            }
        else:
            self.state = {
                "monitor_mode": False,
                "attack_detected": False,
                "hardened": False
            }

    def get_quest_info(self) -> dict:
        """Получение названий и описаний квеста в зависимости от языка."""
        info = {
            "attack": {
                "uz": {
                    "title": "WPA2 Handshake & Hashcat Brute-Force (Hujum)",
                    "description": "WPA2 tarmog'ini buzish: tarmoq kartasini monitoring rejimiga o'tkazish, handshake ushlash va Hashcat orqali parolni topish."
                },
                "ru": {
                    "title": "WPA2 Handshake & Hashcat Brute-Force (Атака)",
                    "description": "Взлом сети WPA2: переключение карты в режим мониторинга, перехват handshake и подбор пароля через Hashcat."
                },
                "en": {
                    "title": "WPA2 Handshake & Hashcat Brute-Force (Attack)",
                    "description": "Cracking WPA2 network: switch card to monitor mode, capture handshake, and crack password via Hashcat."
                }
            },
            "defense": {
                "uz": {
                    "title": "Wi-Fi Tarmog'ini Himoyalash va Deauth-Detection (Himoya)",
                    "description": "Tarmoqqa bo'layotgan Deauth hujumini aniqlash, WPS zayıfligini yopish va 802.11w (PMF) xavfsizlik standartini yoqish."
                },
                "ru": {
                    "title": "Защита Wi-Fi сети и Deauth-Detection (Защита)",
                    "description": "Обнаружение Deauth-атаки на сеть, закрытие уязвимости WPS и включение стандарта безопасности 802.11w (PMF)."
                },
                "en": {
                    "title": "Wi-Fi Protection & Deauth-Detection (Defense)",
                    "description": "Detecting Deauth attack on network, closing WPS vulnerability, and enabling 802.11w (PMF) security standard."
                }
            }
        }
        return info[self.mode][self.lang]

    @property
    def quest(self) -> dict:
        return self.get_quest_info()

    def get_current_instruction(self) -> str:
        """Динамическое вычисление текущей цели с локализацией."""
        instructions = {
            "attack": {
                "uz": [
                    "Kvest muvaffaqiyatli yakunlandi! WPA2 paroli topildi.",
                    "wlan0 tarmoq kartasida monitor rejimini yoqing (airmon-ng).",
                    "Atrofdagi tarmoqlarni skanerlang va WPA2 handshake ushlang (airodump-ng).",
                    "Ushlangan handshake faylini Hashcat yordamida brutforz qiling."
                ],
                "ru": [
                    "Квест успешно завершен! Пароль WPA2 найден.",
                    "Включите режим мониторинга на сетевой карте wlan0 (airmon-ng).",
                    "Захватите WPA2 handshake, сканируя окружающие сети (airodump-ng).",
                    "Выполните брутфорс захваченного хэш-файла с помощью Hashcat."
                ],
                "en": [
                    "Quest completed successfully! WPA2 password found.",
                    "Enable monitor mode on the wlan0 network card (airmon-ng).",
                    "Scan surrounding networks and capture WPA2 handshake (airodump-ng).",
                    "Bruteforce the captured handshake file using Hashcat."
                ]
            },
            "defense": {
                "uz": [
                    "Kvest muvaffaqiyatli yakunlandi! Tarmoq Deauth va WPS hujumlaridan himoyalandi.",
                    "wlan0 tarmoq kartasida monitor rejimini yoqing (airmon-ng).",
                    "Tarmoqdagi Deauth hujumlarini va shubhali paketlarni aniqlang (waidps yoki tshark).",
                    "WPS funksiyasini o'chiring va 802.11w (PMF) himoyasini yoqing (wps_cli yoki hostapd)."
                ],
                "ru": [
                    "Квест успешно завершен! Сеть защищена от Deauth и WPS атак.",
                    "Включите режим мониторинга на сетевой карте wlan0 (airmon-ng).",
                    "Обнаружьте Deauth-атаки и подозрительные пакеты в сети (waidps или tshark).",
                    "Отключите WPS и включите защиту 802.11w (PMF) (wps_cli или hostapd)."
                ],
                "en": [
                    "Quest completed successfully! Network protected against Deauth and WPS attacks.",
                    "Enable monitor mode on the wlan0 network card (airmon-ng).",
                    "Detect Deauth attacks and suspicious packets in the network (waidps or tshark).",
                    "Disable WPS and enable 802.11w (PMF) protection (wps_cli or hostapd)."
                ]
            }
        }

        lang_inst = instructions[self.mode][self.lang]
        if self.mode == "attack":
            if self.state["cracked"]:
                return lang_inst[0]
            elif not self.state["monitor_mode"]:
                return lang_inst[1]
            elif not self.state["handshake_captured"]:
                return lang_inst[2]
            else:
                return lang_inst[3]
        else:
            if self.state["hardened"]:
                return lang_inst[0]
            elif not self.state["monitor_mode"]:
                return lang_inst[1]
            elif not self.state["attack_detected"]:
                return lang_inst[2]
            else:
                return lang_inst[3]

    def get_help_text(self) -> str:
        """Справка по командам системы."""
        if self.lang == "ru":
            return (
                f"{COLOR_CYAN}{COLOR_BOLD}📋 СПРАВКА ПО КОМАНДАМ ТЕРМИНАЛА:{COLOR_RESET}\n"
                f"  {COLOR_YELLOW}help / ?{COLOR_RESET}                     - Показать это меню помощи\n"
                f"  {COLOR_YELLOW}ai -on / ai -off{COLOR_RESET}             - Включить / Отключить подсказки Groq ИИ\n"
                f"  {COLOR_YELLOW}dashboard / stats{COLOR_RESET}            - Открыть интерактивную панель статистики\n"
                f"  {COLOR_YELLOW}language -uzb / -rus / -eng{COLOR_RESET} - Сменить язык системы (O'zbek / Русский / English)\n"
                f"  {COLOR_YELLOW}clear{COLOR_RESET}                        - Очистить экран терминала\n"
                f"  {COLOR_YELLOW}exit{COLOR_RESET}                         - Выйти из тренажёра"
            )
        elif self.lang == "en":
            return (
                f"{COLOR_CYAN}{COLOR_BOLD}📋 TERMINAL COMMAND HELP:{COLOR_RESET}\n"
                f"  {COLOR_YELLOW}help / ?{COLOR_RESET}                     - Show this help menu\n"
                f"  {COLOR_YELLOW}ai -on / ai -off{COLOR_RESET}             - Enable / Disable Groq AI hints\n"
                f"  {COLOR_YELLOW}dashboard / stats{COLOR_RESET}            - Open interactive stats dashboard\n"
                f"  {COLOR_YELLOW}language -uzb / -rus / -eng{COLOR_RESET} - Change language (O'zbek / Русский / English)\n"
                f"  {COLOR_YELLOW}clear{COLOR_RESET}                        - Clear terminal screen\n"
                f"  {COLOR_YELLOW}exit{COLOR_RESET}                         - Exit the simulator"
            )
        else:
            return (
                f"{COLOR_CYAN}{COLOR_BOLD}📋 TERMINAL BUYRUQLARI BO'YICHA YORDAM:{COLOR_RESET}\n"
                f"  {COLOR_YELLOW}help / ?{COLOR_RESET}                     - Ushbu yordam menyusini ko'rsatish\n"
                f"  {COLOR_YELLOW}ai -on / ai -off{COLOR_RESET}             - Groq AI maslahatlarini yoqish / o'chirish\n"
                f"  {COLOR_YELLOW}dashboard / stats{COLOR_RESET}            - Statistikani va interaktiv panelni ochish\n"
                f"  {COLOR_YELLOW}language -uzb / -rus / -eng{COLOR_RESET} - Tilni o'zgartirish (O'zbek / Русский / English)\n"
                f"  {COLOR_YELLOW}clear{COLOR_RESET}                        - Terminal ekranini tozalash\n"
                f"  {COLOR_YELLOW}exit{COLOR_RESET}                         - Trenajyordan chiqish"
            )

    def is_completed(self) -> bool:
        return self.state["cracked"] if self.mode == "attack" else self.state["hardened"]

    def _clean_ai_response(self, text: str) -> str:
        if not text:
            return ""
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
        return re.sub(r'^💡\s*', '', result).strip('"`\' ')

    def _simulate_hashcat(self, delay_sec: int = 4):
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

        candidates = ["12345678", "password", "qwerty123", "admin2024", "iloveyou", "dragon123", "sunshine", "supersecret123"]
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

    def _simulate_deauth_detection(self, delay_sec: int = 3):
        print(f"\n[*] Tarmoq efiri tahlil qilinmoqda... ({delay_sec}s)")
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        steps = 25
        sleep_time = delay_sec / steps

        for i in range(1, steps + 1):
            percent = int((i / steps) * 100)
            filled = int((percent / 100) * 20)
            bar = "=" * filled + ">" + " " * (20 - filled)
            spin = spinners[i % len(spinners)]
            status_line = f"\r{COLOR_CYAN}{spin} [{bar}] {percent}% [Analyzing Management Frames...]{COLOR_RESET}"
            sys.stdout.write(status_line)
            sys.stdout.flush()
            time.sleep(sleep_time)
        print("\n")

    def _simulate_generic_scan(self, delay_sec: int = 3):
        print(f"\n[*] Scanning packets... ({delay_sec}s)")
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
        if not self.use_ai:
            return ""
        if not self.api_key:
            return "API Key topilmadi." if self.lang == "uz" else ("API ключ не найден." if self.lang == "ru" else "API key missing.")

        lang_instructions = {
            "uz": "Ўзбек тилида ТОЛИҚ, ТУГАЛЛАНГАН ва тушунарли 1-3 жумладан иборат маслаҳат беринг.",
            "ru": "Дайте ПОЛНЫЙ, ЗАВЕРШЕННЫЙ и понятный совет из 1-3 предложений НА РУССКОМ ЯЗЫКЕ.",
            "en": "Give a COMPLETE, FINISHED, and clear hint of 1-3 sentences IN ENGLISH."
        }

        system_instruction = (
            f"Siz CyberEdu.ai platformasining ИИ-устозисиз.\n"
            f"ҚОИДАЛАР:\n"
            f"1. {lang_instructions[self.lang]}\n"
            "2. Фикрингизни охиригача етказинг.\n"
            "3. Фойдаланувчи киритган буйруқ нега ҳозирги тизим ҳолатига тўғри келмаслигини айтинг.\n"
            "4. ТЎҒРИ БУЙРУҚНИ ТЎЛИҚ ЁЗМАНГ, фақат кейинги логик қадамга ишора қилинг.\n"
            "5. 'AI:', '💡' каби префикслар ишлатманг."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Цель: {self.get_current_instruction()}\nВведённая команда: {user_cmd}"}
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

        default_hints = {
            "uz": "Buyruq sintaksisini va joriy bosqichni tekshiring.",
            "ru": "Проверьте синтаксис команды и текущий этап задания.",
            "en": "Check command syntax and current step."
        }
        return default_hints[self.lang]

    def process_command(self, user_command: str) -> dict:
        clean_cmd = user_command.strip()
        lower_cmd = clean_cmd.lower()

        if self.is_completed():
            return {"status": "completed", "output": "Kvest allaqachon muvaffaqiyatli yakunlangan!"}

        # 1. Справка HELP
        if lower_cmd in ["help", "?", "-h"]:
            return {
                "status": "info",
                "output": self.get_help_text(),
                "next_instruction": self.get_current_instruction()
            }

        # 2. Переключение ИИ (ai -on / ai -off)
        if lower_cmd in ["ai -on", "ai-on"]:
            self.use_ai = True
            msg = {"uz": "[+] Groq AI maslahatchisi YOQILDI.", "ru": "[+] Подсказки Groq ИИ ВКЛЮЧЕНЫ.", "en": "[+] Groq AI hints ENABLED."}
            return {"status": "info", "output": f"{COLOR_GREEN}{msg[self.lang]}{COLOR_RESET}"}
        
        if lower_cmd in ["ai -off", "ai-off"]:
            self.use_ai = False
            msg = {"uz": "[-] Groq AI maslahatchisi O'CHIRILDI.", "ru": "[-] Подсказки Groq ИИ ОТКЛЮЧЕНЫ.", "en": "[-] Groq AI hints DISABLED."}
            return {"status": "info", "output": f"{COLOR_YELLOW}{msg[self.lang]}{COLOR_RESET}"}

        # 3. Переключение языка (language -uzb / -rus / -eng)
        if lower_cmd in ["language -uzb", "language -uz", "lang -uzb", "lang -uz"]:
            self.lang = "uz"
            return {"status": "info", "output": f"{COLOR_GREEN}[+] Til O'zbek tiliga o'zgartirildi.{COLOR_RESET}"}
        if lower_cmd in ["language -rus", "language -ru", "lang -rus", "lang -ru"]:
            self.lang = "ru"
            return {"status": "info", "output": f"{COLOR_GREEN}[+] Язык успешно изменён на Русский.{COLOR_RESET}"}
        if lower_cmd in ["language -eng", "language -en", "lang -eng", "lang -en"]:
            self.lang = "en"
            return {"status": "info", "output": f"{COLOR_GREEN}[+] Language changed to English.{COLOR_RESET}"}

        # 4. Стандартные системные команды
        if clean_cmd == "pwd":
            return {"status": "info", "output": "/root/Desktop/Cyberedu.ai", "next_instruction": self.get_current_instruction()}
        if clean_cmd == "whoami":
            return {"status": "info", "output": "root", "next_instruction": self.get_current_instruction()}
        if clean_cmd == "clear":
            os.system("clear")
            return {"status": "info", "output": "", "next_instruction": self.get_current_instruction()}

        # 5. Логика АТАКИ
        if self.mode == "attack":
            if clean_cmd == "ls" or clean_cmd.startswith("ls "):
                output = f"{COLOR_CYAN}handshake.hc22000{COLOR_RESET}  wordlist.txt" if self.state["handshake_captured"] else "wordlist.txt"
                return {"status": "info", "output": output, "next_instruction": self.get_current_instruction()}

            if "airmon-ng" in clean_cmd and "start" in clean_cmd:
                self.state["monitor_mode"] = True
                out = "mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon"
                return {"status": "success", "output": out, "completed": False, "next_instruction": self.get_current_instruction()}

            if "airodump-ng" in clean_cmd:
                if not self.state["monitor_mode"]:
                    err = {"uz": "Interface wlan0 is not in monitor mode.", "ru": "Интерфейс wlan0 не в режиме мониторинга.", "en": "Interface wlan0 is not in monitor mode."}
                    return {"status": "error", "output": f"ERROR: {err[self.lang]}", "hint": self._get_groq_ai_hint(clean_cmd)}
                else:
                    self._simulate_generic_scan(delay_sec=3)
                    self.state["handshake_captured"] = True
                    out = "[+] WPA Handshake ushlandi! Saqlandi: handshake.hc22000"
                    return {"status": "success", "output": out, "completed": False, "next_instruction": self.get_current_instruction()}

            if "hashcat" in clean_cmd:
                if not self.state["handshake_captured"]:
                    return {"status": "error", "output": "hashcat: No hash file found.", "hint": self._get_groq_ai_hint(clean_cmd)}
                else:
                    self._simulate_hashcat(delay_sec=4)
                    self.state["cracked"] = True
                    return {"status": "success", "output": "Kvest muvaffaqiyatli yakunlandi!", "completed": True}

        # 6. Логика ЗАЩИТЫ
        else:
            if clean_cmd == "ls" or clean_cmd.startswith("ls "):
                return {"status": "info", "output": "hostapd.conf  waidps.py  rules.json", "next_instruction": self.get_current_instruction()}

            if "airmon-ng" in clean_cmd and "start" in clean_cmd:
                self.state["monitor_mode"] = True
                out = "(mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)"
                return {"status": "success", "output": out, "completed": False, "next_instruction": self.get_current_instruction()}

            if "waidps" in clean_cmd or "tshark" in clean_cmd:
                if not self.state["monitor_mode"]:
                    return {"status": "error", "output": "ERROR: Interface wlan0 is not in monitor mode.", "hint": self._get_groq_ai_hint(clean_cmd)}
                else:
                    self._simulate_deauth_detection(delay_sec=3)
                    self.state["attack_detected"] = True
                    out = f"{COLOR_RED}[!] Deauth Attack aniqlandi! BSSID: AA:BB:CC:DD:EE:FF{COLOR_RESET}"
                    return {"status": "success", "output": out, "completed": False, "next_instruction": self.get_current_instruction()}

            if "wps_cli" in clean_cmd or "hostapd" in clean_cmd or "pmf" in clean_cmd.lower():
                if not self.state["attack_detected"]:
                    return {"status": "error", "output": "Xatolik: Hujum aniqlanmagan.", "hint": self._get_groq_ai_hint(clean_cmd)}
                else:
                    self.state["hardened"] = True
                    out = f"{COLOR_GREEN}[+] WPS O'chirildi! 802.11w (PMF) Yoqildi!{COLOR_RESET}"
                    return {"status": "success", "output": out, "completed": True}

        ai_hint = self._get_groq_ai_hint(clean_cmd)
        return {
            "status": "error",
            "output": f"bash: buyruq topilmadi: '{clean_cmd}'",
            "hint": f"{COLOR_GREEN}{ai_hint}{COLOR_RESET}" if ai_hint else ""
        }