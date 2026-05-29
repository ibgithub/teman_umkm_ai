import unittest
from typing import Any

from agent import TemanUmkmAgent


class FakeTemanUmkmClient:
    def __init__(self) -> None:
        self.products = [
            {"id": 1, "name": "Kopi", "sellingPrice": 10000},
            {"id": 2, "name": "Gula", "sellingPrice": 5000},
            {"id": 3, "name": "Teh", "sellingPrice": 7000},
            {"id": 4, "name": "Ayam Geprek", "sellingPrice": 12000},
            {"id": 5, "name": "Ayam Bakar", "sellingPrice": 13000},
        ]
        self.created_sales: list[dict[str, Any]] = []

    def get_merchants(self) -> list[dict[str, Any]]:
        return [{"id": 10}]

    def get_outlets(self, merchant_id: int) -> list[dict[str, Any]]:
        return [{"id": 20, "merchantId": merchant_id}]

    def get_products(self, merchant_id: int) -> list[dict[str, Any]]:
        return self.products

    def create_sale(
        self,
        merchant_id: int,
        outlet_id: int,
        payment_method: str,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sale = {
            "id": 99,
            "merchantId": merchant_id,
            "outletId": outlet_id,
            "paymentMethod": payment_method,
            "items": items,
        }
        self.created_sales.append(sale)
        return sale


class AgentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeTemanUmkmClient()
        self.agent = TemanUmkmAgent(self.client)

    def test_process_multi_item_order_adds_items_to_cart(self) -> None:
        response = self.agent.process("Saya mau beli kopi dan gula")

        self.assertIn("Berhasil menambahkan", response)
        self.assertIn("- Kopi x1", response)
        self.assertIn("- Gula x1", response)
        self.assertEqual(
            [(item.product_name, item.qty) for item in self.agent.cart.items],
            [("Kopi", 1), ("Gula", 1)],
        )
        self.assertEqual(self.agent.cart.subtotal, 15000)

    def test_process_multi_item_order_with_quantities(self) -> None:
        self.agent.process("beli 2 kopi, 1 gula, 3 teh")

        self.assertEqual(
            [(item.product_name, item.qty) for item in self.agent.cart.items],
            [("Kopi", 2), ("Gula", 1), ("Teh", 3)],
        )
        self.assertEqual(self.agent.cart.subtotal, 46000)

    def test_process_multi_item_order_continues_when_product_not_found(self) -> None:
        response = self.agent.process("beli kopi, sabun, dan gula")

        self.assertIn("Berhasil menambahkan", response)
        self.assertIn("- Kopi x1", response)
        self.assertIn("- Gula x1", response)
        self.assertIn("Produk tidak ditemukan", response)
        self.assertIn("- sabun", response)
        self.assertEqual(
            [(item.product_name, item.qty) for item in self.agent.cart.items],
            [("Kopi", 1), ("Gula", 1)],
        )
        self.assertEqual(self.agent.cart.subtotal, 15000)

    def test_process_single_missing_product_uses_simple_not_found_response(self) -> None:
        response = self.agent.process("beli sabun")

        self.assertEqual(response, "AI: Produk 'sabun' tidak ditemukan.")
        self.assertTrue(self.agent.cart.is_empty())

    def test_process_multi_item_order_when_all_products_not_found(self) -> None:
        response = self.agent.process("beli sabun dan sampo")

        self.assertIn("Berhasil menambahkan", response)
        self.assertIn("- Tidak ada", response)
        self.assertIn("Produk tidak ditemukan", response)
        self.assertIn("- sabun", response)
        self.assertIn("- sampo", response)
        self.assertIn("- Cart masih kosong", response)
        self.assertTrue(self.agent.cart.is_empty())

    def test_process_ambiguous_item_then_continues_remaining_order(self) -> None:
        first_response = self.agent.process("Saya mau beli ayam dan gula")

        self.assertIn("Ayam Geprek", first_response)
        self.assertIn("Ayam Bakar", first_response)
        self.assertIsNotNone(self.agent.pending_action)
        self.assertEqual(len(self.agent.cart.items), 0)

        second_response = self.agent.process("geprek")

        self.assertIn("Produk: Ayam Geprek", second_response)
        self.assertIn("- Gula x1", second_response)
        self.assertIsNone(self.agent.pending_action)
        self.assertEqual(
            [(item.product_name, item.qty) for item in self.agent.cart.items],
            [("Ayam Geprek", 1), ("Gula", 1)],
        )

    def test_process_ambiguous_item_then_continues_remaining_order_with_missing_product(
        self,
    ) -> None:
        first_response = self.agent.process("Saya mau beli ayam, sabun, dan gula")

        self.assertIn("Ayam Geprek", first_response)
        self.assertIn("Ayam Bakar", first_response)
        self.assertIsNotNone(self.agent.pending_action)

        second_response = self.agent.process("bakar")

        self.assertIn("Produk: Ayam Bakar", second_response)
        self.assertIn("- Gula x1", second_response)
        self.assertIn("Produk tidak ditemukan", second_response)
        self.assertIn("- sabun", second_response)
        self.assertIsNone(self.agent.pending_action)
        self.assertEqual(
            [(item.product_name, item.qty) for item in self.agent.cart.items],
            [("Ayam Bakar", 1), ("Gula", 1)],
        )

    def test_checkout_creates_sale_and_clears_cart(self) -> None:
        self.agent.process("beli kopi dan gula")
        response = self.agent.process("bayar cash 20000")

        self.assertIn("Pembayaran berhasil", response)
        self.assertTrue(self.agent.cart.is_empty())
        self.assertEqual(len(self.client.created_sales), 1)
        self.assertEqual(
            self.client.created_sales[0]["items"],
            [
                {"productId": 1, "productName": "Kopi", "qty": 1, "price": 10000},
                {"productId": 2, "productName": "Gula", "qty": 1, "price": 5000},
            ],
        )


if __name__ == "__main__":
    unittest.main()
