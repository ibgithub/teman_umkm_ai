from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConversationContext:
    last_product: dict[str, Any] | None = None
    last_action: str | None = None

    def remember_product(self, product: dict[str, Any], action: str) -> None:
        self.last_product = product
        self.last_action = action
