from time import sleep

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.transactions.monitoring import monitoring_locators as locators


class MonitoringPage:
    login_url = locators.LOGIN_URL

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            45,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        )
        self._listing_window = None
        self._detail_window = None
        self._listing_url = None

    def find_visible_and_enabled(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def fill_login(self, username, password):
        username_input = self.find_visible(locators.USERNAME_LOCATOR)
        password_input = self.find_visible(locators.PASSWORD_LOCATOR)
        submit_button = self.find_visible_and_enabled(locators.SUBMIT_LOCATOR)
        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        submit_button.click()

    def wait_for_dashboard(self):
        self._find_monitoring_section()
        return self

    def open_monitoring_menu(self):
        section = self._find_monitoring_section()
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            section,
        )
        see_all = self._find_see_all_for_section(section)
        self._click_centered(see_all)
        menu_item = self._wait_for_exact_text(locators.MONITORING_PROGRAM_TEXT)
        self._click_centered(menu_item)
        self._listing_window = self.driver.current_window_handle
        self._listing_url = self.driver.current_url
        return self

    def wait_for_monitoring_list(self):
        self._wait_for_exact_text(locators.MONITORING_PROGRAM_TEXT)
        self._wait_for_credit_type_control()
        return self

    def search_by_credit_type(self, credit_type):
        control = self._wait_for_credit_type_control()
        if control.tag_name.lower() == "select":
            Select(control).select_by_visible_text(credit_type)
        else:
            self._click_centered(control)
            option = self.wait.until(
                lambda driver: driver.execute_script(
                    """
                    const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                    const visible = element =>
                        element.getClientRects().length > 0 &&
                        getComputedStyle(element).visibility !== 'hidden' &&
                        getComputedStyle(element).display !== 'none';
                    const options = [...document.querySelectorAll(
                        '[role="option"], option, li, button, [data-value], div, span'
                    )].filter(element =>
                        visible(element) &&
                        normalize(element.innerText || element.textContent) === arguments[0] &&
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent) === arguments[0]
                        )
                    );
                    return options[0] || false;
                    """,
                    credit_type,
                ),
                f"Opsi jenis kredit '{credit_type}' tidak ditemukan.",
            )
            self._click_centered(option)

        previous_button = self._first_detail_button_or_none()
        previous_signature = (
            self._result_signature(previous_button) if previous_button else None
        )
        search_button = self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const buttons = [...document.querySelectorAll(
                    'button, [role="button"], input[type="submit"], input[type="button"]'
                )].filter(element =>
                    visible(element) &&
                    normalize(element.innerText || element.value || element.textContent) ===
                        arguments[0]
                );
                return buttons[0] || false;
                """,
                locators.SEARCH_BUTTON_TEXT,
            ),
            "Tombol Cari pada halaman Monitoring Program UMK tidak ditemukan.",
        )
        self._click_centered(search_button)
        self._wait_for_search_results(previous_button, previous_signature)
        return self

    def open_first_record_detail(self):
        self._listing_window = self.driver.current_window_handle
        self._listing_url = self.driver.current_url
        prior_handles = set(self.driver.window_handles)
        detail_button = self._wait_for_first_detail_button()
        prior_page_text = self.driver.execute_script(
            "return document.body.innerText || document.body.textContent || '';"
        )
        self._click_centered(detail_button)
        self.wait.until(
            lambda driver: (
                bool(set(driver.window_handles) - prior_handles)
                or driver.current_url != self._listing_url
                or self._detail_content_is_visible()
                or self._detail_page_replaced(prior_page_text)
            ),
            "Halaman detail data pertama tidak tampil setelah tombol Lihat Detail diklik.",
        )

        new_windows = [
            handle
            for handle in self.driver.window_handles
            if handle not in prior_handles
        ]
        if new_windows:
            self._detail_window = new_windows[-1]
            self.driver.switch_to.window(self._detail_window)
        else:
            self._detail_window = self.driver.current_window_handle
        return self

    def return_to_home_dashboard(self):
        if self._detail_window:
            self.driver.switch_to.window(self._detail_window)
        sleep(3)
        home_breadcrumb = self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                let candidates = [...document.querySelectorAll(
                    'a, [role="link"], button, [onclick]'
                )].filter(element =>
                    visible(element) &&
                    normalize(element.innerText || element.textContent)
                        .toLocaleLowerCase() === 'beranda'
                );
                if (!candidates.length) {
                    candidates = [...document.querySelectorAll(
                        'body *'
                    )].filter(element =>
                        visible(element) &&
                        normalize(element.innerText || element.textContent)
                            .toLocaleLowerCase() === 'beranda' &&
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent)
                                .toLocaleLowerCase() === 'beranda'
                        )
                    );
                }
                candidates.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                return candidates[0] || false;
                """
            ),
            "Breadcrumb Beranda tidak ditemukan pada halaman detail Monitoring.",
        )
        self._click_centered(home_breadcrumb)
        self.wait_for_dashboard()

        if (
            self._listing_window
            and self._listing_window != self._detail_window
            and self._listing_window in self.driver.window_handles
        ):
            current_window = self.driver.current_window_handle
            self.driver.switch_to.window(self._listing_window)
            self.driver.close()
            self.driver.switch_to.window(current_window)

        self._listing_window = None
        self._detail_window = None
        self._listing_url = None
        return self

    def _find_monitoring_section(self):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const text = arguments[0];
                const headings = [...document.querySelectorAll(
                    'h1, h2, h3, h4, h5, h6, [role="heading"]'
                )].filter(element =>
                    visible(element) &&
                    normalize(element.innerText || element.textContent) === text
                );
                const matches = headings.length ? headings :
                    [...document.querySelectorAll('body *')].filter(element =>
                        visible(element) &&
                        normalize(element.innerText || element.textContent) === text &&
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent) === text
                        )
                    );
                if (!matches.length) return false;
                const target = matches[0];
                target.scrollIntoView({block: 'center', inline: 'center'});
                return target;
                """,
                locators.MONITORING_SECTION_TEXT,
            ),
            "Menu Monitoring tidak ditemukan setelah login. Pastikan akun AO memiliki akses.",
        )

    def _find_see_all_for_section(self, section):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                let parent = arguments[0].parentElement;
                while (parent && parent !== document.body) {
                    const buttons = [...parent.querySelectorAll(
                        '[id="btn_see_all_feature"], button, [role="button"], a'
                    )].filter(element =>
                        visible(element) &&
                        (element.id === 'btn_see_all_feature' ||
                         normalize(element.innerText || element.textContent)
                            .toLocaleLowerCase() === 'lihat semua')
                    );
                    if (buttons.length === 1) return buttons[0];
                    parent = parent.parentElement;
                }
                return false;
                """,
                section,
            ),
            "Tombol Lihat Semua pada kartu Monitoring tidak ditemukan.",
        )

    def _wait_for_exact_text(self, text):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const dialogs = [...document.querySelectorAll(
                    '[role="dialog"], dialog, [aria-modal="true"]'
                )].filter(visible);
                const scopes = dialogs.length ? dialogs : [document];
                for (const scope of scopes) {
                    const matches = [...scope.querySelectorAll('*')].filter(
                        element => visible(element) &&
                            normalize(element.innerText || element.textContent) === arguments[0]
                    );
                    const leaves = matches.filter(element =>
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent) === arguments[0]
                        )
                    );
                    if (leaves.length) return leaves[0];
                }
                return false;
                """,
                text,
            ),
            f"Teks '{text}' tidak ditemukan pada halaman.",
        )

    def _wait_for_credit_type_control(self):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const labels = [...document.querySelectorAll('label, span, div, p')].filter(
                    element => visible(element) &&
                        normalize(element.innerText || element.textContent) === arguments[0] &&
                        ![...element.children].some(child =>
                            normalize(child.innerText || child.textContent) === arguments[0]
                        )
                );
                for (const label of labels) {
                    if (label.htmlFor) {
                        const associated = document.getElementById(label.htmlFor);
                        if (associated && visible(associated)) return associated;
                    }
                    let parent = label.parentElement;
                    while (parent && parent !== document.body) {
                        const controls = [...parent.querySelectorAll(
                            'select, [role="combobox"], input, button'
                        )].filter(visible);
                        if (controls.length === 1) return controls[0];
                        parent = parent.parentElement;
                    }
                }
                return false;
                """,
                locators.CREDIT_TYPE_LABEL,
            ),
            "Dropdown Jenis Kredit tidak ditemukan pada halaman Monitoring Program UMK.",
        )

    def _wait_for_first_detail_button(self):
        return self.wait.until(
            lambda driver: self._first_detail_button_or_none() or False,
            "Tidak ada data hasil pencarian dengan tombol Lihat Detail.",
        )

    def _first_detail_button_or_none(self):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const buttons = [...document.querySelectorAll(
                'button, [role="button"], a'
            )].filter(element =>
                visible(element) &&
                normalize(element.innerText || element.textContent)
                    .toLocaleLowerCase() === arguments[0].toLocaleLowerCase()
            );
            return buttons[0] || null;
            """,
            locators.DETAIL_BUTTON_TEXT,
        )

    def _result_signature(self, detail_button):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const button = arguments[0];
            const row = button.closest('tr, [role="row"], [data-row-key]');
            if (row) return normalize(row.innerText || row.textContent);
            let parent = button.parentElement;
            let signature = '';
            for (let depth = 0; parent && depth < 5; depth += 1) {
                const text = normalize(parent.innerText || parent.textContent);
                if (text.length > signature.length) signature = text;
                if (text.length > normalize(button.innerText || button.textContent).length + 8) {
                    return text;
                }
                parent = parent.parentElement;
            }
            return signature;
            """,
            detail_button,
        )

    def _wait_for_search_results(self, previous_button, previous_signature):
        def results_updated(driver):
            current_button = self._first_detail_button_or_none()
            if not current_button:
                return False
            if previous_button is None:
                return current_button
            try:
                if not previous_button.is_displayed():
                    return current_button
            except StaleElementReferenceException:
                return current_button
            return (
                current_button
                if self._result_signature(current_button) != previous_signature
                else False
            )

        return self.wait.until(
            results_updated,
            "Data hasil pencarian tidak diperbarui setelah tombol Cari diklik.",
        )

    def _detail_content_is_visible(self):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const headings = [...document.querySelectorAll(
                'h1, h2, h3, [role="heading"]'
            )].filter(element =>
                visible(element) &&
                normalize(element.innerText || element.textContent)
                    .toLocaleLowerCase().includes('detail')
            );
            return headings.length > 0 ||
                [...document.querySelectorAll('[role="dialog"], dialog')].some(visible);
            """
        )

    def _detail_page_replaced(self, previous_text):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const hasSearchForm = [...document.querySelectorAll('label, span, div, p')]
                .some(element =>
                    visible(element) &&
                    normalize(element.innerText || element.textContent) === arguments[1]
                );
            const hasDetailAction = [...document.querySelectorAll(
                'button, [role="button"], a'
            )].some(element =>
                visible(element) &&
                normalize(element.innerText || element.textContent)
                    .toLocaleLowerCase() === arguments[2].toLocaleLowerCase()
            );
            const currentText = document.body.innerText || document.body.textContent || '';
            return !hasSearchForm && !hasDetailAction &&
                normalize(currentText) !== normalize(arguments[0]);
            """,
            previous_text,
            locators.CREDIT_TYPE_LABEL,
            locators.DETAIL_BUTTON_TEXT,
        )

    def _click_centered(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
        self.driver.execute_script("arguments[0].click();", element)
