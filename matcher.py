from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ProductMatchResult:
    exact: dict[str, Any] | None
    candidates: list[dict[str, Any]]

    def has_exact_match(self) -> bool:
        return self.exact is not None

    def has_candidates(self) -> bool:
        return len(self.candidates) > 0

    def has_single_candidate(self) -> bool:
        return len(self.candidates) == 1


def match_products(products: list[dict[str, Any]], keyword: str) -> ProductMatchResult:
    normalized_keyword = normalize_text(keyword)

    exact_matches = [
        product
        for product in products
        if normalize_text(str(product.get("name", ""))) == normalized_keyword
    ]

    if exact_matches:
        return ProductMatchResult(exact=exact_matches[0], candidates=exact_matches)

    candidates = [
        product
        for product in products
        if normalized_keyword in normalize_text(str(product.get("name", "")))
    ]

    return ProductMatchResult(exact=None, candidates=candidates)


def resolve_candidate(
    candidates: list[dict[str, Any]],
    user_message: str,
) -> dict[str, Any] | None:
    normalized_message = normalize_text(user_message)

    selected_by_number = resolve_candidate_by_number(candidates, normalized_message)
    if selected_by_number is not None:
        return selected_by_number

    match_result = match_products(candidates, normalized_message)
    if match_result.has_exact_match():
        return match_result.exact

    if match_result.has_single_candidate():
        return match_result.candidates[0]

    return None


def resolve_candidate_by_number(
    candidates: list[dict[str, Any]],
    user_message: str,
) -> dict[str, Any] | None:
    if not user_message.isdigit():
        return None

    selected_index = int(user_message) - 1
    if selected_index < 0 or selected_index >= len(candidates):
        return None

    return candidates[selected_index]


def normalize_text(value: str) -> str:
    return " ".join(value.lower().strip().split())
