from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .api import TemanUmkmClient
from .cart import CartItem, CartSession
from .config import DEFAULT_PAYMENT_METHOD
from .context import ConversationContext
from .llm import TemanUmkmLlm
from .matcher import match_products, resolve_candidate
from .parser import (
    AddItemCommand,
    AddLastItemCommand,
    ClearCartCommand,
    MultiCommand,
    PayCommand,
    RemoveItemCommand,
    ShowCartCommand,
    SingleCommand,
    UserCommand,
    parse_user_message,
)


@dataclass
class PendingAction:
    action_type: Literal["add_item"]
    qty: int
    candidates: list[dict[str, Any]]
    remaining_commands: list[SingleCommand] | None = None


@dataclass
class ProductNotFound:
    keyword: str


class TemanUmkmAgent:
    def __init__(self, client: TemanUmkmClient, llm: TemanUmkmLlm | None = None) -> None:
        self.client = client
        self.llm = llm or TemanUmkmLlm()
        self.cart = CartSession(session_id="cli")
        self.context = ConversationContext()
        self.pending_action: PendingAction | None = None
        self.merchant_id: int | None = None
        self.outlet_id: int | None = None

    def login(self) -> None:
        token = self.client.login()
        self.client.set_token(token)

    def process(self, user_message: str) -> str:
        if self.pending_action is not None:
            return self._resolve_pending_action(user_message)

        command = parse_user_message(user_message)
        if command is None:
            return self.llm.unknown_command()

        return self._handle_command(command)

    def _handle_command(self, command: UserCommand) -> str:
        if isinstance(command, MultiCommand):
            return self._handle_multi_command(command)

        if isinstance(command, AddItemCommand):
            return self._add_item(command)

        if isinstance(command, AddLastItemCommand):
            return self._add_last_item(command)

        if isinstance(command, RemoveItemCommand):
            return self._remove_item(command)

        if isinstance(command, ShowCartCommand):
            return self.llm.show_cart(self.cart)

        if isinstance(command, ClearCartCommand):
            self.cart.clear()
            return self.llm.cart_cleared()

        if isinstance(command, PayCommand):
            return self._pay(command)

        return self.llm.unknown_command()

    def _handle_multi_command(self, command: MultiCommand) -> str:
        responses: list[str] = []
        added_items: list[tuple[str, int]] = []
        missing_keywords: list[str] = []

        for index, child_command in enumerate(command.commands):
            if isinstance(child_command, AddItemCommand):
                result = self._add_item_for_multi(child_command)
                if isinstance(result, CartItem):
                    added_items.append((result.product_name, child_command.qty))
                elif isinstance(result, ProductNotFound):
                    missing_keywords.append(result.keyword)
                else:
                    if added_items or missing_keywords:
                        responses.append(
                            self.llm.order_summary(
                                added_items,
                                missing_keywords,
                                self.cart,
                            )
                        )
                        added_items = []
                        missing_keywords = []
                    responses.append(result)
            else:
                if added_items or missing_keywords:
                    responses.append(
                        self.llm.order_summary(
                            added_items,
                            missing_keywords,
                            self.cart,
                        )
                    )
                    added_items = []
                    missing_keywords = []
                responses.append(self._handle_command(child_command))

            if self.pending_action is not None:
                self.pending_action.remaining_commands = command.commands[index + 1 :]
                return self.llm.combine_responses(responses)

        if added_items or missing_keywords:
            responses.append(
                self.llm.order_summary(
                    added_items,
                    missing_keywords,
                    self.cart,
                )
            )

        return self.llm.combine_responses(responses)

    def _add_item(self, command: AddItemCommand) -> str:
        result = self._add_item_for_multi(command)
        if isinstance(result, CartItem):
            return self.llm.item_added(result, self.cart.subtotal)

        if isinstance(result, ProductNotFound):
            return self.llm.product_not_found(result.keyword)

        return result

    def _add_item_for_multi(
        self,
        command: AddItemCommand,
    ) -> CartItem | ProductNotFound | str:
        merchant_id = self._get_merchant_id()
        if merchant_id is None:
            return self.llm.merchant_not_found()

        products = self.client.get_products(merchant_id)
        match_result = match_products(products, command.product_keyword)

        if match_result.has_exact_match():
            return self._add_product_to_cart_item(match_result.exact, command.qty)

        if not match_result.has_candidates():
            return ProductNotFound(keyword=command.product_keyword)

        if match_result.has_single_candidate():
            return self._add_product_to_cart_item(
                match_result.candidates[0],
                command.qty,
            )

        self.pending_action = PendingAction(
            action_type="add_item",
            qty=command.qty,
            candidates=match_result.candidates,
        )
        return self.llm.clarify_product(match_result.candidates)

    def _add_last_item(self, command: AddLastItemCommand) -> str:
        if self.context.last_product is None:
            return self.llm.last_product_not_found()

        return self._add_product_to_cart(self.context.last_product, command.qty)

    def _resolve_pending_action(self, user_message: str) -> str:
        pending_action = self.pending_action
        if pending_action is None:
            return self.llm.unknown_command()

        product = resolve_candidate(pending_action.candidates, user_message)
        if product is None:
            return self.llm.clarification_not_found(pending_action.candidates)

        self.pending_action = None

        if pending_action.action_type == "add_item":
            responses = [self._add_product_to_cart(product, pending_action.qty)]

            if pending_action.remaining_commands:
                responses.append(
                    self._handle_multi_command(
                        MultiCommand(commands=pending_action.remaining_commands)
                    )
                )

            return self.llm.combine_responses(responses)

        return self.llm.unknown_command()

    def _add_product_to_cart(self, product: dict[str, Any], qty: int) -> str:
        item = self._add_product_to_cart_item(product, qty)
        return self.llm.item_added(item, self.cart.subtotal)

    def _add_product_to_cart_item(self, product: dict[str, Any], qty: int) -> CartItem:
        item: CartItem = self.cart.add_item(product, qty)
        self.context.remember_product(product, action="add_item")
        return item

    def _remove_item(self, command: RemoveItemCommand) -> str:
        item = self.cart.remove_item(command.product_keyword)

        if item is None:
            return self.llm.item_not_in_cart(command.product_keyword)

        return self.llm.item_removed(item, self.cart.subtotal)

    def _pay(self, command: PayCommand) -> str:
        if self.cart.is_empty():
            return self.llm.cart_empty()

        merchant_id = self._get_merchant_id()
        outlet_id = self._get_outlet_id(merchant_id) if merchant_id is not None else None

        if merchant_id is None:
            return self.llm.merchant_not_found()

        if outlet_id is None:
            return self.llm.outlet_not_found()

        total = self.cart.subtotal
        if command.paid_amount < total:
            return self.llm.payment_not_enough(total, command.paid_amount)

        sale = self.client.create_sale(
            merchant_id=merchant_id,
            outlet_id=outlet_id,
            payment_method=command.payment_method or DEFAULT_PAYMENT_METHOD,
            items=self.cart.to_sale_items(),
        )

        change = command.paid_amount - total
        self.cart.clear()

        return self.llm.sale_created(
            sale_id=sale["id"],
            total=total,
            paid_amount=command.paid_amount,
            change=change,
        )

    def _get_merchant_id(self) -> int | None:
        if self.merchant_id is not None:
            return self.merchant_id

        merchants = self.client.get_merchants()
        if not merchants:
            return None

        self.merchant_id = merchants[0]["id"]
        return self.merchant_id

    def _get_outlet_id(self, merchant_id: int) -> int | None:
        if self.outlet_id is not None:
            return self.outlet_id

        outlets = self.client.get_outlets(merchant_id)
        if not outlets:
            return None

        self.outlet_id = outlets[0]["id"]
        return self.outlet_id
