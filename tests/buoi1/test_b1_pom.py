"""Buoi 1 - Page Object Model exercises. Turn every red test green.

Run one exercise:   pytest tests/buoi1 -k b1_1 --headed --slowmo 300
Run all of buoi 1:  pytest tests/buoi1

Rules (same as the final project):
- No locator in this file: locators live in pages/.
- No assertion in pages/: assertions live here.
- No time.sleep(), no wait_for_timeout().
- Every test has a 3-line docstring: goal, precondition, expected.
"""
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage


# ---------------------------------------------------------------- B1.1 (together with the teacher)
@pytest.mark.smoke
@pytest.mark.ui
def test_b1_1_search_keyword_shows_only_matching_products(page):
    """Goal: search filters the grid.
    Precondition: none.
    Expected: caption shows the keyword and every product name contains it."""
    home = HomePage(page).open().search("pliers")
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("pliers")
    names = home.product_names.all_inner_texts()
    assert names, "search returned no products"
    assert all("pliers" in n.lower() for n in names), names


# ---------------------------------------------------------------- B1.2
def test_b1_2_search_unknown_keyword_shows_no_results_message(page):
    """Goal: empty search state.
    Precondition: none.
    Expected: the message 'There are no products found.' and zero product cards."""
    # TODO: search "zzz-no-such-tool", then 2 expects (message text, product count 0)
    raise NotImplementedError("B1.2")


# ---------------------------------------------------------------- B1.3
def test_b1_3_product_add_quantity_three_updates_cart_badge(page):
    """Goal: add-to-cart uses the chosen quantity.
    Precondition: product 'Claw Hammer' exists.
    Expected: toast 'Product added to shopping cart' and the cart badge shows 3."""
    # TODO: HomePage(page).open().open_product("Claw Hammer") ... add_to_cart(quantity=3)
    raise NotImplementedError("B1.3")


# ---------------------------------------------------------------- B1.4
def test_b1_4_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: cart arithmetic.
    Precondition: empty cart (a new context per test gives you one).
    Expected: line price = unit price x 2 and total = sum of the lines."""
    # TODO: read the unit price on the product page BEFORE adding, then go_to_cart()
    # Hint: compare floats with pytest.approx
    raise NotImplementedError("B1.4")


# ---------------------------------------------------------------- B1.5
def test_b1_5_login_wrong_password_shows_error(page):
    """Goal: invalid credentials are rejected.
    Precondition: an e-mail with no account. NEVER a shared account: Toolshop counts failed
    logins (failed_login_attempts) and can lock it for the whole class.
    Expected: 'Invalid email or password' and the URL still ends with /auth/login."""
    # TODO: rewrite test_spaghetti_login_wrong_password with LoginPage
    raise NotImplementedError("B1.5")


def test_b1_5_login_empty_form_shows_required_errors(page):
    """Goal: client-side validation.
    Precondition: none.
    Expected: 'Email is required' and 'Password is required'."""
    raise NotImplementedError("B1.5")


# ---------------------------------------------------------------- B1.6
def test_b1_6_cart_continue_shopping_returns_to_home(page):
    """Goal: page objects chain: each action returns the next page object.
    Precondition: none.
    Expected: after 'Continue Shopping' the product grid is visible again."""
    # TODO: one chain: HomePage(page).open().open_product("Hammer").add_to_cart().go_to_cart()
    raise NotImplementedError("B1.6")


# ---------------------------------------------------------------- B1.7 (challenge)
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_b1_7_sort_by_price_orders_products(page, order):
    """Goal: sorting.
    Precondition: none.
    Expected: prices on the first page are sorted in the chosen direction."""
    # TODO: sort_by(order), wait for the element data-test="sorting_completed", then compare with sorted()
    raise NotImplementedError("B1.7")
