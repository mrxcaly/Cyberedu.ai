import unittest
from engine import CyberGameEngine


class TestDefenseMode(unittest.TestCase):

    def setUp(self):
        """Инициализация движка в режиме защиты с отключенным ИИ для быстрых тестов."""
        self.engine = CyberGameEngine(mode="defense", use_ai=False)

    def test_initial_state(self):
        """1. Проверка начального состояния квеста."""
        self.assertFalse(self.engine.is_completed())
        self.assertFalse(self.engine.state["monitor_mode"])
        self.assertFalse(self.engine.state["attack_detected"])
        self.assertFalse(self.engine.state["hardened"])
        self.assertIn("airmon-ng", self.engine.get_current_instruction())

    def test_successful_defense_flow(self):
        """2. Проверка успешного прохождения всех этапов защиты."""
        # Шаг 1: Включение режим мониторинга
        res_mon = self.engine.process_command("airmon-ng start wlan0")
        self.assertEqual(res_mon["status"], "success")
        self.assertTrue(self.engine.state["monitor_mode"])
        self.assertIn("waidps", self.engine.get_current_instruction())

        # Шаг 2: Обнаружение Deauth-атаки через waidps
        res_scan = self.engine.process_command("waidps")
        self.assertEqual(res_scan["status"], "success")
        self.assertTrue(self.engine.state["attack_detected"])
        self.assertIn("802.11w", self.engine.get_current_instruction())

        # Шаг 3: Настройка hostapd / отключение WPS
        res_hard = self.engine.process_command("hostapd set pmf=1")
        self.assertEqual(res_hard["status"], "success")
        self.assertTrue(res_hard["completed"])
        self.assertTrue(self.engine.state["hardened"])
        self.assertTrue(self.engine.is_completed())

    def test_out_of_order_commands(self):
        """3. Проверка блокировки команд при нарушении порядка шагов."""
        # Попытка включить сканер до включения monitor mode
        res_scan_error = self.engine.process_command("waidps")
        self.assertEqual(res_scan_error["status"], "error")
        self.assertFalse(self.engine.state["attack_detected"])

        # Включаем monitor mode
        self.engine.process_command("airmon-ng start wlan0")

        # Попытка применить настройки hostapd до обнаружения атаки
        res_hard_error = self.engine.process_command("hostapd set pmf=1")
        self.assertEqual(res_hard_error["status"], "error")
        self.assertFalse(self.engine.state["hardened"])

    def test_unknown_command(self):
        """4. Проверка отклика на несуществующую команду."""
        res_unknown = self.engine.process_command("random_command_xyz")
        self.assertEqual(res_unknown["status"], "error")
        self.assertIn("buyruq topilmadi", res_unknown["output"])


if __name__ == "__main__":
    unittest.main()