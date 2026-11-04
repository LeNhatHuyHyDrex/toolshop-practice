from pages.base_page import BasePage


class AccountPage(BasePage):
    path = "/account"

    def __init__(self, page):
        super().__init__(page)
        self.title = page.get_by_test_id("page-title")
        self.nav_invoices = page.get_by_test_id("nav-invoices")
        self.nav_profile = page.get_by_test_id("nav-profile")
