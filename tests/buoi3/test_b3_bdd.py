"""Buoi 3 - BDD with pytest-bdd. Step definitions only call page objects (no new locators here).

Run:  pytest tests/buoi3 -v
Each Examples row becomes its own pytest test - read the test names in the output.
"""
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

# Paths are relative to bdd_features_base_dir in pytest.ini (tests/buoi3/features)
# TODO B3.4: add "cart.feature" here once you have written it
scenarios("search.feature")


# ---------------------------------------------------------------- given (B3.1: read and run)
@given("I am on the home page", target_fixture="home")
def home(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('I search for "{keyword}"'))
def search(home, keyword):
    home.search(keyword)


@then(parsers.parse('every product name contains "{keyword}"'))
def names_contain(home, keyword):
    expect(home.search_completed).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names and all(keyword.lower() in n.lower() for n in names), names


# ---------------------------------------------------------------- B3.2: the two missing steps
# Run pytest first: pytest-bdd tells you exactly which step text has no definition.
# TODO: @then('the search caption mentions "{keyword}"')
# TODO: @then('I see the message "{message}"')


# ---------------------------------------------------------------- B3.4: steps for cart.feature
# Hints:
#   - "When I open the product ..." returns a ProductPage: use target_fixture="product_page"
#   - read the unit price BEFORE adding to the cart and keep it: target_fixture="unit_price"
#   - numbers in steps: parsers.parse("... quantity {quantity:d}")
