import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.transactions.restrukturisasi import rekomendasi_locators as locators


REVIEW_STATEMENT = "Saya telah memeriksa data ini."
DECISION_NOTE = "Survey telah disetujui pada proses approval"
REVIEW_SECTIONS = (
    "Data Mitra Binaan",
    "Data Penjamin",
    "Data Usaha",
    "Data Barang Titipan",
    "Data Keuangan",
    "Fasilitas kredit",
    "Assessment 5C",
)


class RekomendasiPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            30,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def open_first_record(self):
        def find_first_process_button(driver):
            for row in driver.find_elements(*locators.RECOMMENDATION_ROWS):
                if not row.is_displayed():
                    continue
                for button in row.find_elements(*locators.ACTION_BUTTONS):
                    if (
                        button.is_displayed()
                        and button.is_enabled()
                        and self._button_label(button)
                        .casefold()
                        .startswith("proses")
                    ):
                        return button
            return False

        process_button = self.wait.until(
            find_first_process_button,
            "Tombol Proses tidak ditemukan pada record rekomendasi pertama.",
        )
        self._click(process_button)
        self._wait_for_button("Selanjutnya")

    def complete_first_recommendation(self):
        self._click_button("Selanjutnya")
        for section in REVIEW_SECTIONS:
            self._review_section(section)
        time.sleep(5)
        self._select_approval()
        self._fill_decision_note()
        self.wait.until(
            lambda driver: self._decision_note_is_filled(driver),
            "Field Catatan belum terisi sebelum menyimpan keputusan.",
        )
        self._click_button("Simpan")
        self._click_button("Ya, Setujui")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(driver, "Ya, Setujui"),
            "Modal konfirmasi Ya, Setujui tidak tertutup.",
        )
        self._click_button("Kembali ke Daftar")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Kembali ke Daftar"
            ),
            "Halaman rekomendasi tidak terbuka setelah kembali ke daftar.",
        )
        time.sleep(5)

    def _review_section(self, section):
        time.sleep(5)
        self.wait.until(
            lambda driver: self._set_checkbox_for_statement(driver),
            f"Checkbox pernyataan {REVIEW_STATEMENT!r} tidak ditemukan pada "
            f"section {section}.",
        )
        self._click_button("Selanjutnya")

    def _set_checkbox_for_statement(self, driver):
        return driver.execute_script(
            """
            const expected = arguments[0].toLocaleLowerCase();
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const labels = [...document.querySelectorAll('label, [role="checkbox"]')]
                .filter(element =>
                    visible(element) &&
                    normalize(element.innerText || element.textContent || '')
                        .toLocaleLowerCase() === expected
                );
            for (const label of labels) {
                const checkbox = label.control ||
                    (label.htmlFor && document.getElementById(label.htmlFor)) ||
                    label.querySelector('input[type="checkbox"]');
                const target = checkbox || label;
                const checked = checkbox
                    ? checkbox.checked
                    : label.getAttribute('aria-checked') === 'true';
                if (!checked) target.click();
                return checkbox
                    ? checkbox.checked
                    : label.getAttribute('aria-checked') === 'true';
            }

            const checkboxes = [...document.querySelectorAll('input[type="checkbox"]')]
                .filter(visible);
            for (const checkbox of checkboxes) {
                const text = [
                    ...(checkbox.labels || []).map(label => label.innerText || ''),
                    checkbox.parentElement?.innerText || '',
                ].join(' ');
                if (normalize(text).toLocaleLowerCase() !== expected) continue;
                if (!checkbox.checked) checkbox.click();
                return checkbox.checked;
            }
            return false;
            """,
            REVIEW_STATEMENT,
        )

    def _select_approval(self):
        self.wait.until(
            lambda driver: self._select_approval_option(driver),
            "Radio button Setujui tidak ditemukan atau tidak dapat dipilih.",
        )

    def _select_approval_option(self, driver):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const expected = 'setujui';
            const radios = [...document.querySelectorAll(
                'input[type="radio"], [role="radio"]'
            )];
            for (const radio of radios) {
                const labels = Array.from(radio.labels || []);
                const labelText = [
                    ...labels.map(label => label.innerText || ''),
                    radio.getAttribute('aria-label') || '',
                    radio.getAttribute('value') || '',
                    radio.parentElement?.innerText || '',
                ].map(normalize);
                if (!labelText.some(text =>
                    text.toLocaleLowerCase() === expected
                )) {
                    continue;
                }
                if (radio.getAttribute('role') === 'radio') {
                    if (radio.getAttribute('aria-checked') !== 'true') radio.click();
                    return radio.getAttribute('aria-checked') === 'true';
                }
                const label = labels.find(label =>
                    normalize(label.innerText || label.textContent || '')
                        .toLocaleLowerCase() === expected
                );
                if (!radio.checked) (label || radio).click();
                return radio.checked;
            }

            const labels = [...document.querySelectorAll('label')]
                .filter(label =>
                    normalize(label.innerText || label.textContent || '')
                        .toLocaleLowerCase() === expected
                );
            for (const label of labels) {
                const radio = label.control ||
                    (label.htmlFor && document.getElementById(label.htmlFor)) ||
                    label.querySelector('input[type="radio"]');
                if (!radio) continue;
                if (!radio.checked) label.click();
                return radio.checked;
            }
            return false;
            """
        )

    def _fill_decision_note(self):
        field = self.wait.until(
            self._find_decision_note,
            "Field Catatan pada halaman keputusan tidak ditemukan.",
        )
        field.clear()
        field.send_keys(DECISION_NOTE)

    @classmethod
    def _decision_note_is_filled(cls, driver):
        field = cls._find_decision_note(driver)
        return field and field.get_property("value") == DECISION_NOTE

    @staticmethod
    def _find_decision_note(driver):
        return driver.execute_script(
            """
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const fields = [...document.querySelectorAll(
                'textarea, input[type="text"]'
            )].filter(visible);
            for (const field of fields) {
                const labelText = [
                    field.getAttribute('aria-label') || '',
                    field.getAttribute('placeholder') || '',
                    field.getAttribute('name') || '',
                    field.id || '',
                    ...[...(field.labels || [])].map(label => label.innerText || ''),
                    field.closest('label')?.innerText || '',
                    field.parentElement?.innerText || '',
                    field.parentElement?.previousElementSibling?.innerText || '',
                    field.getAttribute('aria-labelledby')
                        ?.split(/\\s+/)
                        .map(id => document.getElementById(id)?.innerText || '')
                        .join(' ') || '',
                ].join(' ').toLocaleLowerCase();
                if (labelText.includes('catatan')) return field;
            }
            return false;
            """
        )

    def _click_button(self, label):
        button = self.wait.until(
            lambda driver: self._find_enabled_button(driver, label),
            f"Tombol {label!r} tidak ditemukan atau tidak aktif.",
        )
        self._click(button)

    @staticmethod
    def _save_success_is_visible(driver):
        return driver.execute_script(
            """
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            return [...document.querySelectorAll('body *')].some(element =>
                visible(element) &&
                (element.innerText || element.textContent || '')
                    .replace(/\\s+/g, ' ')
                    .trim()
                    .toLocaleLowerCase()
                    .includes('data berhasil disimpan')
            );
            """
        )

    def _wait_for_button(self, label):
        return self.wait.until(
            lambda driver: self._find_visible_button_in(driver, label),
            f"Tombol {label!r} tidak ditemukan.",
        )

    def _find_visible_button_in(self, driver, label):
        for button in driver.find_elements(*locators.ACTION_BUTTONS):
            if (
                button.is_displayed()
                and self._button_label(button).casefold() == label.casefold()
            ):
                return button
        return False

    def _find_enabled_button(self, driver, label):
        button = self._find_visible_button_in(driver, label)
        if button and button.is_enabled():
            return button
        return False

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
