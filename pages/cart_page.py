from pages.base_page import BasePage


def money(text: str) -> float:
    """'$28.30' -> 28.3"""
    return float(text.replace("$", "").replace(",", "").strip())


class CartPage(BasePage):
    path = "/checkout"

    def __init__(self, page):
        super().__init__(page)
        # TODO B1.4: product_titles, quantities, line_prices, total
        # TODO B1.6: continue_shopping

    def line_totals(self) -> list[float]:
        # TODO B1.4
        raise NotImplementedError("B1.4")

    def total_value(self) -> float:
        # TODO B1.4
        raise NotImplementedError("B1.4")
