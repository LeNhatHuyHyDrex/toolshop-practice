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
    raise NotImplementedError("B2.2")


# ---------------------------------------------------------------- B2.3 data-driven
@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_b2_3_search_api_returns_only_matching_names(api, case):
    """Goal: GET /products/search?q=... filters by name.
    Precondition: none.
    Expected: at least one result and every name contains the keyword.
    Extra: add "saw" and "wrench" to data/search_keywords.json - no code change needed."""
    raise NotImplementedError("B2.3")


# ---------------------------------------------------------------- B2.4 errors
# TODO B2.4a: one parametrized test: GET /users/me -> 401, GET /products/does-not-exist -> 404
def test_b2_4a_protected_or_missing_resource_returns_4xx(api):
    raise NotImplementedError("B2.4a - turn this into a @pytest.mark.parametrize test")


def test_b2_4b_register_empty_body_returns_422_with_field_errors(api):
    """Goal: server-side validation. Precondition: none.
    Expected: 422 and error lists for 'email' and 'password'."""
    raise NotImplementedError("B2.4b")


def test_b2_4c_register_leaked_password_is_rejected(api):
    """Goal: password policy. Precondition: none.
    Expected: 422 because 'Welcome01!' appears in known data leaks."""
    raise NotImplementedError("B2.4c")


# ---------------------------------------------------------------- B2.5 token
def test_b2_5a_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: bearer token grants access. Precondition: user registered by the fixture.
    Expected: 200 and the same email."""
    raise NotImplementedError("B2.5a")


def test_b2_5b_register_response_does_not_expose_password(api):
    """Goal: no secrets in responses. Precondition: none.
    Expected: 201 and no 'password' key in the JSON body."""
    raise NotImplementedError("B2.5b")


# ---------------------------------------------------------------- B2.6 your own fixture
# TODO B2.6: write a fixture `new_cart` (in this file) that POSTs /carts and returns the id.
def test_b2_6_cart_add_product_quantity_two_is_stored(api):
    """Goal: cart API stores the quantity.
    Precondition: a new cart (your fixture) and the first product of GET /products.
    Expected: GET /carts/{id} has exactly 1 item, quantity 2, same product_id."""
    raise NotImplementedError("B2.6 - add the new_cart fixture to the signature")
