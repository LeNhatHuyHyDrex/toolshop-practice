from pages.base_page import BasePage


class ContactPage(BasePage):
    path = "/contact"

    def __init__(self, page):
        super().__init__(page)
        self.first_name = page.get_by_test_id("first-name")
        self.last_name = page.get_by_test_id("last-name")
        self.email = page.get_by_test_id("email")
        self.subject = page.get_by_test_id("subject")
        self.message = page.get_by_test_id("message")
        self.attachment = page.get_by_test_id("attachment")
        self.submit_button = page.get_by_test_id("contact-submit")
        self.success = page.get_by_role("alert")
        self.errors = page.locator("[data-test$='-error']")

    def fill_form(self, first: str, last: str, email: str, subject: str, message: str):
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.email.fill(email)
        self.subject.select_option(subject)
        self.message.fill(message)
        return self

    def attach(self, path):
        self.attachment.set_input_files(path)
        return self

    def submit(self):
        self.submit_button.click()
        return self
