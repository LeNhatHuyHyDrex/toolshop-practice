from playwright.sync_api import Page


class BasePage:
    """Common parts of every Toolshop page.

    Rules: locators live in __init__, actions return a page object, no assertions here.
    """

    path = "/"
    # PROD uses normal routes (/auth/login), BUGGY uses hash routes (/#/auth/login).
    # conftest.py sets this from the ROUTE_PREFIX environment variable.
    route_prefix = ""

    def __init__(self, page: Page):
        self.page = page
        self.nav_home = page.get_by_test_id("nav-home")
        self.nav_contact = page.get_by_test_id("nav-contact")
        self.nav_sign_in = page.get_by_test_id("nav-sign-in")
        self.nav_cart = page.get_by_test_id("nav-cart")
        self.cart_quantity = page.get_by_test_id("cart-quantity")
        self.nav_menu = page.get_by_test_id("nav-menu")
        self.toast = page.get_by_role("alert")

    def open(self):
        self.page.goto(self.route_prefix + self.path)
        return self

    def go_to_cart(self):
        from pages.cart_page import CartPage

        self.nav_cart.click()
        return CartPage(self.page)

    def go_to_sign_in(self):
        from pages.login_page import LoginPage

        self.nav_sign_in.click()
        return LoginPage(self.page)

    def go_to_contact(self):
        from pages.contact_page import ContactPage

        self.nav_contact.click()
        return ContactPage(self.page)
