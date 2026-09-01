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


def get_kali_prompt() -> str:
    """Генерация двухстрочного промпта Kali Linux Zsh."""
    line1 = f"{GREEN}┌──({BLUE}{BOLD}root㉿kali{RESET}{GREEN})-[{RESET}{CYAN}~{RESET}{GREEN}]{RESET}\n"
    line2 = f"{GREEN}└─{BLUE}{BOLD}${RESET} "
    return line1 + line2


def main():
    engine = CyberGameEngine()
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