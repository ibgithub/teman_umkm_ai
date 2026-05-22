from __future__ import annotations

from typing import Any

from cart import CartItem, CartSession


class TemanUmkmLlm:
    """Response layer. Replace this class later when using a real LLM API."""

    def unknown_command(self) -> str:
        return (
            "AI: Saya belum mengerti. Coba ketik: tambah 2 kopi, cart, "
            "hapus kopi, clear cart, atau bayar cash 50000."
        )

    def merchant_not_found(self) -> str:
        return "AI: Merchant tidak ditemukan."

    def outlet_not_found(self) -> str:
        return "AI: Outlet tidak ditemukan."

    def product_not_found(self, keyword: str) -> str:
        return f"AI: Produk '{keyword}' tidak ditemukan."

    def last_product_not_found(self) -> str:
        return "AI: Saya belum tahu produk terakhirnya. Coba ketik: tambah 1 kopi."

    def clarify_product(self, candidates: list[dict[str, Any]]) -> str:
        lines = ["AI: Saya menemukan beberapa produk:"]

        for index, product in enumerate(candidates, start=1):
            lines.append(f"{index}. {product['name']}")

        lines.append("")
        lines.append("Mau yang mana? Balas dengan nomor atau nama produk.")
        return "\n".join(lines)

    def clarification_not_found(self, candidates: list[dict[str, Any]]) -> str:
        lines = ["AI: Saya belum bisa menentukan pilihan itu. Pilih salah satu:"]

        for index, product in enumerate(candidates, start=1):
            lines.append(f"{index}. {product['name']}")

        return "\n".join(lines)

    def item_added(self, item: CartItem, subtotal: int | float) -> str:
        return (
            "AI:\n"
            "Item berhasil ditambahkan ke cart.\n\n"
            f"Produk: {item.product_name}\n"
            f"Qty sekarang: {item.qty}\n"
            f"Subtotal cart: Rp {subtotal}"
        )

    def item_removed(self, item: CartItem, subtotal: int | float) -> str:
        return (
            "AI:\n"
            "Item berhasil dihapus dari cart.\n\n"
            f"Produk: {item.product_name}\n"
            f"Subtotal cart: Rp {subtotal}"
        )

    def item_not_in_cart(self, keyword: str) -> str:
        return f"AI: Produk '{keyword}' tidak ada di cart."

    def cart_empty(self) -> str:
        return "AI: Cart masih kosong."

    def cart_cleared(self) -> str:
        return "AI: Cart berhasil dikosongkan."

    def show_cart(self, cart: CartSession) -> str:
        if cart.is_empty():
            return self.cart_empty()

        lines = ["AI:", "Isi cart:"]
        for item in cart.items:
            lines.append(f"- {item.product_name} x{item.qty} = Rp {item.total}")

        lines.append("")
        lines.append(f"Total: Rp {cart.subtotal}")
        return "\n".join(lines)

    def payment_not_enough(self, total: int | float, paid_amount: int | float) -> str:
        shortage = total - paid_amount
        return (
            "AI: Uang pembayaran belum cukup.\n\n"
            f"Total: Rp {total}\n"
            f"Dibayar: Rp {paid_amount}\n"
            f"Kurang: Rp {shortage}"
        )

    def sale_created(
        self,
        sale_id: Any,
        total: int | float,
        paid_amount: int | float,
        change: int | float,
    ) -> str:
        return (
            "AI:\n"
            "Pembayaran berhasil dan transaksi sudah dibuat.\n\n"
            f"Sales ID: {sale_id}\n"
            f"Total: Rp {total}\n"
            f"Dibayar: Rp {paid_amount}\n"
            f"Kembalian: Rp {change}"
        )
