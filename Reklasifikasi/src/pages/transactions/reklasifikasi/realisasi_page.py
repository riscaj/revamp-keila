import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select, WebDriverWait

from src.pages.transactions.reklasifikasi import realisasi_locators as locators


APPLICATION_TYPE_LABEL = "Jenis Pengajuan"
PROBLEM_CREDIT_APPLICATION = "Kredit Bermasalah Khusus"


class RealisasiPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            30,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def filter_problem_credit_application(self):
        application_type = self.wait.until(
            lambda driver: self._find_application_type_control(driver),
            "Dropdown Jenis Pengajuan tidak ditemukan pada halaman realisasi.",
        )
        if application_type.tag_name.casefold() == "select":
            select = Select(application_type)
            option = next(
                (
                    option
                    for option in select.options
                    if self._normalize(option.text).casefold()
                    == PROBLEM_CREDIT_APPLICATION.casefold()
                ),
                None,
            )
            if option is None:
                raise RuntimeError(
                    "Opsi Kredit Bermasalah Khusus tidak ditemukan pada dropdown "
                    "Jenis Pengajuan."
                )
            select.select_by_visible_text(option.text)
            self.wait.until(
                lambda driver: self._native_application_type_is_selected(
                    driver, application_type
                ),
                "Jenis Pengajuan belum memilih Kredit Bermasalah Khusus.",
            )
        else:
            self.wait.until(
                lambda driver: self._open_custom_application_type_dropdown(driver),
                "Dropdown Jenis Pengajuan tidak dapat dibuka.",
            )
            option = self.wait.until(
                lambda driver: self._find_application_type_option(driver),
                "Opsi Kredit Bermasalah Khusus tidak ditemukan.",
            )
            self._click(option)
            self.wait.until(
                lambda driver: self._custom_application_type_is_selected(
                    driver, application_type
                ),
                "Jenis Pengajuan belum memilih Kredit Bermasalah Khusus.",
            )

        time.sleep(3)
        self._click_button("Cari")
        self._wait_for_first_process_button()

    def open_first_record(self):
        process_button = self._wait_for_first_process_button()
        time.sleep(3)
        self._click(process_button)
        self.wait.until(
            lambda driver: self._find_enabled_button(driver, "Simpan"),
            "Tombol Simpan tidak ditemukan setelah membuka record realisasi.",
        )
        time.sleep(5)

    def complete_first_record(self):
        self._click_button("Simpan")
        self._click_button("Ya, Simpan")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Ya, Simpan"
            ),
            "Modal konfirmasi Ya, Simpan tidak tertutup.",
        )
        self._click_button("Kembali ke Daftar")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Kembali ke Daftar"
            ),
            "Halaman daftar realisasi tidak terbuka setelah kembali.",
        )
        time.sleep(3)

    def _find_application_type_control(self, driver):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const expected = normalize(arguments[0]).toLocaleLowerCase();
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const labels = [...document.querySelectorAll('label, span, div, p')]
                .filter(element => visible(element) &&
                    normalize(element.innerText || element.textContent)
                        .toLocaleLowerCase() === expected)
                .sort((left, right) =>
                    left.querySelectorAll('*').length - right.querySelectorAll('*').length
                );
            const selector = [
                'select', '[role="combobox"]', '[aria-haspopup="listbox"]',
                'input:not([type="hidden"])', 'button', '[class*="select"]'
            ].join(',');
            for (const label of labels) {
                let container = label;
                for (let depth = 0; depth < 6 && container; depth += 1) {
                    const controls = [...container.querySelectorAll(selector)]
                        .filter(control => control !== label && visible(control));
                    if (controls.length === 1) return controls[0];
                    if (controls.length > 1) {
                        const dropdown = controls.find(control =>
                            control.matches(
                                'select, [role="combobox"], [aria-haspopup="listbox"]'
                            ) ||
                            control.className?.toString().toLocaleLowerCase()
                                .includes('select')
                        );
                        if (dropdown) return dropdown;
                    }
                    container = container.parentElement;
                }
            }
            return false;
            """,
            APPLICATION_TYPE_LABEL,
        )

    @staticmethod
    def _native_application_type_is_selected(driver, select_element):
        return driver.execute_script(
            """
            return arguments[0].selectedOptions.length === 1 &&
                arguments[0].selectedOptions[0].text.trim() === arguments[1];
            """,
            select_element,
            PROBLEM_CREDIT_APPLICATION,
        )

    @staticmethod
    def _custom_application_type_is_selected(driver, control):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[1]);
            const element = arguments[0];
            if (element.matches('input, textarea')) return normalize(element.value) === expected;
            return [
                element.innerText,
                element.textContent,
                element.getAttribute('aria-valuetext'),
                element.getAttribute('aria-label'),
                element.getAttribute('title')
            ].some(value => normalize(value).includes(expected));
            """,
            control,
            PROBLEM_CREDIT_APPLICATION,
        )

    def _open_custom_application_type_dropdown(self, driver):
        control = self._find_application_type_control(driver)
        if not control:
            return False
        self._click(control)
        return True

    @staticmethod
    def _find_application_type_option(driver):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const options = [...document.querySelectorAll(
                '[role="option"], [role="menuitem"], option, li, button, label, div, span'
            )].filter(element => visible(element) &&
                normalize(element.innerText || element.textContent) === expected)
                .sort((left, right) =>
                    left.querySelectorAll('*').length - right.querySelectorAll('*').length
                );
            return options[0] || false;
            """,
            PROBLEM_CREDIT_APPLICATION,
        )

    def _click_button(self, label):
        button = self.wait.until(
            lambda driver: self._find_enabled_button(driver, label),
            f"Tombol {label!r} tidak ditemukan atau tidak aktif.",
        )
        self._click(button)

    def _wait_for_first_process_button(self):
        return self.wait.until(
            lambda driver: self._find_first_process_button(driver),
            "Tombol Proses tidak ditemukan pada data realisasi pertama.",
        )

    def _find_first_process_button(self, driver):
        for row in driver.find_elements(*locators.REALISASI_ROWS):
            if not row.is_displayed():
                continue
            for button in row.find_elements(*locators.ACTION_BUTTONS):
                if (
                    button.is_displayed()
                    and button.is_enabled()
                    and self._button_label(button).casefold().startswith("proses")
                ):
                    return button
        return False

    def _find_enabled_button(self, driver, label):
        button = self._find_visible_button_in(driver, label)
        if button and button.is_enabled():
            return button
        return False

    def _find_visible_button_in(self, driver, label):
        for button in driver.find_elements(*locators.ACTION_BUTTONS):
            if (
                button.is_displayed()
                and self._button_label(button).casefold() == label.casefold()
            ):
                return button
        return False

    @staticmethod
    def _normalize(value):
        return " ".join(value.split())

    @staticmethod
    def _button_label(button):
        label = (
            button.text
            or button.get_attribute("value")
            or button.get_attribute("aria-label")
            or ""
        )
        return " ".join(label.split())

    def _click(self, element):
        self.driver.execute_script(
            """
            arguments[0].scrollIntoView({block: 'center', inline: 'center'});
            arguments[0].click();
            """,
            element,
        )
