from engine import CyberGameEngine

def main():
    try:
        engine = CyberGameEngine("quests/wpa2_crack.json")
    except Exception as e:
        print(f"Dvijokni yuklashda xatolik: {e}")
        return

    print(f"=== {engine.quest['title']} ===")
    print(engine.quest['description'])
    print("=" * 50)

    while not engine.is_completed():
        print(f"\n[Topshiriq]: {engine.get_current_instruction()}")
        user_input = input("root@kali:~# ")
        
        result = engine.process_command(user_input)
        print("\n" + result["output"])

        if result["status"] == "error":
            print(f"💡 [AI-Maslahat]: {result['hint']}")

    print("\n🎉 Tabriklaymiz! Barcha topshiriqlar muvaffaqiyatli bajarildi.")

if __name__ == "__main__":
    main()