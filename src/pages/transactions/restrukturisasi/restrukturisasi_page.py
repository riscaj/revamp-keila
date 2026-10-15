import time

from selenium.common.exceptions import (
    NoSuchWindowException,
    StaleElementReferenceException,
)

from src.pages.transactions.restrukturisasi import restrukturisasi_locators as locators


class RestrukturisasiPage:
    login_url = locators.LOGIN_URL
    credit_number_locator = locators.CREDIT_NUMBER_LOCATOR

    def __init__(self, driver):
        self.driver = driver

    def find_visible_and_enabled(self, locator):
        while True:
            try:
                for element in self.driver.find_elements(*locator):
                    if element.is_displayed() and element.is_enabled():
                        return element
            except StaleElementReferenceException:
                time.sleep(0.2)
                continue
            time.sleep(0.5)

    def find_visible(self, locator):
        while True:
            try:
                for element in self.driver.find_elements(*locator):
                    if element.is_displayed():
                        return element
            except StaleElementReferenceException:
                time.sleep(0.2)
                continue
            time.sleep(0.5)

    def wait_for_dashboard(self):
        while True:
            try:
                handles = self.driver.window_handles
            except NoSuchWindowException as error:
                raise RuntimeError(
                    "Jendela Chrome tertutup sebelum dashboard ditemukan."
                ) from error
            if not handles:
                raise RuntimeError(
                    "Semua jendela Chrome tertutup sebelum dashboard ditemukan."
                )

            for handle in handles:
                try:
                    self.driver.switch_to.window(handle)
                    for element in self.driver.find_elements(
                        *locators.PUMK_SECTION_LOCATOR
                    ):
                        if element.is_displayed() and element.is_enabled():
                            return element
                except (NoSuchWindowException, StaleElementReferenceException):
                    continue
            time.sleep(1)

    def click_centered(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", element)

    def find_pumk_see_all(self):
        while True:
            try:
                button = self.driver.execute_script(
                    """
                    const visible = element =>
                        element.getClientRects().length > 0 &&
                        getComputedStyle(element).visibility !== 'hidden' &&
                        getComputedStyle(element).display !== 'none';
                    const headings = [...document.querySelectorAll('body *')]
                        .filter(element =>
                            element.textContent.trim() === 'Pasca Kredit PUMK' &&
                            visible(element)
                        );
                    for (const heading of headings) {
                        let parent = heading.parentElement;
                        while (parent && parent !== document.body) {
                            const buttons = [...parent.querySelectorAll(
                                '[id="btn_see_all_feature"]'
                            )].filter(visible);
                            if (buttons.length === 1) return buttons[0];
                            parent = parent.parentElement;
                        }
                    }
                    return null;
                    """
                )
                if button is not None:
                    return button
            except StaleElementReferenceException:
                pass
            time.sleep(0.5)

    def fill_login(self, username, password):
        username_input = self.find_visible(locators.USERNAME_LOCATOR)
        password_input = self.find_visible(locators.PASSWORD_LOCATOR)
        submit_button = self.find_visible_and_enabled(locators.SUBMIT_LOCATOR)

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        submit_button.click()

    def open_restructuring_menu(self, pumk_section):
        self.driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(0.5)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            pumk_section,
        )
        self.click_centered(self.find_pumk_see_all())
        restructuring_item = self.find_visible_and_enabled(
            locators.RESTRUCTURING_LOCATOR
        )
        self.click_centered(restructuring_item)

    def search_credit_number(self):
        search_button = self.find_visible_and_enabled(locators.SEARCH_CREDIT_LOCATOR)
        self.click_centered(search_button)
