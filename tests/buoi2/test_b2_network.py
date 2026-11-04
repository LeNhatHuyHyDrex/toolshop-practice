"""Buoi 2 - route / mocking, and API + UI together.

Run:  pytest tests/buoi2/test_b2_network.py --headed
"""
import json
import re

import pytest  # noqa: F401
from playwright.sync_api import expect

from pages.account_page import AccountPage  # noqa: F401
from pages.home_page import HomePage  # noqa: F401

# Open DevTools > Network on the home page and look at how the product list is loaded:
#   PROD:   QUERY https://api.practicesoftwaretesting.com/products          (JSON body)
#   BUGGY:  GET   https://api-with-bugs.../products?between=price,1&page=1
# One regex catches both, and NOT /products/search or /products/{id}:
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
EMPTY_PAGE = {"current_page": 1, "data": [], "from": None, "last_page": 1,
              "per_page": 9, "to": None, "total": 0}


# ---------------------------------------------------------------- B2.7
def test_b2_7_home_without_images_still_lists_products(page):
    """Goal: the page works without images. Precondition: none.
    Expected: product names visible AND at least one image request was aborted (prove the route ran)."""
    # TODO: page.route(<regex for .png .jpg .jpeg .webp .avif .svg>, handler that records the URL and aborts)
    #       register the route BEFORE opening the page
    raise NotImplementedError("B2.7")


# ---------------------------------------------------------------- B2.8
def test_b2_8_home_with_empty_product_list_shows_no_results(page):
    """Goal: empty state of the grid. Precondition: list API mocked with EMPTY_PAGE.
    Expected: 'There are no products found.' and 0 product cards."""
    # TODO: route.fulfill(status=200, content_type="application/json", body=json.dumps(EMPTY_PAGE))
    raise NotImplementedError("B2.8")


# ---------------------------------------------------------------- B2.9
def test_b2_9_home_when_product_api_fails_page_stays_usable(page):
    """Goal: resilience. Precondition: list API returns 500.
    Expected: 0 product cards and the search box is still editable."""
    raise NotImplementedError("B2.9")


# ---------------------------------------------------------------- B2.10 (challenge)
def test_b2_10_home_renders_price_from_api_response(page):
    """Goal: the UI shows what the API sends. Precondition: real response, first price patched to 999.99.
    Expected: the first price on the page is '$999.99'.
    Hint: response = route.fetch(); body = response.json(); ...; route.fulfill(response=response, json=body)"""
    raise NotImplementedError("B2.10")


# ---------------------------------------------------------------- B2.11 (challenge)
def test_b2_11_account_page_with_token_injected_skips_login_form(page, auth_token):
    """Goal: use the API to set up UI state, skip the login form.
    Precondition: token from the auth_token fixture.
    Expected: AccountPage opens, title 'My account', user menu contains 'QA Bot'.
    Hint: Toolshop keeps the token in localStorage under the key 'auth-token'.
          page.add_init_script(f"window.localStorage.setItem('auth-token', {json.dumps(auth_token)})")"""
    raise NotImplementedError("B2.11")


# ---------------------------------------------------------------- B2.12 (given): storage state, login once per session
def test_b2_12_logged_in_page_shows_user_menu(logged_in_page):
    """Goal: reuse a saved login (fixture auth_state in conftest.py). Precondition: none.
    Expected: user menu shows the account name."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")
