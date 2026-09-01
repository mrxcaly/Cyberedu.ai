import os
import re
import sys
import time
import unicodedata

# ANSI-цвета Kali Linux
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_visible_len(text: str) -> int:
    """Точный расчет ширины символов для выравнивания рамок."""
    clean = re.sub(r'\033\[[0-9;]*m', '', text)
    length = 0
    for char in clean:
        if ord(char) == 0xFE0F:
            continue
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            length += 2
        elif ord(char) in [0x1F4CA, 0x2694, 0x1F6E1, 0x1F4A1]:
            length += 2
        else:
            length += 1
    return length


class Dashboard:
    def __init__(self, engine):
        self.engine = engine
        self.start_time = time.time()
        self.cmd_count = 0
        self.ai_hints_count = 0

    def increment_cmd(self, used_ai: bool = False):
        self.cmd_count += 1
        if used_ai:
            self.ai_hints_count += 1

    def render(self):
        """Отрисовка интерактивного дашборда на выбранном языке."""
        os.system("clear")
        elapsed = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed, 60)

        CONTENT_WIDTH = 62
        BOX_BORDER_LEN = CONTENT_WIDTH + 2

        def format_row(left: str = "", right: str = "") -> str:
            vis_l = get_visible_len(left)
            vis_r = get_visible_len(right)
            padding = CONTENT_WIDTH - vis_l - vis_r
            if padding < 0:
                padding = 0
            return f"{CYAN}{BOLD}│{RESET} {left}{' ' * padding}{right} {CYAN}{BOLD}│{RESET}"

        lang = self.engine.lang

        # Локализованный словарь слов
        labels = {
            "uz": {
                "title": "📊 CYBEREDU.AI - TIZIM DASHBOARDI",
                "mode": "Rejim:",
                "time": "Vaqt:",
                "iface": "Interfeys:",
                "ai": "AI Maslahatchi:",
                "progress": "KVEST PROGRESSI:",
                "stats": "STATISTIKA & MONITORING:",
                "cmds": "Bajarilgan buyruqlar:",
                "hints": "AI Maslahatlar soni:",
                "target": "Nishon / Freymlari:",
                "back": "Orqaga qaytish uchun [Enter] tugmasini bosing...",
                "active": "FAOL",
                "disabled": "OCHIQ",
                "attack": "⚔️  HUJUM (ATTACK)",
                "defense": "🛡️  HIMOYA (DEFENSE)",
                "captured": "Ushlangan",
                "waiting": "Kutilmoqda",
                "detected": "Aniqlandi"
            },
            "ru": {
                "title": "📊 CYBEREDU.AI - ПАНЕЛЬ МОНИТОРИНГА",
                "mode": "Режим:",
                "time": "Время:",
                "iface": "Интерфейс:",
                "ai": "ИИ-Помощник:",
                "progress": "ПРОГРЕСС КВЕСТА:",
                "stats": "СТАТИСТИКА И МОНИТОРИНГ:",
                "cmds": "Выполнено команд:",
                "hints": "Подсказок ИИ:",
                "target": "Цель / Фреймы:",
                "back": "Нажмите [Enter] для возврата...",
                "active": "ВКЛ (Groq)",
                "disabled": "ВЫКЛ",
                "attack": "⚔️  АТАКА (ATTACK)",
                "defense": "🛡️  ЗАЩИТА (DEFENSE)",
                "captured": "Захвачен",
                "waiting": "Ожидание",
                "detected": "Обнаружен"
            },
            "en": {
                "title": "📊 CYBEREDU.AI - SYSTEM DASHBOARD",
                "mode": "Mode:",
                "time": "Time:",
                "iface": "Interface:",
                "ai": "AI Advisor:",
                "progress": "QUEST PROGRESS:",
                "stats": "STATISTICS & MONITORING:",
                "cmds": "Executed commands:",
                "hints": "AI Hints count:",
                "target": "Target / Frames:",
                "back": "Press [Enter] to return...",
                "active": "ENABLED",
                "disabled": "DISABLED",
                "attack": "⚔️  ATTACK",
                "defense": "🛡️  DEFENSE",
                "captured": "Captured",
                "waiting": "Waiting",
                "detected": "Detected"
            }
        }[lang]

        mode_name = labels["attack"] if self.engine.mode == "attack" else labels["defense"]
        iface_status = "wlan0mon (Monitor)" if self.engine.state["monitor_mode"] else "wlan0 (Managed)"

        if self.engine.mode == "attack":
            target_status = labels["captured"] if self.engine.state["handshake_captured"] else labels["waiting"]
            progress_val = 0
            if self.engine.state["monitor_mode"]: progress_val = 33
            if self.engine.state["handshake_captured"]: progress_val = 66
            if self.engine.state["cracked"]: progress_val = 100
        else:
            target_status = labels["detected"] if self.engine.state["attack_detected"] else labels["waiting"]
            progress_val = 0
            if self.engine.state["monitor_mode"]: progress_val = 33
            if self.engine.state["attack_detected"]: progress_val = 66
            if self.engine.state["hardened"]: progress_val = 100

        filled_count = progress_val // 5
        empty_count = 20 - filled_count
        progress_bar_str = f"[{GREEN}{'█' * filled_count}{RESET}{'░' * empty_count}] {progress_val}%"

        ai_status = f"{GREEN}{labels['active']}{RESET}" if self.engine.use_ai else f"{RED}{labels['disabled']}{RESET}"

        # Отрисовка
        print(f"{CYAN}{BOLD}┌" + "─" * BOX_BORDER_LEN + f"┐{RESET}")
        print(format_row(f"{YELLOW}{BOLD}{labels['title']}{RESET}"))
        print(f"{CYAN}{BOLD}├" + "─" * BOX_BORDER_LEN + f"┤{RESET}")
        
        print(format_row(f"{BOLD}{labels['mode']}{RESET} {mode_name}", f"{BOLD}{labels['time']}{RESET} {minutes:02d}:{seconds:02d}"))
        print(format_row(f"{BOLD}{labels['iface']}{RESET} {iface_status}", f"{BOLD}{labels['ai']}{RESET} {ai_status}"))
        
        print(f"{CYAN}{BOLD}├" + "─" * BOX_BORDER_LEN + f"┤{RESET}")
        print(format_row(f"{BOLD}{labels['progress']}{RESET}"))
        print(format_row(progress_bar_str))
        
        print(f"{CYAN}{BOLD}├" + "─" * BOX_BORDER_LEN + f"┤{RESET}")
        print(format_row(f"{BOLD}{labels['stats']}{RESET}"))
        print(format_row(f"  • {labels['cmds']} {BOLD}{self.cmd_count}{RESET}"))
        print(format_row(f"  • {labels['hints']} {BOLD}{self.ai_hints_count}{RESET}"))
        print(format_row(f"  • {labels['target']} {BOLD}{target_status}{RESET}"))
        
        print(f"{CYAN}{BOLD}└" + "─" * BOX_BORDER_LEN + f"┘{RESET}\n")

        input(f"{YELLOW}{labels['back']}{RESET}")