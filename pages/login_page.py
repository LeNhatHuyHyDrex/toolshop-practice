from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/auth/login"

    def __init__(self, page):
        super().__init__(page)
        # TODO B1.5: email, password, submit_button, error, email_error, password_error

    def login(self, email: str, password: str):
        # TODO B1.5
        raise NotImplementedError("B1.5")
