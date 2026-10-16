import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.transactions.restrukturisasi import survey_locators as locators


SURVEY_NOTE = "Ya saya setujui proses survey ini"


class SurveyPage:
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
            for row in driver.find_elements(*locators.SURVEY_ROWS):
                if not row.is_displayed():
                    continue
                for button in row.find_elements(*locators.ACTION_BUTTONS):
                    if (
                        button.is_displayed()
                        and button.is_enabled()
                        and self._button_label(button).casefold() == "proses survey"
                    ):
                        return button
            return False

        process_button = self.wait.until(
            find_first_process_button,
            "Tombol Proses Survey tidak ditemukan pada record pertama.",
        )
        self._click(process_button)
        self._wait_for_button("Selanjutnya")

    def complete_first_survey(self):
        self._click_next()
        self._save_and_continue()
        self._save_and_continue()
        self._save_and_continue()
        self._click_next()
        self._save_and_continue()
        self._save_and_continue()
        self._save_current_page()
        self._click_button("Selesaikan Survey")
        self._fill_survey_note_and_save()
        self._click_button("Kembali ke Daftar")
        self._wait_for_button("Proses Survey")

    def _save_and_continue(self):
        self._save_current_page()
        self._click_next()

    def _click_next(self):
        self._click_button("Selanjutnya")
        time.sleep(5)

    def _save_current_page(self):
        self._click_button("Simpan")
        self._click_button("Ya, Simpan Data")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Ya, Simpan Data"
            ),
            "Modal Ya, Simpan Data tidak tertutup setelah konfirmasi.",
        )
        self.wait.until(
            self._save_success_is_visible,
            "Notifikasi 'Data berhasil disimpan' tidak muncul setelah menyimpan section.",
        )

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

    def _fill_survey_note_and_save(self):
        field_and_button = self.wait.until(
            self._find_survey_note_and_save_button,
            "Field Catatan dan tombol Simpan pada konfirmasi survey tidak ditemukan.",
        )
        note_field, save_button = field_and_button
        note_field.clear()
        note_field.send_keys(SURVEY_NOTE)
        self._click(save_button)

    @staticmethod
    def _button_label(button):
        label = (
            button.text
            or button.get_attribute("value")
            or button.get_attribute("aria-label")
            or ""
        )
        return " ".join(label.split())

    def _wait_for_button(self, label):
        return self.wait.until(
            lambda driver: self._find_visible_button_in(driver, label),
            f"Tombol {label!r} tidak ditemukan.",
        )

    def _click_button(self, label):
        button = self.wait.until(
            lambda driver: self._find_enabled_button(driver, label),
            f"Tombol {label!r} tidak ditemukan atau tidak aktif.",
        )
        self._click(button)

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

    def _find_survey_note_and_save_button(self, driver):
        return driver.execute_script(
            """
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const fields = [...document.querySelectorAll('textarea, input[type="text"]')]
                .filter(visible);
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
                if (!labelText.includes('catatan')) continue;

                let parent = field.parentElement;
                while (parent && parent !== document.body) {
                    const saveButton = [...parent.querySelectorAll(
                        'button, [role="button"], input[type="button"], input[type="submit"]'
                    )].find(button =>
                        visible(button) &&
                        !button.disabled &&
                        normalize(button.innerText || button.value || '')
                            .toLocaleLowerCase() === 'simpan'
                    );
                    if (saveButton) return [field, saveButton];
                    parent = parent.parentElement;
                }
            }
            return false;
            """
        )

    def _click(self, element):
        self.driver.execute_script(
            """
            arguments[0].scrollIntoView({block: 'center', inline: 'center'});
            arguments[0].click();
            """,
            element,
        )
