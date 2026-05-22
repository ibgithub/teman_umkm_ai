from __future__ import annotations

from typing import Any

import requests

from config import BASE_URL, PASSWORD, REQUEST_TIMEOUT, USERNAME


class TemanUmkmApiError(RuntimeError):
    pass


class TemanUmkmClient:
    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def login(self, username: str = USERNAME, password: str = PASSWORD) -> str:
        data = self._request(
            "POST",
            "/api/auth/login",
            json={"username": username, "password": password},
            auth_required=False,
        )
        return data["token"]

    def set_token(self, token: str) -> None:
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_merchants(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/merchants/data")

    def get_outlets(self, merchant_id: int) -> list[dict[str, Any]]:
        return self._request("GET", f"/api/outlets/byMerchant/{merchant_id}")

    def get_products(self, merchant_id: int) -> list[dict[str, Any]]:
        return self._request("GET", f"/api/products/byMerchant/{merchant_id}")

    def create_sale(
        self,
        merchant_id: int,
        outlet_id: int,
        payment_method: str,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = {
            "merchantId": merchant_id,
            "outletId": outlet_id,
            "paymentMethod": payment_method,
            "items": items,
        }
        return self._request("POST", "/api/sales", json=payload)

    def _request(
        self,
        method: str,
        path: str,
        auth_required: bool = True,
        **kwargs: Any,
    ) -> Any:
        url = f"{self.base_url}{path}"

        if auth_required and "Authorization" not in self.session.headers:
            raise TemanUmkmApiError("Token belum tersedia. Login terlebih dahulu.")

        try:
            response = self.session.request(
                method,
                url,
                timeout=REQUEST_TIMEOUT,
                **kwargs,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            message = getattr(exc.response, "text", str(exc))
            raise TemanUmkmApiError(f"Request gagal: {method} {url} - {message}") from exc

        if not response.content:
            return None

        return response.json()


def find_product(products: list[dict[str, Any]], keyword: str) -> dict[str, Any] | None:
    keyword = keyword.lower().strip()

    for product in products:
        name = str(product.get("name", "")).lower()
        if keyword in name:
            return product

    return None
