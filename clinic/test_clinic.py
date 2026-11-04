"""Flaky clinic (buoi 4, exercise B4.1). Five sick tests. Diagnose, then cure.

Run each patient several times and watch it flicker:
  for i in 1 2 3 4 5; do pytest clinic -q -p no:randomly; done
Patient 3 also: run it alone, and run it in parallel:
  pytest clinic/test_clinic.py::test_patient3_b_add_product_to_the_same_cart
  pytest clinic -n 2

For every patient write down: symptom, cause, cure. The cure must not use sleep.
"""
import time

from playwright.sync_api import expect

from conftest import register_user, strong_password
from pages.home_page import HomePage


# Patient 1 - "it passes when I debug it step by step"
def test_patient1_search_hammer(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    home.search("hammer")
    names = home.product_names.all_inner_texts()
    assert names and all("hammer" in n.lower() for n in names), names


# Patient 2 - "I added a sleep and now it works on my laptop"
def test_patient2_sort_price_desc(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    home.sort_by("price,desc")
    time.sleep(0.5)
    prices = home.prices()
    assert prices == sorted(prices, reverse=True), prices


# Patient 3 - "green in the full run, red when I run it alone or in CI"
CART_ID = None


def test_patient3_a_create_cart(api):
    global CART_ID
    CART_ID = api.post("/carts").json()["id"]
    assert CART_ID


def test_patient3_b_add_product_to_the_same_cart(api):
    product = api.get("/products", params={"page": 1}).json()["data"][0]
    response = api.post(f"/carts/{CART_ID}", data={"product_id": product["id"], "quantity": 1})
    assert response.ok, response.text()


# Patient 4 - "it was green yesterday"
def test_patient4_register_clinic_user(api):
    response = register_user(api, "qa-clinic-patient4@example.com", strong_password())
    assert response.status == 201, response.text()


# Patient 5 - "red on CI, green on my machine, sometimes red on my machine too"
def test_patient5_price_slider_max_15(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    slider = page.get_by_role("slider").nth(1)
    slider.focus()
    for _ in range(85):
        page.keyboard.press("ArrowLeft")
    expect(slider).to_have_attribute("aria-valuenow", "15")
    prices = home.prices()
    assert all(p <= 15 for p in prices), prices
