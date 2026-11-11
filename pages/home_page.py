import re

from pages.base_page import BasePage

# PROD loads the grid with "QUERY /products", BUGGY with "GET /products?...". Not /products/search.
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")


class HomePage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.search_box = page.get_by_test_id("search-query")
        self.search_result_count = page.get_by_test_id("search-result-count")
        # B1.1
        self.search_button = page.get_by_test_id("search-submit")
        self.search_caption = page.get_by_test_id("search-caption")
        self.search_completed = page.get_by_test_id("search_completed")
        self.product_names = page.get_by_test_id("product-name")
        # B1.2
        self.no_results = page.get_by_test_id("no-results")
        # B1.7
        self.sort_select = page.get_by_test_id("sort")
        self.sorting_completed = page.get_by_test_id("sorting_completed")
        self.product_prices = page.get_by_test_id("product-price")
        # TODO B2/B4 (later): price_slider_max = page.get_by_role("slider").nth(1)

    def open(self):
        """Return only after the first product list has arrived.

        Race in Toolshop: if you search before the initial list arrives, the late initial list
        overwrites the search results. Waiting for that response is synchronisation, not an assertion.
        """
        with self.page.expect_response(lambda r: PRODUCT_LIST.search(r.url) is not None):
            super().open()
        return self

    def search(self, keyword: str):
        self.search_box.fill(keyword)
        self.search_button.click()
        return self

    def sort_by(self, value: str):
        """value: name,asc | name,desc | price,asc | price,desc"""
        self.sort_select.select_option(value)
        return self

    def product_card(self, name: str):
        # Exact name match: "Pliers" must not match "Combination Pliers".
        return self.product_names.filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))

    def open_product(self, name: str):
        from pages.product_page import ProductPage

        self.product_card(name).first.click()
        return ProductPage(self.page)

    def prices(self) -> list[float]:
        return [float(p.replace("$", "")) for p in self.product_prices.all_inner_texts()]
