from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CartItem:
    product_id: int
    product_name: str
    qty: int
    price: int | float

    @property
    def total(self) -> int | float:
        return self.qty * self.price

    def to_sale_item(self) -> dict:
        return {
            "productId": self.product_id,
            "productName": self.product_name,
            "qty": self.qty,
            "price": self.price,
        }


@dataclass
class CartSession:
    session_id: str
    items: list[CartItem] = field(default_factory=list)

    @property
    def subtotal(self) -> int | float:
        return sum(item.total for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def add_item(self, product: dict, qty: int) -> CartItem:
        product_id = product["id"]
        existing_item = self._find_item_by_product_id(product_id)

        if existing_item is not None:
            existing_item.qty += qty
            return existing_item

        item = CartItem(
            product_id=product_id,
            product_name=product["name"],
            qty=qty,
            price=product["sellingPrice"],
        )
        self.items.append(item)
        return item

    def remove_item(self, product_keyword: str) -> CartItem | None:
        product_keyword = product_keyword.lower().strip()

        for index, item in enumerate(self.items):
            if product_keyword in item.product_name.lower():
                return self.items.pop(index)

        return None

    def clear(self) -> None:
        self.items.clear()

    def to_sale_items(self) -> list[dict]:
        return [item.to_sale_item() for item in self.items]

    def _find_item_by_product_id(self, product_id: int) -> CartItem | None:
        for item in self.items:
            if item.product_id == product_id:
                return item

        return None
