import os
import sys
from engine import CyberGameEngine
from dashboard import Dashboard

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(title: str, description: str):
    """Отрисовка верхушки квеста в Kali-стиле."""
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
    """Выбор режима при запуске."""
    os.system("clear")
    print(f"{CYAN}{BOLD}===================================================={RESET}")
    print(f"{YELLOW}{BOLD}          CYBEREDU.AI - WI-FI LAB REJIMLARI         {RESET}")
    print(f"{CYAN}{BOLD}===================================================={RESET}\n")
    print(f"{BOLD}[1]{RESET} ⚔️  {YELLOW}{BOLD}Wi-Fi Hujum (Attack Mode){RESET}")
    print(f"    WPA2 Handshake ushlash va Hashcat orqali brutforz qilish.\n")
    print(f"{BOLD}[2]{RESET} 🛡️  {GREEN}{BOLD}Wi-Fi Himoya (Defense Mode){RESET}")
    print(f"    Deauth hujumlarini aniqlash, WPS'ni yopish va PMF yoqish.\n")

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
    """Промпт Kali Zsh."""
    line1 = f"{GREEN}┌──({BLUE}{BOLD}root㉿kali{RESET}{GREEN})-[{RESET}{CYAN}~{RESET}{GREEN}]{RESET}\n"
    line2 = f"{GREEN}└─{BLUE}{BOLD}${RESET} "
    return line1 + line2


def main():
    mode = show_mode_selection()
    engine = CyberGameEngine(mode=mode, lang="uz")
    dashboard = Dashboard(engine)

    print_banner(engine.quest["title"], engine.quest["description"])

    while not engine.is_completed():
        instruction = engine.get_current_instruction()

        print()
        print(f"{BOLD}{YELLOW}[Topshiriq / Задание]:{RESET} {instruction}")
        print()

        try:
            cmd = input(get_kali_prompt())
        except (KeyboardInterrupt, EOFError):
            print("\n\nChiqish...")
            break

        clean_cmd = cmd.strip()
        if not clean_cmd:
            continue

        if clean_cmd.lower() in ["exit", "quit"]:
            print("\nChiqish...")
            break

        # Команда открытия дашборда
        if clean_cmd.lower() in ["dashboard", "stats"]:
            dashboard.render()
            print_banner(engine.quest["title"], engine.quest["description"])
            continue

        # Обработка команды через движок
        res = engine.process_command(clean_cmd)

        # Вывод результатов
        if res.get("output"):
            print()
            print(res["output"])

        if res.get("hint"):
            print()
            print(f"💡 [AI-Maslahat]: {res['hint']}")

        # Если сменили язык, перерисовываем баннер с новым языком
        if clean_cmd.lower().startswith("language") or clean_cmd.lower().startswith("lang"):
            print_banner(engine.quest["title"], engine.quest["description"])

        # Обновление статистики вызовов
        dashboard.increment_cmd(used_ai=bool(res.get("hint")))

        if res.get("completed"):
            print(f"\n{GREEN}{BOLD}🎉 Табриклаймиз! Квест муваффақиятли якунланди!{RESET}\n")
            break


if __name__ == "__main__":
    main()