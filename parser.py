from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias


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


SingleCommand: TypeAlias = (
    AddItemCommand
    | AddLastItemCommand
    | RemoveItemCommand
    | ShowCartCommand
    | ClearCartCommand
    | PayCommand
)


@dataclass
class MultiCommand:
    commands: list[SingleCommand]


UserCommand: TypeAlias = SingleCommand | MultiCommand


def parse_user_message(user_message: str) -> UserCommand | None:
    normalized = user_message.lower().strip()

    if normalized in {"cart", "show cart", "lihat cart", "keranjang", "cart saya apa"}:
        return ShowCartCommand()

    if normalized in {"clear cart", "kosongkan cart", "hapus cart"}:
        return ClearCartCommand()

    natural_order_command = parse_natural_order_command(normalized)
    if natural_order_command is not None:
        return natural_order_command

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


def parse_natural_order_command(normalized: str) -> AddItemCommand | MultiCommand | None:
    prefixes = [
        "saya mau beli ",
        "saya ingin beli ",
        "aku mau beli ",
        "aku ingin beli ",
        "mau beli ",
        "ingin beli ",
        "tolong belikan ",
        "belikan ",
        "beli ",
        "pesan ",
        "order ",
    ]

    items_text = ""
    for prefix in prefixes:
        if normalized.startswith(prefix):
            items_text = normalized.removeprefix(prefix).strip()
            break

    if not items_text:
        return None

    item_texts = split_order_items(items_text)
    commands = [
        command
        for item_text in item_texts
        if (command := parse_order_item_text(item_text)) is not None
    ]

    if not commands:
        return None

    if len(commands) == 1:
        return commands[0]

    return MultiCommand(commands=commands)


def split_order_items(items_text: str) -> list[str]:
    normalized_items = items_text.replace(",", " dan ")
    return [
        item_text.strip()
        for item_text in normalized_items.split(" dan ")
        if item_text.strip()
    ]


def parse_order_item_text(item_text: str) -> AddItemCommand | None:
    parts = item_text.split()
    if not parts:
        return None

    try:
        qty = int(parts[0])
        product_keyword = " ".join(parts[1:]).strip()
    except ValueError:
        qty = 1
        product_keyword = item_text.strip()

    if qty <= 0 or not product_keyword:
        return None

    return AddItemCommand(qty=qty, product_keyword=product_keyword)


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
    if len(parts) < 2:
        return None

    try:
        qty = int(parts[1])
        product_keyword = " ".join(parts[2:]).strip()
    except ValueError:
        qty = 1
        product_keyword = " ".join(parts[1:]).strip()

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
