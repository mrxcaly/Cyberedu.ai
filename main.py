import os
import sys
from engine import CyberGameEngine

# ANSI-цвета Kali Linux
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(title: str, description: str):
    """Вывод баннера с точным выравниванием рамок."""
    os.system("clear")
    
    INNER_WIDTH = 66
    CONTENT_WIDTH = INNER_WIDTH - 2

    print(f"{CYAN}{BOLD}┌" + "─" * INNER_WIDTH + f"┐{RESET}")
    
    formatted_title = f"{title:<{CONTENT_WIDTH}}"
    print(f"{CYAN}{BOLD}│ {YELLOW}{formatted_title}{CYAN}{BOLD} │{RESET}")
    
    print(f"{CYAN}{BOLD}├" + "─" * INNER_WIDTH + f"┤{RESET}")

    words = description.split()
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= CONTENT_WIDTH:
            current_line += (" " if current_line else "") + word
        else:
            formatted_line = f"{current_line:<{CONTENT_WIDTH}}"
            print(f"{CYAN}{BOLD}│ {RESET}{formatted_line}{CYAN}{BOLD} │{RESET}")
            current_line = word

    if current_line:
        formatted_line = f"{current_line:<{CONTENT_WIDTH}}"
        print(f"{CYAN}{BOLD}│ {RESET}{formatted_line}{CYAN}{BOLD} │{RESET}")

    print(f"{CYAN}{BOLD}└" + "─" * INNER_WIDTH + f"┘{RESET}")


def show_mode_selection() -> str:
    """Стартовое меню выбора режима лабораторной работы."""
    os.system("clear")
    print(f"{CYAN}{BOLD}===================================================={RESET}")
    print(f"{YELLOW}{BOLD}          CYBEREDU.AI - WI-FI LAB REJIMLARI         {RESET}")
    print(f"{CYAN}{BOLD}===================================================={RESET}\n")
    print(f"{BOLD}[1]{RESET} ⚔️  {YELLOW}{BOLD}Wi-Fi Hujum (Attack Mode){RESET}")
    print(f"    WPA2 Handshake ushlash va Hashcat orqali brutforz qilish.\n")
    print(f"{BOLD}[2]{RESET} 🛡️  {GREEN}{BOLD}Wi-Fi Himoya (Defense Mode){RESET}")
    print(f"    Deauth hujumlarini aniqlash, WPS'ni yopish va PMF (802.11w) yoqish.\n")

    while True:
        try:
            choice = input(f"{CYAN}{BOLD}Rejimni tanlang (1 yoki 2): {RESET}").strip()
            if choice == "1":
                return "attack"
            elif choice == "2":
                return "defense"
            print(f"{YELLOW}Iltimos, faqat 1 yoki 2 raqamini kiriting.{RESET}")
        except (KeyboardInterrupt, EOFError):
            print("\n\nChiqish...")
            sys.exit(0)


def get_kali_prompt() -> str:
    """Генерация двухстрочного промпта Kali Linux Zsh."""
    line1 = f"{GREEN}┌──({BLUE}{BOLD}root㉿kali{RESET}{GREEN})-[{RESET}{CYAN}~{RESET}{GREEN}]{RESET}\n"
    line2 = f"{GREEN}└─{BLUE}{BOLD}${RESET} "
    return line1 + line2


def main():
    # 1. Запрос выбора режима
    mode = show_mode_selection()

    # 2. Запуск движка в выбранном режиме
    engine = CyberGameEngine(mode=mode)
    print_banner(engine.quest["title"], engine.quest["description"])

    while not engine.is_completed():
        instruction = engine.get_current_instruction()
        
        # Отступ сверху и снизу для блока [Topshiriq]
        print()
        print(f"{BOLD}{YELLOW}[Topshiriq]:{RESET} {instruction}")
        print()

        try:
            cmd = input(get_kali_prompt())
        except (KeyboardInterrupt, EOFError):
            print("\n\nChiqish...")
            break

        if not cmd.strip():
            continue

        res = engine.process_command(cmd)

        # Вывод результата выполнения команды
        if res.get("output"):
            print()
            print(res["output"])

        # Вывод подсказки ИИ
        if res.get("hint"):
            print()
            print(f"💡 [AI-Maslahat]: {res['hint']}")

        if res.get("completed"):
            print(f"\n{GREEN}{BOLD}🎉 Табриклаймиз! Квест муваффақиятли якунланди!{RESET}\n")
            break


if __name__ == "__main__":
    main()