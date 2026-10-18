import time

from selenium.common.exceptions import (
    NoSuchWindowException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait

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
        def find_pumk_section(driver):
            try:
                handles = driver.window_handles
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
                    driver.switch_to.window(handle)
                    driver.execute_script(
                        "window.scrollTo(0, document.documentElement.scrollHeight);"
                    )
                    for element in driver.find_elements(
                        *locators.PUMK_SECTION_LOCATOR
                    ):
                        if element.is_displayed() and element.is_enabled():
                            return element
                except (NoSuchWindowException, StaleElementReferenceException):
                    continue
            return False

        return WebDriverWait(
            self.driver,
            60,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(
            find_pumk_section,
            "Menu Pasca Kredit PUMK tidak ditemukan setelah login dan scroll "
            "dashboard. Pastikan akun memiliki akses ke menu ini.",
        )

    def return_to_home_dashboard(self):
        home_breadcrumb = WebDriverWait(
            self.driver, 30, poll_frequency=0.5
        ).until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const clickable = [...document.querySelectorAll(
                    'a, [role="link"], button, [onclick]'
                )].filter(element =>
                    visible(element) &&
                    normalize(element.innerText || element.textContent) === 'Beranda'
                );
                const candidates = clickable.length
                    ? clickable
                    : [...document.querySelectorAll('body *')].filter(element =>
                        visible(element) &&
                        normalize(element.innerText || element.textContent) === 'Beranda' &&
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent) === 'Beranda'
                        )
                    );
                candidates.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                return candidates[0] || false;
                """
            ),
            "Breadcrumb Beranda tidak ditemukan pada halaman pengajuan.",
        )
        self.click_centered(home_breadcrumb)
        return self.wait_for_dashboard()

    def click_centered(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", element)

    def find_pumk_see_all(self):
        return WebDriverWait(
            self.driver,
            30,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(
            lambda driver: driver.execute_script(
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
                return false;
                """
            ),
            "Tombol Lihat Semua pada bagian Pasca Kredit PUMK tidak ditemukan.",
        )

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

    def open_survey_menu(self, pumk_section):
        self.driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(0.5)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            pumk_section,
        )
        self.click_centered(self.find_pumk_see_all())
        survey_item = WebDriverWait(self.driver, 30, poll_frequency=0.5).until(
            lambda driver: driver.execute_script(
                """
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const normalize = value => value.trim().replace(/\\s+/g, ' ');
                const matches = [...document.querySelectorAll('body *')]
                    .filter(element => {
                        const text = normalize(
                            element.innerText || element.textContent || ''
                        ).toLocaleLowerCase();
                        return visible(element) &&
                            text === 'survey restrukturisasi pumk';
                    });
                const leaves = matches.filter(element =>
                    ![...element.children].some(child => {
                        const text = normalize(
                            child.innerText || child.textContent || ''
                        ).toLocaleLowerCase();
                        return text === 'survey restrukturisasi pumk';
                    })
                );
                const candidates = leaves.length ? leaves : matches;
                candidates.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                return candidates[0] || null;
                """
            )
        )
        self.click_centered(survey_item)

    def open_recommendation_menu(self, pumk_section):
        self._open_pumk_menu(
            pumk_section,
            "Rekomendasi Restrukturisasi PUMK",
            "Menu Rekomendasi Restrukturisasi PUMK tidak ditemukan.",
        )

    def open_approval_menu(self, pumk_section):
        self._open_pumk_menu(
            pumk_section,
            "Persetujuan Restrukturisasi PUMK",
            "Menu Persetujuan Restrukturisasi PUMK tidak ditemukan.",
        )

    def open_realisasi_menu(self, pumk_section):
        self._open_pumk_menu(
            pumk_section,
            "Realisasi Restrukturisasi PUMK",
            "Menu Realisasi Restrukturisasi PUMK tidak ditemukan.",
            wait_for_process_list=False,
            open_see_all=False,
        )

    def _open_pumk_menu(
        self,
        pumk_section,
        menu_title,
        error_message,
        wait_for_process_list=True,
        open_see_all=True,
    ):
        self.driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(0.5)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            pumk_section,
        )
        if open_see_all:
            self.click_centered(self.find_pumk_see_all())
        WebDriverWait(self.driver, 30, poll_frequency=0.5).until(
            lambda driver: driver.execute_script(
                """
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const normalize = value => value.trim().replace(/\\s+/g, ' ');
                const findMenuItems = scope => {
                    const matches = [...scope.querySelectorAll('*')].filter(element =>
                        visible(element) &&
                        normalize(element.innerText || element.textContent || '') ===
                            arguments[0]
                    );
                    return matches.filter(element =>
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent || '') ===
                                arguments[0]
                        )
                    );
                };
                let candidates = [];
                if (arguments[2]) {
                    candidates = findMenuItems(document);
                } else {
                    let section = arguments[1].parentElement;
                    while (section && section !== document.body) {
                        candidates = findMenuItems(section);
                        if (candidates.length) break;
                        section = section.parentElement;
                    }
                }
                candidates.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                const target = candidates[0];
                if (!target) return false;
                target.scrollIntoView({block: 'center', inline: 'center'});
                target.click();
                return true;
                """,
                menu_title,
                pumk_section,
                open_see_all,
            ),
            error_message,
        )
        if wait_for_process_list:
            self.wait_for_process_list()

    def wait_for_process_list(self):
        return WebDriverWait(self.driver, 30, poll_frequency=0.5).until(
            lambda driver: driver.execute_script(
                """
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                return [...document.querySelectorAll(
                    'button, [role="button"], input[type="button"], input[type="submit"]'
                )].some(element =>
                    visible(element) &&
                    (element.innerText || element.value || '')
                        .trim().toLocaleLowerCase().startsWith('proses')
                );
                """
            ),
            "Daftar proses restrukturisasi PUMK tidak ditemukan.",
        )

    def search_credit_number(self):
        search_button = self.find_visible_and_enabled(locators.SEARCH_CREDIT_LOCATOR)
        self.click_centered(search_button)
