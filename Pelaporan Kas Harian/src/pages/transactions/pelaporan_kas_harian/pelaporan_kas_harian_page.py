from pathlib import Path
from time import sleep

from selenium.common.exceptions import (
    NoAlertPresentException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.transactions.pelaporan_kas_harian import (
    pelaporan_kas_harian_locators as locators,
)


class PelaporanKasHarianPage:
    login_url = locators.LOGIN_URL
    ACTION_PAUSE_SECONDS = 1
    SALDO_CMS_NOMINAL = "4.950.001"
    CMS_BANK_UPLOAD_DIRECTORY = (
        Path(__file__).resolve().parents[4] / "Upload_CMS_Bank"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            45,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def fill_login(self, username, password):
        username_input = self.wait.until(
            EC.visibility_of_element_located(locators.USERNAME_LOCATOR)
        )
        sleep(self.ACTION_PAUSE_SECONDS)
        password_input = self.wait.until(
            EC.visibility_of_element_located(locators.PASSWORD_LOCATOR)
        )
        sleep(self.ACTION_PAUSE_SECONDS)
        submit_button = self.wait.until(
            EC.element_to_be_clickable(locators.SUBMIT_LOCATOR)
        )
        username_input.clear()
        username_input.send_keys(username)
        sleep(self.ACTION_PAUSE_SECONDS)
        password_input.clear()
        password_input.send_keys(password)
        self._click_centered(submit_button)

    def wait_for_dashboard(self):
        self.wait.until(
            lambda driver: self._scroll_to_program_umk(),
            "Bagian Program UMK tidak ditemukan setelah login.",
        )

    def open_report_menu(self):
        self.wait.until(
            lambda _driver: self._scroll_to_program_umk(),
            "Bagian Program UMK tidak ditemukan setelah login.",
        )
        see_all_button = self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const headings = [...document.querySelectorAll('span')]
                    .filter(element =>
                        visible(element) &&
                        normalize(element.textContent) === arguments[0]
                    );
                for (const heading of headings) {
                    let parent = heading.parentElement;
                    while (parent && parent !== document.body) {
                        const buttons = [...parent.querySelectorAll(
                            `[id="${arguments[1]}"]`
                        )].filter(visible);
                        if (buttons.length === 1) return buttons[0];
                        parent = parent.parentElement;
                    }
                }
                return false;
                """,
                locators.PROGRAM_UMK_TEXT,
                locators.FEATURE_LIST_BUTTON_ID,
            ),
            "Tombol Lihat Semua pada bagian Program UMK tidak ditemukan.",
        )
        self._click_centered(see_all_button)

        dialog = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, locators.FEATURE_DIALOG_ID)
            )
        )
        menu_item = self._find_exact_visible_text(
            locators.REPORT_MENU_TEXT,
            scope=dialog,
        )
        self._click_centered(menu_item)
        self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                return [...document.querySelectorAll('body *')].some(element =>
                    visible(element) &&
                    normalize(element.textContent) === arguments[0]
                );
                """,
                locators.REPORT_PAGE_TITLE,
            ),
            "Halaman Pelaporan Harian Kas Dan Bank PUMK tidak terbuka.",
        )
        self.wait.until(
            EC.visibility_of_element_located(locators.REPORT_TABLE_LOCATOR),
            "Tabel Pelaporan Harian Kas Dan Bank PUMK tidak ditemukan.",
        )

    def process_pending_or_add_report(self):
        for attempt in range(3):
            try:
                rows = self._visible_report_rows()
                if not rows:
                    raise AssertionError(
                        "Tabel pelaporan tidak memiliki baris data untuk diperiksa."
                    )

                row_statuses = [
                    self._normalized_text(row.text)
                    for row in rows
                ]
                pending_rows = [
                    row
                    for row, status in zip(rows, row_statuses)
                    if "belum dilaporkan" in status
                ]
                repair_rows = [
                    row
                    for row, status in zip(rows, row_statuses)
                    if "perlu perbaikan" in status
                ]
                all_approved = all(
                    "disetujui" in status for status in row_statuses
                )
                if pending_rows:
                    row_to_process = pending_rows[0]
                    action = "process"
                elif repair_rows:
                    row_to_process = repair_rows[0]
                    action = "process_repair"
                elif all_approved:
                    action = "add_report"
                else:
                    approved_count = sum(
                        "disetujui" in status for status in row_statuses
                    )
                    raise AssertionError(
                        "Tidak ditemukan data berstatus Belum Dilaporkan, "
                        "Perlu Perbaikan, atau seluruh data Disetujui. "
                        f"Status terbaca: {len(pending_rows)} belum dilaporkan, "
                        f"{len(repair_rows)} perlu perbaikan, "
                        f"{approved_count} disetujui, "
                        f"{len(rows) - len(pending_rows) - len(repair_rows) - approved_count} "
                        "status lain."
                    )
                break
            except StaleElementReferenceException as error:
                if attempt == 2:
                    raise AssertionError(
                        "Tabel laporan terus diperbarui saat status dibaca; "
                        "gagal mendapatkan data yang stabil setelah 3 percobaan."
                    ) from error
                sleep(0.5)

        if action in {"process", "process_repair"}:
            self._click_and_follow_window_change(
                self._find_row_action(row_to_process, "proses"),
                "Proses",
            )
            if action == "process_repair":
                self._click_centered(
                    self._find_exact_visible_text("Selanjutnya")
                )
                self._calculate_cash_denominations()
                return action

            self._complete_cash_denominations()
            return action

        self._click_and_follow_window_change(
            self._find_exact_visible_text("Tambah Laporan"),
            "Tambah Laporan",
        )
        self._complete_cash_denominations()
        return "add_report"

    def _click_and_follow_window_change(self, element, action_name):
        try:
            previous_handles = set(self.driver.window_handles)
        except NoSuchWindowException as error:
            raise NoSuchWindowException(
                f"Jendela Chrome sudah tertutup sebelum tombol "
                f"'{action_name}' diklik."
            ) from error
        if not previous_handles:
            raise NoSuchWindowException(
                f"Tidak ada jendela Chrome yang terbuka saat tombol "
                f"'{action_name}' akan diklik."
            )

        self._click_centered(element)

        def switch_to_available_window(driver):
            try:
                handles = driver.window_handles
            except NoSuchWindowException:
                return False
            if not handles:
                return False

            new_handles = [
                handle for handle in handles if handle not in previous_handles
            ]
            if new_handles:
                try:
                    driver.switch_to.window(new_handles[-1])
                except NoSuchWindowException:
                    return False
                return True

            try:
                current_handle = driver.current_window_handle
            except NoSuchWindowException:
                current_handle = None
            if current_handle not in handles:
                try:
                    driver.switch_to.window(handles[-1])
                except NoSuchWindowException:
                    return False
            return True

        try:
            WebDriverWait(
                self.driver,
                5,
                poll_frequency=0.25,
            ).until(
                switch_to_available_window,
                f"Jendela Chrome tidak tersedia setelah tombol "
                f"'{action_name}' diklik.",
            )
        except TimeoutException as error:
            raise NoSuchWindowException(
                f"Jendela Chrome tertutup setelah tombol '{action_name}' "
                "diklik; tidak ada jendela yang bisa dilanjutkan."
            ) from error

    def _complete_cash_denominations(self):
        self._fill_first_row_sheet_count()
        self._calculate_cash_denominations()

    def _calculate_cash_denominations(self):
        self._scroll_to_page_bottom()
        self._click_centered(self._find_exact_visible_text("Hitung"))
        self._click_centered(self._find_exact_visible_text("Selanjutnya"))

    def complete_bank_balance_report(self):
        upload_path = self._cms_bank_pdf_path()
        upload_input = self.wait.until(
            self._find_cms_bank_upload_input,
            "Input upload CMS Bank tidak ditemukan pada halaman Saldo Bank.",
        )
        sleep(self.ACTION_PAUSE_SECONDS)
        upload_input.send_keys(str(upload_path))
        self.wait.until(
            lambda driver: self._cms_bank_file_is_selected(
                driver,
                upload_path.name,
            ),
            f"File CMS Bank '{upload_path.name}' belum berhasil dipilih.",
        )

        saldo_input = self.wait.until(
            self._find_saldo_cms_input,
            "Field Saldo CMS tidak ditemukan pada halaman Saldo Bank.",
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            saldo_input,
        )
        sleep(self.ACTION_PAUSE_SECONDS)
        saldo_input.click()
        sleep(self.ACTION_PAUSE_SECONDS)
        saldo_input.clear()
        saldo_input.send_keys(self.SALDO_CMS_NOMINAL)
        saldo_input.send_keys(Keys.TAB)
        sleep(self.ACTION_PAUSE_SECONDS)
        self.wait.until(
            lambda _driver: saldo_input.get_property("value").strip()
            == self.SALDO_CMS_NOMINAL,
            "Field Saldo CMS tidak terisi "
            f"{self.SALDO_CMS_NOMINAL} setelah difokuskan, diketik, dan "
            "disimpan dengan berpindah fokus.",
        )

        self._scroll_to_page_bottom()
        self._click_centered(self._find_exact_visible_text("Hitung"))
        self._submit_bank_report()

    def complete_repair_bank_balance_report(self):
        self._submit_bank_report()

    def _submit_bank_report(self):
        self._click_centered(self._find_exact_visible_text("Kirim Laporan"))
        confirmation_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[normalize-space(.)="Ya, Lanjutkan"]',
                )
            ),
            "Tombol konfirmasi 'Ya, Lanjutkan' tidak muncul setelah "
            "mengeklik Kirim Laporan.",
        )
        self._click_centered(confirmation_button)
        self._acknowledge_understood_popup("setelah konfirmasi laporan")

    def _acknowledge_understood_popup(self, context):
        def find_popup(driver):
            try:
                return "alert", driver.switch_to.alert
            except NoAlertPresentException:
                pass

            element = driver.execute_script(
                """
                const expected = arguments[0];
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const interactive = [...document.querySelectorAll(
                    'button, [role="button"], input[type="button"], '
                    + 'input[type="submit"], a'
                )].find(element =>
                    visible(element) &&
                    normalize(
                        element.innerText || element.value || element.textContent
                    ) === expected &&
                    !element.disabled
                );
                if (interactive) return interactive;

                const matches = [...document.querySelectorAll('span, div')]
                    .filter(element =>
                        visible(element) &&
                        normalize(element.innerText || element.textContent) === expected
                    );
                for (const match of matches) {
                    let candidate = match;
                    while (candidate && candidate !== document.body) {
                        if (
                            candidate.matches(
                                'button, [role="button"], input[type="button"], '
                                + 'input[type="submit"], a'
                            ) &&
                            !candidate.disabled
                        ) {
                            return candidate;
                        }
                        candidate = candidate.parentElement;
                    }
                    return match;
                }
                return false;
                """,
                "Mengerti",
            )
            if element and element.is_displayed() and element.is_enabled():
                return "element", element
            return False

        popup_type, popup = self.wait.until(
            find_popup,
            f"Tombol atau alert 'Mengerti' tidak ditemukan {context}.",
        )
        if popup_type == "alert":
            popup.accept()
        else:
            self._click_centered(popup)

        self.wait.until(
            lambda driver: self._understood_popup_is_closed(driver),
            f"Popup Mengerti belum tertutup {context}.",
        )
        sleep(5)

    @staticmethod
    def _understood_popup_is_closed(driver):
        try:
            driver.switch_to.alert
        except NoAlertPresentException:
            return not bool(
                driver.execute_script(
                    """
                    const normalize = value =>
                        (value || '').trim().replace(/\\s+/g, ' ');
                    const visible = element =>
                        element.getClientRects().length > 0 &&
                        getComputedStyle(element).visibility !== 'hidden' &&
                        getComputedStyle(element).display !== 'none';
                    return [...document.querySelectorAll(
                        'button, [role="button"], input[type="button"], '
                        + 'input[type="submit"], a, span, div'
                    )].some(element =>
                        visible(element) &&
                        normalize(
                            element.innerText ||
                            element.value ||
                            element.textContent
                        ) === 'Mengerti'
                    );
                    """
                )
            )
        return False

    def _visible_report_rows(self):
        self.wait.until(
            EC.visibility_of_element_located(locators.REPORT_TABLE_LOCATOR)
        )
        return self.wait.until(
            self._loaded_report_rows,
            "Tabel laporan belum selesai dimuat: kolom Status masih kosong.",
        )

    def _loaded_report_rows(self, driver):
        table = driver.find_element(*locators.REPORT_TABLE_LOCATOR)
        headers = table.find_elements(By.CSS_SELECTOR, "thead th")
        status_column = next(
            (
                index
                for index, header in enumerate(headers)
                if self._normalized_text(header.text) == "status"
            ),
            None,
        )
        if status_column is None:
            return False

        rows = [
            row
            for row in driver.find_elements(*locators.REPORT_ROWS_LOCATOR)
            if row.is_displayed()
        ]
        if not rows:
            return False

        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if (
                status_column >= len(cells)
                or not self._normalized_text(cells[status_column].text)
            ):
                return False
        return rows

    def _find_row_action(self, row, action_text):
        for element in row.find_elements(
            By.CSS_SELECTOR,
            'button, [role="button"], input[type="button"], input[type="submit"]',
        ):
            text = self._normalized_text(
                element.text
                or element.get_attribute("aria-label")
                or element.get_attribute("value")
                or element.get_attribute("title")
                or ""
            )
            if element.is_displayed() and element.is_enabled() and text == action_text:
                return element
        raise AssertionError(
            "Tombol Proses tidak ditemukan pada baris laporan."
        )

    def _fill_first_row_sheet_count(self):
        sheet_input = self.wait.until(
            self._first_row_sheet_count_input,
            "Input Jumlah Lembar pada baris pertama tidak ditemukan.",
        )
        sleep(self.ACTION_PAUSE_SECONDS)
        try:
            sheet_input.clear()
            sheet_input.send_keys("0")
        except NoSuchWindowException as error:
            self._switch_to_open_window()
            sheet_input = self.wait.until(
                self._first_row_sheet_count_input,
                "Input Jumlah Lembar tidak ditemukan setelah berpindah "
                "ke jendela browser yang aktif.",
            )
            try:
                sheet_input.clear()
                sheet_input.send_keys("0")
            except NoSuchWindowException as retry_error:
                raise NoSuchWindowException(
                    "Jendela Chrome kembali tertutup saat mengisi Jumlah "
                    "Lembar; pengisian tidak dapat dilanjutkan."
                ) from retry_error
        sleep(self.ACTION_PAUSE_SECONDS)
        self.wait.until(
            lambda _driver: sheet_input.get_attribute("value") == "0",
            "Jumlah Lembar pada baris pertama tidak terisi 0.",
        )

    def _switch_to_open_window(self):
        def switch_to_available_window(driver):
            try:
                handles = driver.window_handles
            except NoSuchWindowException:
                return False
            for handle in reversed(handles):
                try:
                    driver.switch_to.window(handle)
                except NoSuchWindowException:
                    continue
                return True
            return False

        try:
            WebDriverWait(
                self.driver,
                5,
                poll_frequency=0.25,
            ).until(
                switch_to_available_window,
                "Tidak ada jendela Chrome yang dapat digunakan.",
            )
        except TimeoutException as error:
            raise NoSuchWindowException(
                "Jendela Chrome tertutup saat mengisi Jumlah Lembar dan "
                "tidak ada jendela lain yang dapat digunakan."
            ) from error

    def _first_row_sheet_count_input(self, driver):
        for table in driver.find_elements(By.CSS_SELECTOR, "table"):
            if not table.is_displayed():
                continue
            headers = table.find_elements(By.CSS_SELECTOR, "thead th")
            sheet_column = next(
                (
                    index
                    for index, header in enumerate(headers)
                    if "jumlah" in self._normalized_text(header.text)
                    and (
                        "lembar" in self._normalized_text(header.text)
                        or "keping" in self._normalized_text(header.text)
                    )
                ),
                None,
            )
            if sheet_column is not None:
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                if not rows:
                    continue
                cells = rows[0].find_elements(By.CSS_SELECTOR, "td")
                if sheet_column >= len(cells):
                    continue
                inputs = cells[sheet_column].find_elements(
                    By.CSS_SELECTOR,
                    'input:not([type="hidden"]), textarea',
                )
                if inputs and inputs[0].is_displayed() and inputs[0].is_enabled():
                    return inputs[0]

        return False

    def _cms_bank_pdf_path(self):
        if not self.CMS_BANK_UPLOAD_DIRECTORY.is_dir():
            raise FileNotFoundError(
                "Folder Upload_CMS_Bank tidak ditemukan: "
                f"{self.CMS_BANK_UPLOAD_DIRECTORY}"
            )

        pdf_files = sorted(
            path
            for path in self.CMS_BANK_UPLOAD_DIRECTORY.iterdir()
            if path.is_file() and path.suffix.casefold() == ".pdf"
        )
        if not pdf_files:
            raise FileNotFoundError(
                "Tidak ada file PDF untuk upload di folder "
                f"{self.CMS_BANK_UPLOAD_DIRECTORY}."
            )
        if len(pdf_files) > 1:
            raise RuntimeError(
                "Ditemukan lebih dari satu PDF di folder Upload_CMS_Bank; "
                "sisakan satu file yang akan digunakan."
            )
        return pdf_files[0]

    def _find_cms_bank_upload_input(self, driver):
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        pdf_inputs = [
            element
            for element in inputs
            if "pdf" in (element.get_attribute("accept") or "").casefold()
        ]
        candidates = pdf_inputs or inputs
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise AssertionError(
                "Ditemukan beberapa input file dan tidak dapat memastikan "
                "input untuk CMS Bank."
            )
        return False

    @staticmethod
    def _cms_bank_file_is_selected(driver, filename):
        return driver.execute_script(
            """
            const filename = arguments[0];
            const normalize = value => (value || '').trim().replace(/\\\\/g, '/');
            const fileInputs = [...document.querySelectorAll('input[type="file"]')];
            if (fileInputs.some(input => {
                const files = [...(input.files || [])];
                const inputValue = normalize(input.value).split('/').pop();
                return files.some(file => file.name === filename) ||
                    inputValue === filename;
            })) {
                return true;
            }

            for (const input of fileInputs) {
                let parent = input.parentElement;
                for (let depth = 0; parent && depth < 8; depth += 1) {
                    const style = getComputedStyle(parent);
                    const visible =
                        parent.getClientRects().length > 0 &&
                        style.visibility !== 'hidden' &&
                        style.display !== 'none';
                    if (
                        visible &&
                        normalize(parent.innerText).includes(filename)
                    ) {
                        return true;
                    }
                    parent = parent.parentElement;
                }
            }

            const visibleFilename = [...document.querySelectorAll(
                'label, [role="status"], [aria-live], span, p'
            )].some(element => {
                const style = getComputedStyle(element);
                return element.getClientRects().length > 0 &&
                    style.visibility !== 'hidden' &&
                    style.display !== 'none' &&
                    normalize(element.innerText || element.textContent)
                        .includes(filename);
            });
            const pageShowsFilename = normalize(
                document.body ? document.body.innerText : ''
            ).includes(filename);
            return visibleFilename || pageShowsFilename;
            """,
            filename,
        )

    def _find_saldo_cms_input(self, driver):
        return driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const visible = element =>
                element.getClientRects().length > 0 &&
                getComputedStyle(element).visibility !== 'hidden' &&
                getComputedStyle(element).display !== 'none';
            const nominalInputs = [...document.querySelectorAll(
                'input[placeholder], textarea[placeholder]'
            )].filter(element =>
                visible(element) &&
                normalize(element.getAttribute('placeholder'))
                    .toLocaleLowerCase().includes('masukkan nominal')
            );
            for (const input of nominalInputs) {
                let parent = input.parentElement;
                for (let depth = 0; parent && depth < 6; depth += 1) {
                    if (normalize(parent.innerText).toLocaleLowerCase()
                        .includes('saldo cms')) {
                        return input;
                    }
                    parent = parent.parentElement;
                }
            }
            if (nominalInputs.length === 1) return nominalInputs[0];

            const inputs = [...document.querySelectorAll(
                'input:not([type="hidden"]):not([type="file"]), textarea'
            )].filter(element => visible(element) && !element.disabled);
            for (const input of inputs) {
                let context = [
                    input.getAttribute('placeholder'),
                    input.getAttribute('aria-label'),
                    input.getAttribute('name'),
                    input.getAttribute('id'),
                    ...[...(input.labels || [])].map(label => label.innerText)
                ].join(' ');
                let parent = input.parentElement;
                for (let depth = 0; parent && depth < 3; depth += 1) {
                    context += ' ' + (parent.innerText || '');
                    parent = parent.parentElement;
                }
                const normalized = normalize(context).toLocaleLowerCase();
                if (normalized.includes('saldo') && normalized.includes('cms')) {
                    return input;
                }
            }
            return false;
            """
        )

    def _scroll_to_page_bottom(self):
        self.driver.execute_script(
            """
            const root = document.scrollingElement || document.documentElement;
            window.scrollTo({
                top: root.scrollHeight,
                behavior: 'smooth'
            });
            """
        )
        sleep(self.ACTION_PAUSE_SECONDS)

    def _find_exact_visible_text(self, text, scope=None):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const root = arguments[1] || document;
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const matches = [...root.querySelectorAll(
                    'a, button, [role="button"], input[type="button"], '
                    + 'input[type="submit"], span, div, li'
                )].filter(element =>
                    visible(element) &&
                    normalize(
                        element.innerText || element.value || element.textContent
                    ) === arguments[0] &&
                    ![...element.children].some(child =>
                        normalize(child.innerText || child.textContent) === arguments[0]
                    )
                );
                return matches[0] || false;
                """,
                text,
                scope,
            ),
            f"Elemen dengan teks '{text}' tidak ditemukan.",
        )

    def _click_centered(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
        sleep(self.ACTION_PAUSE_SECONDS)
        self.driver.execute_script("arguments[0].click();", element)
        sleep(self.ACTION_PAUSE_SECONDS)

    def _scroll_to_program_umk(self):
        return self.driver.execute_script(
            """
            const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
            const heading = [...document.querySelectorAll('span')]
                .find(element => normalize(element.textContent) === arguments[0]);
            if (heading) {
                heading.scrollIntoView({behavior: 'smooth', block: 'center'});
                return true;
            }

            const root = document.scrollingElement;
            const scrollables = [
                root,
                ...document.querySelectorAll('*')
            ].filter(element =>
                element &&
                element.scrollHeight > element.clientHeight + 1 &&
                getComputedStyle(element).overflowY !== 'hidden'
            );
            scrollables.sort(
                (left, right) =>
                    (right.scrollHeight - right.clientHeight) -
                    (left.scrollHeight - left.clientHeight)
            );
            const scroller = scrollables[0];
            if (scroller) {
                const step = Math.max(scroller.clientHeight * 0.75, 400);
                scroller.scrollTop = Math.min(
                    scroller.scrollTop + step,
                    scroller.scrollHeight
                );
            } else {
                window.scrollBy(0, Math.max(window.innerHeight * 0.75, 400));
            }
            return false;
            """,
            locators.PROGRAM_UMK_TEXT,
        )

    @staticmethod
    def _normalized_text(value):
        return " ".join(value.casefold().split())
