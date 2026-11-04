"""Buoi 4 - LOOSE assertions. Every test here is green on PROD *and* on BUGGY.

That is the problem: BUGGY has real defects in exactly these features, and this suite misses all of them.

Exercise B4.4: for each test, tighten the assertion so that it
  - stays green on PROD,
  - turns red on BUGGY,
  - and the failure message tells a developer what is wrong.
Do NOT add new tests to reach a number. Strengthen the expectation.

Run on BUGGY:
  BASE_URL=https://with-bugs.practicesoftwaretesting.com API_URL=https://api-with-bugs.practicesoftwaretesting.com ROUTE_PREFIX=/# pytest tests/buoi4 -v
"""
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.regression
@pytest.mark.ui
def test_b4_a_add_to_cart_shows_a_toast(page):
    """Goal: user gets feedback after add-to-cart. Precondition: none. Expected: a toast appears."""
    product = HomePage(page).open().open_product("Combination Pliers").add_to_cart()
    expect(product.toast.first).to_be_visible()  # LOOSE: what does the toast say?


@pytest.mark.regression
@pytest.mark.ui
def test_b4_b_cart_has_a_total(page):
    """Goal: cart shows prices. Precondition: one product, quantity 2. Expected: a positive total."""
    cart = HomePage(page).open().open_product("Combination Pliers").add_to_cart(quantity=2).go_to_cart()
    expect(cart.product_titles.first).to_have_text("Combination Pliers")
    assert cart.total_value() > 0  # LOOSE: is every line right?


@pytest.mark.regression
@pytest.mark.ui
def test_b4_c_search_without_results_counts_zero(page):
    """Goal: empty search state. Precondition: none. Expected: result counter says 0."""
    home = HomePage(page).open().search("zzz-no-such-tool")
    expect(home.search_result_count).to_contain_text("0")  # LOOSE: is the user told why the grid is empty?


@pytest.mark.regression
@pytest.mark.ui
def test_b4_d_login_empty_form_stays_on_login(page):
    """Goal: validation of the login form. Precondition: none. Expected: user stays on the login page."""
    login = LoginPage(page).open()
    login.submit_button.click()
    expect(page).to_have_url(re.compile(r"/auth/login$"))  # LOOSE: which messages are shown?


@pytest.mark.regression
@pytest.mark.ui
def test_b4_e_header_has_contact_and_search(page):
    """Goal: header controls exist. Precondition: none. Expected: Contact link and Search button visible."""
    home = HomePage(page).open()
    expect(home.nav_contact).to_be_visible()  # LOOSE: read the labels
    expect(home.search_button).to_be_visible()


@pytest.mark.regression
@pytest.mark.ui
def test_b4_f_home_lists_products(page):
    """Goal: catalogue is browsable. Precondition: none. Expected: products are listed."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()  # LOOSE: can the user reach ALL products? (hint: GET /products total vs per_page)


@pytest.mark.regression
@pytest.mark.api
def test_b4_g_search_api_finds_wrench(api):
    """Goal: search endpoint answers. Precondition: none. Expected: results for 'wrench'."""
    names = [p["name"] for p in api.get("/products/search", params={"q": "wrench"}).json()["data"]]
    assert len(names) > 0  # LOOSE: are they all wrenches?
