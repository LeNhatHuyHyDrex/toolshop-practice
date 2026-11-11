from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name = page.get_by_test_id("product-name")
        self.unit_price = page.get_by_test_id("unit-price")
        self.quantity = page.get_by_test_id("quantity")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")

    def add_to_cart(self, quantity: int = 1):
        if quantity != 1:
            self.quantity.fill(str(quantity))
        self.add_to_cart_button.click()
        return self

    def price(self) -> float:
        return float(self.unit_price.inner_text())
