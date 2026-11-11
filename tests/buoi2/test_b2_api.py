"""Buoi 2 - API testing with APIRequestContext (not the requests library).

Fixtures you can use (see conftest.py): api, test_user, auth_token, auth_headers
Helpers: register_user(api, email, password), new_email(), strong_password()

Run:  pytest tests/buoi2/test_b2_api.py -v
"""
import json
from pathlib import Path

import pytest

from conftest import new_email, register_user, strong_password  # noqa: F401  (you will need them)

KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text())


# ---------------------------------------------------------------- B2.1 (together)
@pytest.mark.smoke
@pytest.mark.api
def test_b2_1_status_returns_toolshop(api):
    """Goal: API is alive. Precondition: none. Expected: 200 and app_name Toolshop."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"


# ---------------------------------------------------------------- B2.2
def test_b2_2_products_first_page_has_pagination_and_product_shape(api):
    """Goal: contract of GET /products.
    Precondition: none.
    Expected: keys current_page/data/per_page/total/last_page, 0 < len(data) <= per_page,
    every product has id (str or int), a non-empty name and a price > 0.
    Rule: NO absolute numbers (PROD has 50 products, BUGGY 26)."""
    response = api.get("/products")
    assert response.status == 200, response.text()
    body = response.json()
    assert {"current_page", "data", "per_page", "total", "last_page"} <= body.keys()
    assert 0 < len(body["data"]) <= body["per_page"]
    for product in body["data"]:
        assert isinstance(product["id"], (str, int)), product
        assert product["name"], product
        assert product["price"] > 0, product


# ---------------------------------------------------------------- B2.3 data-driven
@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_b2_3_search_api_returns_only_matching_names(api, case):
    """Goal: GET /products/search?q=... filters by name.
    Precondition: none.
    Expected: at least one result and every name contains the keyword.
    Extra: add "saw" and "wrench" to data/search_keywords.json - no code change needed."""
    response = api.get("/products/search", params={"q": case["keyword"]})
    assert response.status == 200, response.text()
    names = [product["name"] for product in response.json()["data"]]
    assert names, f"no product found for {case['keyword']!r}"
    assert all(case["must_contain"] in name.lower() for name in names), names


# ---------------------------------------------------------------- B2.4 errors
@pytest.mark.parametrize("path, expected_status", [
    ("/users/me", 401),
    ("/products/does-not-exist", 404),
], ids=["no-token", "unknown-product"])
def test_b2_4a_protected_or_missing_resource_returns_4xx(api, path, expected_status):
    """Goal: protected or missing resources are refused.
    Precondition: no Authorization header.
    Expected: the exact 4xx status for each path and a JSON body with a message."""
    response = api.get(path)
    assert response.status == expected_status, response.text()
    assert response.json()["message"]


def test_b2_4b_register_empty_body_returns_422_with_field_errors(api):
    """Goal: server-side validation. Precondition: none.
    Expected: 422 and error lists for 'email' and 'password'."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()
    for field in ("email", "password"):
        assert isinstance(errors[field], list) and errors[field], errors


def test_b2_4c_register_leaked_password_is_rejected(api):
    """Goal: password policy. Precondition: none.
    Expected: 422 because 'Welcome01!' appears in known data leaks."""
    response = register_user(api, new_email(), "Welcome01!")
    assert response.status == 422, response.text()
    assert any("data leak" in message for message in response.json()["password"])


# ---------------------------------------------------------------- B2.5 token
def test_b2_5a_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: bearer token grants access. Precondition: user registered by the fixture.
    Expected: 200 and the same email."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]


def test_b2_5b_register_response_does_not_expose_password(api):
    """Goal: no secrets in responses. Precondition: none.
    Expected: 201 and no 'password' key in the JSON body."""
    response = register_user(api, new_email(), strong_password())
    assert response.status == 201, response.text()
    assert "password" not in response.json()


# ---------------------------------------------------------------- B2.6 your own fixture
@pytest.fixture
def new_cart(api) -> str:
    """Create an empty cart and return its id."""
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]


def test_b2_6_cart_add_product_quantity_two_is_stored(api, new_cart):
    """Goal: cart API stores the quantity.
    Precondition: a new cart (your fixture) and the first product of GET /products.
    Expected: GET /carts/{id} has exactly 1 item, quantity 2, same product_id."""
    product = api.get("/products").json()["data"][0]
    added = api.post(f"/carts/{new_cart}", data={"product_id": product["id"], "quantity": 2})
    assert added.status == 200, added.text()
    cart = api.get(f"/carts/{new_cart}")
    assert cart.status == 200, cart.text()
    items = cart.json()["cart_items"]
    assert len(items) == 1, items
    assert items[0]["quantity"] == 2
    assert items[0]["product_id"] == product["id"]
