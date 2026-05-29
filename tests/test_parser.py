import unittest

from parser import AddItemCommand, MultiCommand, parse_user_message


class ParserTest(unittest.TestCase):
    def test_parse_single_natural_order(self) -> None:
        command = parse_user_message("beli kopi")

        self.assertIsInstance(command, AddItemCommand)
        self.assertEqual(command.qty, 1)
        self.assertEqual(command.product_keyword, "kopi")

    def test_parse_multi_natural_order(self) -> None:
        command = parse_user_message("Saya mau beli kopi dan gula")

        self.assertIsInstance(command, MultiCommand)
        self.assertEqual(
            [(item.qty, item.product_keyword) for item in command.commands],
            [(1, "kopi"), (1, "gula")],
        )

    def test_parse_multi_natural_order_with_quantities(self) -> None:
        command = parse_user_message("beli 2 kopi dan 1 gula")

        self.assertIsInstance(command, MultiCommand)
        self.assertEqual(
            [(item.qty, item.product_keyword) for item in command.commands],
            [(2, "kopi"), (1, "gula")],
        )

    def test_parse_multi_natural_order_with_sama_separator(self) -> None:
        command = parse_user_message("beli kopi sama gula")

        self.assertIsInstance(command, MultiCommand)
        self.assertEqual(
            [(item.qty, item.product_keyword) for item in command.commands],
            [(1, "kopi"), (1, "gula")],
        )

    def test_parse_multi_natural_order_with_comma_and_dan(self) -> None:
        command = parse_user_message("beli kopi, gula, dan teh")

        self.assertIsInstance(command, MultiCommand)
        self.assertEqual(
            [(item.qty, item.product_keyword) for item in command.commands],
            [(1, "kopi"), (1, "gula"), (1, "teh")],
        )

    def test_parse_multi_natural_order_with_trailing_quantities(self) -> None:
        command = parse_user_message("beli kopi 2 dan gula 1")

        self.assertIsInstance(command, MultiCommand)
        self.assertEqual(
            [(item.qty, item.product_keyword) for item in command.commands],
            [(2, "kopi"), (1, "gula")],
        )

    def test_parse_multi_natural_order_with_comma_quantities(self) -> None:
        command = parse_user_message("beli 2 kopi, 1 gula, 3 teh")

        self.assertIsInstance(command, MultiCommand)
        self.assertEqual(
            [(item.qty, item.product_keyword) for item in command.commands],
            [(2, "kopi"), (1, "gula"), (3, "teh")],
        )

    def test_parse_explicit_add_without_quantity(self) -> None:
        command = parse_user_message("tambah kopi")

        self.assertIsInstance(command, AddItemCommand)
        self.assertEqual(command.qty, 1)
        self.assertEqual(command.product_keyword, "kopi")


if __name__ == "__main__":
    unittest.main()
