from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class AddItemCommand:
    qty: int
    product_keyword: str


@dataclass
class AddLastItemCommand:
    qty: int


@dataclass
class RemoveItemCommand:
    product_keyword: str


@dataclass
class ShowCartCommand:
    pass


@dataclass
class ClearCartCommand:
    pass


@dataclass
class PayCommand:
    payment_method: Literal["CASH"]
    paid_amount: int


UserCommand = (
    AddItemCommand
    | AddLastItemCommand
    | RemoveItemCommand
    | ShowCartCommand
    | ClearCartCommand
    | PayCommand
)


def parse_user_message(user_message: str) -> UserCommand | None:
    normalized = user_message.lower().strip()

    if normalized in {"cart", "show cart", "lihat cart", "keranjang", "cart saya apa"}:
        return ShowCartCommand()

    if normalized in {"clear cart", "kosongkan cart", "hapus cart"}:
        return ClearCartCommand()

    parts = normalized.split()
    if not parts:
        return None

    if parts[0] in {"jual", "tambah"}:
        add_last_command = parse_add_last_item_command(parts)
        if add_last_command is not None:
            return add_last_command

        return parse_add_item_command(parts)

    if parts[0] in {"hapus", "remove"}:
        return parse_remove_item_command(parts)

    if parts[0] == "bayar":
        return parse_pay_command(parts)

    return None


def parse_add_last_item_command(parts: list[str]) -> AddLastItemCommand | None:
    if len(parts) == 2 and parts[1] == "lagi":
        return AddLastItemCommand(qty=1)

    if len(parts) == 3 and parts[2] == "lagi":
        try:
            qty = int(parts[1])
        except ValueError:
            return None

        if qty <= 0:
            return None

        return AddLastItemCommand(qty=qty)

    return None


def parse_add_item_command(parts: list[str]) -> AddItemCommand | None:
    if len(parts) < 3:
        return None

    try:
        qty = int(parts[1])
    except ValueError:
        return None

    product_keyword = " ".join(parts[2:]).strip()
    if qty <= 0 or not product_keyword:
        return None

    return AddItemCommand(qty=qty, product_keyword=product_keyword)


def parse_remove_item_command(parts: list[str]) -> RemoveItemCommand | None:
    if len(parts) < 2:
        return None

    product_keyword = " ".join(parts[1:]).strip()
    if not product_keyword:
        return None

    return RemoveItemCommand(product_keyword=product_keyword)


def parse_pay_command(parts: list[str]) -> PayCommand | None:
    if len(parts) < 3 or parts[1] != "cash":
        return None

    paid_amount_text = parts[2].replace(".", "").replace(",", "")

    try:
        paid_amount = int(paid_amount_text)
    except ValueError:
        return None

    if paid_amount <= 0:
        return None

    return PayCommand(payment_method="CASH", paid_amount=paid_amount)
