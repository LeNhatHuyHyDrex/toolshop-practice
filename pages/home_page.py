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
        # TODO B1.1: search_button, search_caption, search_completed, product_names
        # TODO B1.2: no_results
        # TODO B1.7: sort_select, product_prices
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
        # TODO B1.1: fill the box, click the button, return self
        raise NotImplementedError("B1.1")

    def sort_by(self, value: str):
        """value: name,asc | name,desc | price,asc | price,desc"""
        # TODO B1.7
        raise NotImplementedError("B1.7")

    def product_card(self, name: str):
        # Exact name match: "Pliers" must not match "Combination Pliers".
        return self.product_names.filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))

    def open_product(self, name: str):
        from pages.product_page import ProductPage

        # TODO B1.3: click the card of that product, return a ProductPage
        raise NotImplementedError("B1.3")

    def prices(self) -> list[float]:
        return [float(p.replace("$", "")) for p in self.product_prices.all_inner_texts()]
