from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # TODO B1.3: name, unit_price, quantity, add_to_cart_button
        # Find the data-test values with DevTools (F12) or: playwright codegen https://practicesoftwaretesting.com

    def add_to_cart(self, quantity: int = 1):
        # TODO B1.3: set the quantity field if quantity != 1, click "Add to cart", return self
        raise NotImplementedError("B1.3")

    def price(self) -> float:
        # TODO B1.4: unit price as a float
        raise NotImplementedError("B1.4")
