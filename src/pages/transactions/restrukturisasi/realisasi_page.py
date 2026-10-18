import time
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select, WebDriverWait

from src.pages.transactions.restrukturisasi import realisasi_locators as locators


FACILITY_FILTER_LABEL = "Pilih fasilitas restrukturisasi"
ALL_FACILITIES_LABEL = "Semua"
REALISASI_PDF = (
    Path(__file__).resolve().parents[4]
    / "Upload_Realisasi"
    / "Pdf test file.pdf"
)
UPLOAD_FIELDS = (
    "Berkas Surat Perjanjian Kredit",
    "Berkas Kartu Angsuran",
)


class RealisasiPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            30,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def filter_all_facilities(self):
        native_select = self._find_facility_select()
        if native_select:
            select = Select(native_select)
            option = next(
                (
                    option
                    for option in select.options
                    if self._normalize(option.text).casefold()
                    == ALL_FACILITIES_LABEL.casefold()
                ),
                None,
            )
            if option is None:
                raise RuntimeError(
                    "Opsi Semua tidak ditemukan pada dropdown Fasilitas Restrukturisasi."
                )
            select.select_by_visible_text(option.text)
            self.wait.until(
                lambda driver: self._native_facility_is_all_selected(
                    driver, native_select
                ),
                "Dropdown Fasilitas Restrukturisasi belum memilih opsi Semua.",
            )
        else:
            self._open_custom_facility_dropdown()
            option = self._select_all_facilities_option()
            option.click()
            self.wait.until(
                lambda driver: self._custom_facility_is_all_selected(driver),
                "Dropdown Fasilitas Restrukturisasi belum memilih opsi Semua.",
            )

        time.sleep(3)
        self._click_button("Cari")
        self._wait_for_first_process_button()

    def open_first_record(self):
        process_button = self._wait_for_first_process_button()
        time.sleep(3)
        self._click(process_button)
        self.wait.until(
            lambda driver: self._find_upload_fields(driver),
            "Form realisasi tidak menampilkan Berkas Surat Perjanjian Kredit "
            "dan Berkas Kartu Angsuran.",
        )
        time.sleep(5)

    def upload_agreement_files(self):
        if not REALISASI_PDF.is_file():
            raise FileNotFoundError(
                f"File PDF untuk realisasi tidak ditemukan: {REALISASI_PDF}"
            )
        if REALISASI_PDF.suffix.casefold() != ".pdf":
            raise ValueError(f"File realisasi harus PDF: {REALISASI_PDF}")

        for field_label in UPLOAD_FIELDS:
            file_input = self.wait.until(
                lambda driver: self._find_file_input(driver, field_label),
                f"Input upload {field_label!r} tidak ditemukan.",
            )
            file_input.send_keys(str(REALISASI_PDF))
            self.wait.until(
                lambda driver: self._file_is_selected(driver, file_input),
                f"File PDF tidak terpasang pada {field_label}.",
            )

        time.sleep(3)
        self._click_button("Simpan")
        self._click_button("Ya, Realisasikan")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Ya, Realisasikan"
            ),
            "Modal konfirmasi Ya, Realisasikan tidak tertutup.",
        )
        self._click_button("Kembali ke Daftar")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Kembali ke Daftar"
            ),
            "Halaman daftar realisasi tidak terbuka setelah kembali.",
        )
        time.sleep(5)

    def _find_facility_select(self):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const selects = [...document.querySelectorAll('select')];
            for (const select of selects) {
                if (!visible(select)) continue;
                const context = [
                    ...Array.from(select.labels || []).map(label => label.innerText || ''),
                    select.getAttribute('aria-label') || '',
                    select.parentElement?.innerText || '',
                    select.parentElement?.parentElement?.innerText || '',
                    select.parentElement?.parentElement?.parentElement?.innerText || '',
                ].map(normalize).join(' ').toLocaleLowerCase();
                if (context.includes(arguments[0].toLocaleLowerCase())) return select;
            }
            return false;
            """,
            FACILITY_FILTER_LABEL,
        )

    @staticmethod
    def _native_facility_is_all_selected(driver, select_element):
        return driver.execute_script(
            """
            const selected = arguments[0].selectedOptions[0];
            return selected &&
                selected.textContent.trim().toLocaleLowerCase() ===
                    arguments[1].toLocaleLowerCase();
            """,
            select_element,
            ALL_FACILITIES_LABEL,
        )

    def _custom_facility_is_all_selected(self, driver):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const expected = arguments[0].toLocaleLowerCase();
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            return [...document.querySelectorAll('body *')].some(element =>
                visible(element) &&
                normalize(
                    element.value ||
                    element.innerText ||
                    element.textContent ||
                    element.getAttribute('aria-label') ||
                    ''
                ).toLocaleLowerCase() === expected &&
                ![...element.children].some(child =>
                    normalize(child.innerText || child.textContent || '')
                        .toLocaleLowerCase() === expected
                )
            );
            """,
            ALL_FACILITIES_LABEL,
        )

    def _open_custom_facility_dropdown(self):
        self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const expected = arguments[0].toLocaleLowerCase();
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const controls = [...document.querySelectorAll('body *')].filter(element =>
                    visible(element) &&
                    normalize(
                        element.value ||
                        element.innerText ||
                        element.textContent ||
                        element.getAttribute('aria-label') ||
                        element.getAttribute('placeholder') ||
                        ''
                    ).toLocaleLowerCase() === expected
                );
                controls.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                const target = controls[0];
                if (!target) return false;
                target.click();
                return true;
                """,
                FACILITY_FILTER_LABEL,
            ),
            "Dropdown Fasilitas Restrukturisasi tidak dapat dibuka.",
        )

    def _select_all_facilities_option(self):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const expected = arguments[0].toLocaleLowerCase();
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const options = [...document.querySelectorAll(
                    'body *'
                )].filter(element =>
                    visible(element) &&
                    normalize(
                        element.innerText || element.textContent || element.label || ''
                    ).toLocaleLowerCase() === expected
                    && ![...element.children].some(child =>
                        normalize(
                            child.innerText || child.textContent || child.label || ''
                        ).toLocaleLowerCase() === expected
                    )
                );
                options.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height -
                        rightRect.width * rightRect.height;
                });
                const target = options[0];
                return target || false;
                """,
                ALL_FACILITIES_LABEL,
            ),
            "Opsi Semua tidak ditemukan pada dropdown Fasilitas Restrukturisasi.",
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
    def _find_upload_fields(driver):
        return driver.execute_script(
            """
            const fields = [...document.querySelectorAll('input[type="file"]')];
            return fields.length >= arguments[0] ? fields : false;
            """,
            len(UPLOAD_FIELDS),
        )

    @staticmethod
    def _find_file_input(driver, field_label):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ')
                .toLocaleLowerCase();
            const expected = normalize(arguments[0]);
            const inputs = [...document.querySelectorAll('input[type="file"]')];
            const matches = [];
            for (const input of inputs) {
                const descriptions = [
                    ...Array.from(input.labels || []).map(label => label.innerText || ''),
                    input.getAttribute('aria-label') || '',
                    input.getAttribute('name') || '',
                    input.id || '',
                    input.parentElement?.innerText || '',
                    input.parentElement?.parentElement?.innerText || '',
                    input.parentElement?.parentElement?.parentElement?.innerText || '',
                ];
                const text = normalize(descriptions.join(' '));
                if (text.includes(expected)) {
                    matches.push({input, score: text.length});
                }
            }
            matches.sort((left, right) => left.score - right.score);
            return matches[0]?.input || false;
            """,
            field_label,
        )

    @staticmethod
    def _file_is_selected(driver, file_input):
        return driver.execute_script(
            """
            return arguments[0].files.length > 0 &&
                arguments[0].files[0].name === arguments[1];
            """,
            file_input,
            REALISASI_PDF.name,
        )

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
